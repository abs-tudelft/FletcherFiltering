import pyarrow as pa

import typed_ast.ast3 as ast

import typed_astunparse as astunparse

import moz_sql_parser as msp

import transpyle

import vhdre

STRING_LEN = 255

global_unique_counter = 0

source_header_header = """#include "hls_stream.h"
#include "fletcherfiltering.h" """

source_code_header = """#include "query.h" """


def getConcatFunction(func, params):
    global global_unique_counter
    global_unique_counter += 1
    buf_name = "buffer{}".format(global_unique_counter)
    function_ast = [
        ast.AnnAssign(
            target=ast.Name(
                id=buf_name,
                ctx=ast.Store()),
            annotation=ast.Name(
                id=out_col_reg[col_name]['type']['ctype'],
                ctx=ast.Load()),
            value=col['ast'],
            simple=1),

        ast.Call(
            func=ast.Name(
                id=func['name'],
                ctx=ast.Load()
            ),
            args=[ast.Name(id=buf_name, ctx=ast.Load())] + expandParamListsWithLengths(getCppCode(params)),
            keywords=[])
    ]

    return function_ast


boolops = {
    'and': ast.And,
    'or': ast.Or,
}

binops = {
    'mul': ast.Mult,
    'div': ast.Div,
    'add': ast.Add,
    'sub': ast.Sub,
}

compops = {
    'lt': ast.Lt,
    'lte': ast.LtE,
    'gt': ast.Gt,
    'gte': ast.GtE,
    'eq': ast.Eq,
    'neq': ast.NotEq,
    'is': ast.Is,
}

unops = {
    'not': ast.Not,
    'neg': ast.USub,
}

literals = {
    'literal': ast.Str
}

functions = {
    'like': {
        'name': 'sql_builtin_like',
        'params': 2,
        'nargs': False,
        'generator': None
    },
    'in': {
        'name': 'sql_builtin_in',
        'params': 1,
        'nargs': True,
        'generator': None
    },
    'concat': {
        'name': 'sql_builtin_concat',
        'params': 2,
        'nargs': True,
        'generator': getConcatFunction
    }
}

types = {
    'int32': {'ctype': 'int', 'has_length': False},
    'string': {'ctype': 'char', 'has_length': True},
    'timestamp[ms]': {'ctype': 'unsigned long long', 'has_length': False}
}


def convertLikePattern(pattern):
    assert (len(pattern.strip('%_')) > 0)
    front_anchor = None
    back_anchor = None
    if len(pattern) >= 1:
        front_anchor = pattern[0]
    if len(pattern) >= 3:
        back_anchor = pattern[-1]

    anchors = {
        '%': '.*',
        '_': '.+'
    }

    if front_anchor in anchors:
        pattern = anchors[front_anchor] + pattern[1:]

    if back_anchor in anchors:
        pattern = pattern[:-1] + anchors[back_anchor]

    return pattern


def getFunctionDefinition():
    return "void sql_query(schema_in &in, schema_out &out)"


def transformType(type):
    type_key = str(type)
    return types[type_key]


def getColumn(col):
    col_name = "col"
    if 'name' in col:
        col_name = col['name']
    elif isinstance(col['value'], str) or isinstance(col['value'], int):
        col_name = col['value']

    return {"name": col_name, "ast": getCppCode(col['value'])}


