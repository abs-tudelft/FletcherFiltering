from moz_sql_parser import parse
 
# Function to print reverse level order traversal
def reverseLevelOrder(root): 
    h = height(root) 
    for i in reversed(range(1, h + 1)): 
        print(root)

def printNode(node):
    if isinstance(node, dict):
        print(node)
    elif isinstance(node, list):
        print(node)
    else:
        print(node)

# Compute the height of a tree-- the number of
# nodes along the longest path from the root node
# down to the farthest leaf node
def height(node): 
    if node is None: 
        return 0 
    else:   
        if isinstance(node, dict): # All dicts are ops.
            maxheight = 0
            for key in node.keys():
                tmpheight = height(node.get(key,None))
                if tmpheight > maxheight:
                    maxheight = tmpheight
  
            return maxheight + 1
        elif isinstance(node, list): # Lists are parameters
            maxheight = 0
            for key in node:
                tmpheight = height(key)
                if tmpheight > maxheight:
                    maxheight = tmpheight
  
            return maxheight
        else:
            return 1

binops = {
    'and':"AND",
    'or':"OR",
    'lt':"<",
    'lte':">=",
    'gt':">",
    'gte':">=",
    'eq':"==",
    'neq':"!=",
    'is':"==",
    'mul':"*",
    'div':"/",
    'add':"+",
    'sub':"!"
    }

unops = {'not':"!",
          'neg':"-"}

literals = {'literal':"'",
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

def getCppCode(node): 
    if node is None: 
        return "" 
    else:   
        if isinstance(node, dict): # All dicts are ops.
            if len(node.keys()) == 1:
                op = list(node.keys())[0]
                params = node[op]
                if op in binops and isinstance(params, list):
                    if len(params) == 2:
                        print("Processing BinOp {} with parameters a: {} and b: {}".format(op,params[0],params[1]))
                        return getBinOp(op,params[0],params[1])
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
            return ", ".join(tmp)
        else:
            return str(node)

def getBinOp(op,a,b):
    if op in binops:
        return "({1} {0} {2})".format(binops[op],getCppCode(a),getCppCode(b))
    else:
        raise ValueError("BinOp type not supported.") 

def getUnOp(op,a):
    if op in unops:
        return "({0}{1})".format(unops[op],getCppCode(a))
    else:
        raise ValueError("UnOp type not supported.") 

def getLiteralOp(op,content):
    if op in literals:
        if isinstance(content, str):
            return "{0}{1}{0}".format(literals[op],getCppCode(content))
        else:
            return getCppCode(content)
    else:
        raise ValueError("Literal type not supported.") 

def getFunction(op,params):
    if op in functions:
        func = functions[op]
        if len(params) == func['params'] or (func['nargs'] and len(params) >= func['params']) or \
        ('literal' in params and len(params) == 1 and (len(params['literal']) == func['params'] or (func['nargs'] and len(params['literal']) >= func['params']))):
                        
            return "{0}({1})".format(functions[op]['name'],getCppCode(params))
        else:
            raise ValueError("Function did not have the correct parameter number.") 
    else:
        raise ValueError("Function type not supported.") 
        

obj = parse("select a, CONCAT('a','b','c') from jobs WHERE a > 5 AND (-b) < 3 OR c IN('abc',3,'def')")

print("Select Columns: {}".format(obj['select']))
print("Where Condition: {}".format(obj['where']))

print("Total tree height: {}".format(height(obj['where'])))

cols = list(map(getCppCode, obj['select']))

filter = getCppCode(obj['where'])

print("C++ filter:")
print("if ( {} )".format(filter))

print("C++ columns")
colcount = 0
for col in cols:
    print("col{} = {};".format(colcount,col))
    colcount += 1
#reverseLevelOrder(obj['where'])