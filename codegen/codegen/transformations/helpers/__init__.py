__all__ = ["FunctionResolver", "ArrowTypeResolver"]

import sys

import typed_ast.ast3 as ast
import horast.nodes as horast

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