def getCppCode(node):
    if node is None:
        return ""
    else:
        if isinstance(node, dict):  # All dicts are ops.
            if len(node.keys()) == 1 or 'name' in node.keys():
                op = list(node.keys())[0]
                params = node[op]
                if op in boolops and isinstance(params, list):
                    if len(params) >= 2:
                        print("Processing BoolOp {} with parameters {}".format(op, params))
                        return getBoolOp(op, params)
                    else:
                        raise ValueError("BoolOp did not have the correct number of parameters.")
                if op in binops and isinstance(params, list):
                    if len(params) >= 2:
                        print("Processing BinOp {} with parameters {}".format(op, params))
                        if len(params) == 2:
                            return getBinOp(op, params[0], params[1])
                        else:
                            return getBinOp(op, {'add': params[:-1]}, params[-1])
                    else:
                        raise ValueError("BinOp did not have the correct number of parameters.")
                if op in compops and isinstance(params, list):
                    if len(params) == 2:
                        print("Processing CompOp {} with parameters a: {} and b: {}".format(op, params[0], params[1]))
                        return getCompOp(op, params[0], params[1])
                    else:
                        raise ValueError("CompOp did not have the correct number of parameters.")
                elif op in unops:
                    if len(params) == 1 or isinstance(params, str):
                        print("Processing UnOp {} with parameter: {}".format(op, params))
                        return getUnOp(op, params)
                    else:
                        raise ValueError("UnOp did not have the correct number of parameters.")
                elif op in literals:
                    if isinstance(params, str) or isinstance(params, dict):
                        print("Processing Literal {} with content: {}".format(op, params))
                        return getLiteralOp(op, params)
                    if isinstance(params, list):  # Expand literals when they are in a list.
                        newparams = list(map(lambda content: {'literal': content}, params))
                        print("Processing Literal {} with content: {}".format(op, newparams))
                        return getLiteralOp(op, newparams)
                    else:
                        raise ValueError("Literal did not have the correct parameter type.")
                elif op in functions:
                    func = functions[op]
                    print("Processing Function {} with params: {}".format(op, params))
                    return getFunction(op, params)
                else:
                    raise ValueError("Unsupported operator {}.".format(op))
            else:
                raise ValueError("Node types with multiple ops are not supported.")
        elif isinstance(node, list):  # Lists are parameters
            print("Processing parameter list with params: {}".format(node))
            tmp = list(map(getCppCode, node))
            return tmp
        else:
            if isinstance(node, int):
                return ast.Num(node)
            else:
                return ast.Name(node, ast.Load())


def getBoolOp(op, a):
    if op in boolops:
        return ast.BoolOp(boolops[op](), list(map(getCppCode, a)))
    else:
        raise ValueError("BoolOp type not supported.")


def getBinOp(op, a, b):
    if op in binops:
        return ast.BinOp(getCppCode(a), binops[op](), getCppCode(b))
    else:
        raise ValueError("BinOp type not supported.")


def getCompOp(op, a, b):
    if op in compops:
        return ast.Compare(getCppCode(a), [compops[op]()], [getCppCode(b)])
    else:
        raise ValueError("CompOp type not supported.")


def getUnOp(op, a):
    if op in unops:
        return ast.UnaryOp(unops[op](), getCppCode(a))
    else:
        raise ValueError("UnOp type not supported.")


def getLiteralOp(op, content):
    if op in literals:
        if isinstance(content, str) and op == 'literal':
            return ast.Str(content)
        else:
            return getCppCode(content)
    else:
        raise ValueError("Literal type not supported.")


def getFunction(op, params):
    if op in functions:
        func = functions[op]
        if len(params) == func['params'] or (func['nargs'] and len(params) >= func['params']) or \
                ('literal' in params and len(params) == 1 and (len(params['literal']) == func['params'] or (
                        func['nargs'] and len(params['literal']) >= func['params']))):
            if func['generator']:
                return func['generator'](func, params)
            else:
                return ast.Call(
                    func=ast.Name(
                        id=functions[op]['name'],
                        ctx=ast.Load()
                    ),
                    args=expandParamListsWithLengths(getCppCode(params)),
                    keywords=[])
        else:
            raise ValueError("Function did not have the correct parameter number.")
    else:
        raise ValueError("Function type not supported.")


def getLengthFunction(func):
    if isinstance(func, ast.Call):
        func_name = func.func.id
        func_lookup = {functions[x]['name']: x for x in functions.keys()}
        if func_name in func_lookup:
            return ast.Call(
                func=ast.Name(
                    id=functions[func_lookup[func_name]]['name_length'],
                    ctx=ast.Load()
                ),
                args=func.args[1::2],
                keywords=[])
        else:
            raise ValueError("Function {} not found.".format(func_name))
    elif isinstance(func, ast.Name):
        return func
    else:
        raise ValueError("Argument was not of type ast.Call or ast.Name but {}.".format(func))


