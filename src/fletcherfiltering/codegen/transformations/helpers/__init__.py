__all__ = ["FunctionResolver", "ArrowTypeResolver", "ArrowTestTypeResolver"]

import typed_ast.ast3 as ast
import horast.nodes as horast
from moz_sql_parser.ast_nodes import ASTNode

class ReferenceMetadata:
    def __init__(self, signal):
        self.signal = signal

    def __str__(self):
        return self.__class__.__name__ + '(' + (self.dict_as_parameters(self.__dict__) if self.__dict__ else '') + ')'

    def dict_as_parameters(self, dict):
        def render(item):
            if isinstance(item, str):
                return item.replace("\"", "\\\"")
            elif isinstance(item, ASTNode):
                return item
            elif isinstance(item, ast.AST):
                return ast.dump(item)
            else:
                return item
        dict = {k: v for k, v in dict.items() if v is not None and k != '_fields'}

        if len(dict) == 1:
            v = dict[next(iter(dict))]
            return "{1}{0}{1}".format(render(v), '"' if isinstance(v, str) else "")
        else:
            return ','.join(
                ["{0}={2}{1}{2}".format(k, render(v), '"' if isinstance(v, str) else "") for (k, v) in dict.items()])

    __repr__ = __str__

    def __key(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, ReferenceMetadata):
            # Don't recognise "other", so let *it* decide if we're equal
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__key())

def iter_fields(node):
    """
    Yield a tuple of ``(fieldname, value)`` for each field in ``node._fields``
    that is present on *node*.
    """
    for field in node._fields:
        try:
            yield field, getattr(node, field)
        except AttributeError:
            pass

def make_comment(comment, eol=False):
    comment = horast.Comment(value=ast.Str(comment), eol=eol, lineno=0, col_offset=0)
    return comment

def grouped(iterable, n):
    "s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ..."
    return zip(*[iter(iterable)]*n)
