import moz_sql_parser as msp

import pyarrow as pa

import llvmlite.ir as ir

datatypes = {
    pa.Int32Value: ir.IntType(4),
    pa.DoubleValue: ir.DoubleType(),
    pa.StringValue: ir.ArrayType(ir.IntType(1),255)
}

boolops = {
    'and': ir.IRBuilder.and_,
    'or': ir.IRBuilder.or_,
}

binops = {
    'mul':ast.Mult,
    'div':ast.Div,
    'add':ast.Add,
    'sub':ast.Sub,
    }

compops = {
    'lt':ast.Lt,
    'lte':ast.LtE,
    'gt':ast.Gt,
    'gte':ast.GtE,
    'eq':ast.Eq,
    'neq':ast.NotEq,
    'is':ast.Is,
    }

unops = {'not':ast.Not,
          'neg':ast.USub,
         }

literals = {'literal':ast.Str,
            'value':""}

functions = {
    'like': {
        'name': 'sql_builtin_like',
        'params': 2,
        'nargs': False
        },
    'in':{
        'name': 'sql_builtin_in',
        'params': 1,
        'nargs': True                   
    },
    'concat':{
        'name': 'sql_builtin_concat',
        'params': 2,
        'nargs': True                   
    }
             }

def getFunctionDefinition():
    return "void sql_query(schema_in &in, schema_out &out)"

def getCppCode(node): 
    if node is None: 
        return "" 
    else:   
        if isinstance(node, dict): # All dicts are ops.
            if len(node.keys()) == 1 or 'name' in node.keys():
                op = list(node.keys())[0]
                params = node[op]
                if op in boolops and isinstance(params, list):
                    if len(params) == 2:
                        print("Processing BoolOp {} with parameters a: {} and b: {}".format(op,params[0],params[1]))
                        return getBoolOp(op,params[0],params[1])
                    else:
                        raise ValueError("BinOp did not have the correct number of parameters.")
                if op in binops and isinstance(params, list):
                    if len(params) == 2:
                        print("Processing BinOp {} with parameters a: {} and b: {}".format(op,params[0],params[1]))
                        return getBinOp(op,params[0],params[1])
                    else:
                        raise ValueError("BinOp did not have the correct number of parameters.")
                if op in compops and isinstance(params, list):
                    if len(params) == 2:
                        print("Processing CompOp {} with parameters a: {} and b: {}".format(op,params[0],params[1]))
                        return getCompOp(op,params[0],params[1])
                    else:
                        raise ValueError("BinOp did not have the correct number of parameters.")
                elif op in unops:
                    if len(params) == 1:
                        print("Processing UnOp {} with parameter: {}".format(op,params))
                        return getUnOp(op,params)
                    else:
                        raise ValueError("UnOp did not have the correct number of parameters.") 
                elif op in literals:
                    if isinstance(params, str) or isinstance(params, dict):
                        print("Processing Literal {} with content: {}".format(op,params))
                        return getLiteralOp(op,params)  
                    if isinstance(params, list): #  Expand literals when they are in a list.
                        newparams = list(map(lambda content: {'literal':content},params))
                        print("Processing Literal {} with content: {}".format(op,newparams))
                        return getLiteralOp(op,newparams)  
                    else:
                        raise ValueError("Literal did not have the correct parameter type.") 
                elif op in functions:
                    func = functions[op]
                    print("Processing Function {} with params: {}".format(op,params))
                    return getFunction(op,params)                    
                else:
                    raise ValueError("Unsupported operator {}.".format(op)) 
            else:
                raise ValueError("Node types with multiple ops are not supported.") 
        elif isinstance(node, list): # Lists are parameters
            print("Processing parameter list with params: {}".format(node))
            tmp = list(map(getCppCode,node))
            return tmp
        else:
            if isinstance(node,int):
                return ast.Num(node)
            else:
                return ast.Name(node,ast.Load())

def getBoolOp(op,a,b):
    if op in boolops:
        return ast.BoolOp(boolops[op](),[getCppCode(a),getCppCode(b)])
    else:
        raise ValueError("BoolOp type not supported.")

def getBinOp(op,a,b):
    if op in binops:
        return ast.BinOp(getCppCode(a),binops[op](),getCppCode(b))
    else:
        raise ValueError("BinOp type not supported.")

def getCompOp(op,a,b):
    if op in compops:
        return ast.Compare(getCppCode(a),[compops[op]()],[getCppCode(b)])
    else:
        raise ValueError("CompOp type not supported.")

def getUnOp(op,a):
    if op in unops:
        return ast.UnaryOp(unops[op](),getCppCode(a))
    else:
        raise ValueError("UnOp type not supported.") 

def getLiteralOp(op,content):
    if op in literals:
        if isinstance(content, str) and op == 'literal':
            return ast.Str(content)
        else:
            return getCppCode(content)
    else:
        raise ValueError("Literal type not supported.") 

def getFunction(op,params):
    if op in functions:
        func = functions[op]
        if len(params) == func['params'] or (func['nargs'] and len(params) >= func['params']) or \
        ('literal' in params and len(params) == 1 and (len(params['literal']) == func['params'] or (func['nargs'] and len(params['literal']) >= func['params']))):
            return ast.Call(ast.Name(functions[op]['name'],ast.Load()),getCppCode(params),[])
        else:
            raise ValueError("Function did not have the correct parameter number.") 
    else:
        raise ValueError("Function type not supported.") 
  
if __name__ == "__main__":

    schema = pa.read_schema("../schema-test/schema.fbs")

    name_reg = {}

    for col in schema:
        #print("Field: {}, type: {}, nullable: {}".format(col.name, col.type, col.nullable))
        name_reg[col.name] = {"type": col.type, "nullable": col.nullable}

    print(name_reg)

    obj = msp.parse("select a, CONCAT('a','b','c') as concat from jobs WHERE a > 5 AND (-b) < 3")

    print("Select Columns: {}".format(obj['select']))
    print("Where Condition: {}".format(obj['where']))

    #print("Total tree height: {}".format(height(obj['where'])))

    cols = list(map(getCppCode, obj['select']))


    filter = getCppCode(obj['where'])

    filter = ast.If(filter,[ast.Pass()],[ast.Pass()])
    test_filt = ast.parse("if a > 5 and (-b) < 3:\n  pass\nelse:\n  pass","local")

    print(astunparse.dump(test_filt.body[0]))
    print("C++ filter:")
    print(astunparse.dump(filter))

    print("C++ columns")
    colcount = 0
    for col in cols:
        print("col{} = {};".format(colcount,astunparse.dump(col)))
        colcount += 1
    #reverseLevelOrder(obj['where'])