def expandParamListsWithLengths(params):
    newlist = []
    for param in params:
        if isinstance(param, ast.Name):
            if param.id in in_col_reg:
                newlist.append(param)
                if in_col_reg[param.id]['type']['has_length']:
                    newlist.append(ast.Name(id=param.id + "_len", ctx=param.ctx))
            else:
                raise KeyError(
                    "Found undefined column {}, make sure your input schema is correct "
                    "and agrees with the columns used in the query.".format(param.id))
        elif isinstance(param, ast.Str):
            newlist.append(param)
            newlist.append(ast.Num(len(param.s)))
        elif isinstance(param, ast.Num):
            str_value = str(param.n)
            newlist.append(ast.Str(str_value))
            newlist.append(ast.Num(len(str_value)))
        else:
            raise ValueError(
                "Unsupported item in parameter list {}.".format(param))

    return newlist


def ASTHLSStream(t):
    return ast.Subscript(
        value=ast.Name(
            id='hls::stream',
            ctx=ast.Load()),
        slice=ast.Name(
            id=t,
            ctx=ast.Load()))


if __name__ == "__main__":
    in_schema = pa.read_schema("../schema-test/in_schema.fbs")
    out_schema = pa.read_schema("../schema-test/out_schema.fbs")

    in_col_reg = {}
    out_col_reg = {}

    for col in in_schema:
        print("IN Field: {}, type: {}, nullable: {}".format(col.name, col.type, col.nullable))
        in_col_reg[col.name] = {'type': transformType(col.type), 'nullable': col.nullable}

    for col in out_schema:
        print("OUT Field: {}, type: {}, nullable: {}".format(col.name, col.type, col.nullable))
        out_col_reg[col.name] = {'type': transformType(col.type), 'nullable': col.nullable}

    obj = msp.parse(
        "select int1, CONCAT(string1,4) as concat, CONCAT('123456',string1) as concat2 from jobs WHERE int1 >= 5 + 4 + 2 AND (-int2) < 3")

    # print("Select Columns: {}".format(obj['select']))
    # print("Where Condition: {}".format(obj['where']))

    # print("Total tree height: {}".format(height(obj['where'])))

    cols = list(map(getColumn, obj['select']))

    filter = getCppCode(obj['where'])

    in_schema_tmp_ast = []
    in_schema_load_ast = []
    in_schema_ast = []
    out_schema_tmp_ast = []
    out_schema_store_ast = []
    out_schema_ast = []

    print("\n\n")

    for col in cols:
        col_name = col['name']
        col_name_code = col_name + "_o"
        if out_col_reg[col_name]['type']['has_length']:
            col_ast = ast.AnnAssign(
                target=ast.Name(
                    id=col_name_code,
                    ctx=ast.Store()
                ),
                annotation=ast.Name(
                    id=out_col_reg[col_name]['type']['ctype'] + '*',
                    ctx=ast.Load()),
                value=col['ast'],
                simple=1)
        else:
            col_ast = ast.AnnAssign(
                target=ast.Name(
                    id=col_name_code,
                    ctx=ast.Store()),
                annotation=ast.Name(
                    id=out_col_reg[col_name]['type']['ctype'],
                    ctx=ast.Load()),
                value=col['ast'],
                simple=1)

        col_len = ast.AnnAssign(
            target=ast.Name(
                id=col_name_code + '_len',
                ctx=ast.Store()),
            annotation=ast.Name(
                id='int',
                ctx=ast.Load()),
            value=getLengthFunction(col['ast']),
            simple=1)

        if out_col_reg[col_name]['type']['has_length']:
            output_col_ast = ast.For(
                target=ast.Name(id='i', ctx=ast.Store()),
                iter=ast.Call(
                    func=ast.Name(
                        id='range',
                        ctx=ast.Load()
                    ),
                    args=[
                        ast.Num(0),
                        ast.Name(
                            id=col_name_code + '_len',
                            ctx=ast.Load()
                        )
                    ],
                    keywords=[]
                ),
                body=[ast.Expr(ast.BinOp(
                    left=
                    ast.Attribute(
                        value=ast.Name(
                            id='out_data',
                            ctx=ast.Load()),
                        attr=col_name,
                        ctx=ast.Store()),
                    op=ast.LShift(),
                    right=ast.Subscript(
                        value=ast.Name(
                            id=col_name_code,
                            ctx=ast.Load()
                        ),
                        slice=ast.Index(ast.Name(
                            id='i',
                            ctx=ast.Load()
                        )),
                        ctx=ast.Load()
                    ),
                    type_comment=None))
                ],
                orelse=None,
                type_comment=ast.Name(
                    id='int',
                    ctx=ast.Load()
                )
            )
        else:
            output_col_ast = ast.Expr(ast.BinOp(
                left=
                ast.Attribute(
                    value=ast.Name(
                        id='out_data',
                        ctx=ast.Load()),
                    attr=col_name,
                    ctx=ast.Store()),
                op=ast.LShift(),
                right=ast.Name(
                    id=col_name_code,
                    ctx=ast.Load()
                ),
                type_comment=None))

        output_col_ast_len = ast.Expr(ast.BinOp(
            left=
            ast.Attribute(
                value=ast.Name(
                    id='out_data',
                    ctx=ast.Load()),
                attr=col_name + '_len',
                ctx=ast.Store()),
            op=ast.LShift(),
            right=ast.Name(
                id=col_name_code + '_len',
                ctx=ast.Load()
            ),
            type_comment=None))

        col_def = ast.AnnAssign(
            target=ast.Name(
                id=col_name,
                ctx=ast.Store()),
            annotation=ASTHLSStream(str(out_col_reg[col_name]['type']['ctype'])),
            value=None,
            simple=1)

        col_def_len = ast.AnnAssign(
            target=ast.Name(
                id=col_name + '_len',
                ctx=ast.Store()),
            annotation=ASTHLSStream('int'),
            value=None,
            simple=1)

        if out_col_reg[col_name]['type']['has_length']:
            out_schema_tmp_ast.append(col_len)
            out_schema_store_ast.append(output_col_ast_len)
            out_schema_ast.append(col_def_len)
        out_schema_tmp_ast.append(col_ast)
        out_schema_store_ast.append(output_col_ast)
        out_schema_ast.append(col_def)

    for col_name in in_col_reg:

        if in_col_reg[col_name]['type']['has_length']:
            col_tmp_def = ast.AnnAssign(
                target=ast.Subscript(
                    value=ast.Name(
                        id=col_name,
                        ctx=ast.Store()
                    ),
                    slice=ast.Index(ast.Num(STRING_LEN)),
                    ctx=ast.Store()
                ),
                annotation=ast.Name(
                    id=in_col_reg[col_name]['type']['ctype'],
                    ctx=ast.Load()),
                value=None,
                simple=1)
        else:
            col_tmp_def = ast.AnnAssign(
                target=ast.Name(
                    id=col_name,
                    ctx=ast.Store()),
                annotation=ast.Name(
                    id=in_col_reg[col_name]['type']['ctype'],
                    ctx=ast.Load()),
                value=None,
                simple=1)

        col_tmp_def_len = ast.AnnAssign(
            target=ast.Name(
                id=col_name + '_len',
                ctx=ast.Store()),
            annotation=ast.Name(id='int', ctx=ast.Store()),
            value=None,
            simple=1)
        if in_col_reg[col_name]['type']['has_length']:
            col = ast.For(
                target=ast.Name(id='i', ctx=ast.Store()),
                iter=ast.Call(
                    func=ast.Name(
                        id='range',
                        ctx=ast.Load()
                    ),
                    args=[
                        ast.Num(0),
                        ast.Name(
                            id=col_name + '_len',
                            ctx=ast.Load()
                        )
                    ],
                    keywords=[]
                ),
                body=[ast.Expr(ast.BinOp(
                    left=ast.Attribute(
                        value=ast.Name(
                            id='in_data',
                            ctx=ast.Load()),
                        attr=col_name,
                        ctx=ast.Load()),
                    op=ast.RShift(),
                    right=ast.Subscript(
                        value=ast.Name(
                            id=col_name,
                            ctx=ast.Load()
                        ),
                        slice=ast.Index(ast.Name(
                            id='i',
                            ctx=ast.Load()
                        )),
                        ctx=ast.Store()
                    ),
                    type_comment=None)
                )],
                orelse=None,
                type_comment=ast.Name(
                    id='int',
                    ctx=ast.Load()
                )
            )
        else:
            col = ast.Expr(ast.BinOp(
                left=ast.Attribute(
                    value=ast.Name(
                        id='in_data',
                        ctx=ast.Load()),
                    attr=col_name,
                    ctx=ast.Load()),
                op=ast.RShift(),
                right=ast.Name(
                    id=col_name,
                    ctx=ast.Store()),
                type_comment=None))
        col_len = ast.Expr(ast.BinOp(
            left=ast.Attribute(
                value=ast.Name(
                    id='in_data',
                    ctx=ast.Load()),
                attr=col_name + "_len",
                ctx=ast.Load()),
            op=ast.RShift(),
            right=ast.Name(
                id=col_name + "_len",
                ctx=ast.Store()),
            type_comment=None))

        col_def = ast.AnnAssign(
            target=ast.Name(
                id=col_name,
                ctx=ast.Store()),
            annotation=ASTHLSStream(str(in_col_reg[col_name]['type']['ctype'])),
            value=None,
            simple=1)

        col_def_len = ast.AnnAssign(
            target=ast.Name(
                id=col_name + '_len',
                ctx=ast.Store()),
            annotation=ASTHLSStream('int'),
            value=None,
            simple=1)

        if in_col_reg[col_name]['type']['has_length']:
            in_schema_ast.append(col_def_len)
            in_schema_load_ast.append(col_len)
            in_schema_tmp_ast.append(col_tmp_def_len)
        in_schema_ast.append(col_def)
        in_schema_load_ast.append(col)
        in_schema_tmp_ast.append(col_tmp_def)

    body_ast = in_schema_tmp_ast + in_schema_load_ast

    body_ast.append(ast.AnnAssign(
        target=ast.Name(
            id='__pass_record',
            ctx=ast.Store()
        ),
        annotation=ast.Name(
            id='bool',
            ctx=ast.Load()
        ),
        value=filter,
        simple=1
    ))
    body_ast += out_schema_tmp_ast

    body_ast.append(ast.If(
        test=ast.Name(
            id='__pass_record',
            ctx=ast.Load()),
        body=out_schema_store_ast,
        orelse=[]))

    function_ast = ast.FunctionDef(
        name='query',
        args=ast.arguments(
            args=[
                ast.arg(
                    arg='in_data',
                    annotation=ast.Index(ast.Name(
                        id='in_schema',
                        ctx=ast.Load())),
                    type_comment=None),
                ast.arg(
                    arg='out_data',
                    annotation=ast.Index(ast.Name(
                        id='out_schema',
                        ctx=ast.Load())),
                    type_comment=None)
            ],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[]),
        body=body_ast,
        decorator_list=[],
        returns=ast.Name(
            id='bool',
            ctx=ast.Load()),
        type_comment=None)

    header_ast = [ast.Expr(ast.ClassDef(
        name='in_schema',
        bases=[],
        keywords=[],
        body=in_schema_ast,
        decorator_list=[ast.Name(
            id='struct',
            ctx=ast.Load())])),
        ast.Expr(ast.ClassDef(
            name='out_schema',
            bases=[],
            keywords=[],
            body=out_schema_ast,
            decorator_list=[ast.Name(
                id='struct',
                ctx=ast.Load())])),
        function_ast
    ]

    code_ast = [
        function_ast
    ]

    with open("example.py", 'r') as source:
        print("Example File:")
        test_filt = ast.parse(source.read(), "example.py")
        print(astunparse.dump(test_filt.body))

    vhdre.RegexMatcher('test', '.+test.*')

    to_language = transpyle.Language.find('C++')
    unparser = transpyle.Unparser.find(to_language)(headers=False)
    unparser_header = transpyle.Unparser.find(to_language)(headers=True)

    cpp_code = unparser.unparse(code_ast)
    cpp_header = unparser_header.unparse(header_ast)
    print("C++ header:")
    print(cpp_header)
    print("C++ code:")
    print(cpp_code)

    with open("../../codegen-cpp/query.cpp", 'w') as source_file:
        source_file.write(source_code_header)
        source_file.write(str(cpp_code))

    with open("../../codegen-cpp/query.h", 'w') as header_file:
        header_file.write(source_header_header)
        header_file.write(str(cpp_header))

    # reverseLevelOrder(obj['where'])
