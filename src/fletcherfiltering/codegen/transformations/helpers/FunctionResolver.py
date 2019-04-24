import pyarrow as pa
import collections

import typed_ast.ast3 as ast

from . import grouped
from ... import settings

FunctionMetadata = collections.namedtuple('FunctionMetadata', ['resolved_name', 'generator', 'id'])

PrePostAST = collections.namedtuple('FunctionAST', ['pre_ast', 'ast', 'post_ast', 'len_ast'])


import itertools

class FunctionResolver(object):

    def __init__(self):
        self.num_id = 0

    def get_next_id(self):
        val = self.num_id
        self.num_id += 1
        return val

    @staticmethod
    def make_method_name(funcname: str) -> str:
        return 'func_' + str(funcname).upper()

    def resolve(self, funcname: str, length_func: bool = False) -> FunctionMetadata:
        """Dispatch method"""
        method_name = self.make_method_name(funcname)
        # Get the method from 'self'. Default to a lambda.
        method = getattr(self, method_name, lambda x: self.unknown_type(x))
        # Call the method as we return it
        return method(length_func)

    def func_CONCAT(self, length_func: bool = False) -> FunctionMetadata:
        return FunctionMetadata('__sql_builtin_concat' + (settings.LENGHT_SUFFIX if length_func else ''), self.gen_CONCAT,
                                self.get_next_id())

    @staticmethod
    def gen_CONCAT(func_ast, func: FunctionMetadata) -> PrePostAST:
        assert (isinstance(func_ast, ast.Call))
        assert (isinstance(func, FunctionMetadata))

        assert (len(func_ast.args) % 2 == 0)

        buf_name = "buffer{}".format(func.id)
        offset_name = "buffer_offset{}".format(func.id)
        offset_ref_name = "&buffer_offset{}".format(func.id)

        extra_ast = [
            ast.AnnAssign(
            target=ast.Subscript(
                value=ast.Name(
                    id=buf_name,
                    ctx=ast.Store()
                ),
                slice=ast.Index(ast.Num(256)),
                ctx=ast.Store()
            ),
            annotation=ast.Name(
                id='char',
                ctx=ast.Load()),
            value=None,
            simple=1),
            ast.AnnAssign(
                target=ast.Name(
                        id=offset_name,
                        ctx=ast.Store()
                    ),
                annotation=ast.Name(
                    id='int',
                    ctx=ast.Load()),
                value=ast.Num(n=0),
                simple=1)
            ]


        buffer_ast = ast.Name(id=buf_name, ctx=ast.Load())
        offset_ast = ast.Name(id=offset_name, ctx=ast.Load())
        offset_value_ast = ast.Name(id=offset_ref_name, ctx=ast.Load())
        for arg, arg_len in grouped(func_ast.args,2):
            extra_ast.append(
                ast.Expr(
                    value=ast.Call(
                    func=func_ast.func,
                    args=[buffer_ast,offset_value_ast,arg,arg_len],
                    keywords=[])
                )
            )

        func_ast.args = [ast.Name(id=buf_name, ctx=ast.Load())] + func_ast.args

        value_ast = ast.Name(
                    id=buf_name,
                    ctx=ast.Load()
                )

        len_ast = offset_ast

        return PrePostAST(extra_ast, value_ast, None, len_ast)

    def unknown_type(self, length_func: bool = False):
        raise NotImplementedError(
            '{}{} cannot be processed'.format(length_func, ' \'s length function' if length_func else ''))
