class CodegenError(Exception):
    """Base class for other exceptions"""
    pass


class SchemaFileNotReadable(CodegenError):
    """Raised when schema file is not readable."""
    pass

class QueryTooShort(CodegenError):
    """Raised when input query is too short."""
    pass

class OutputDirIsNotWritable(CodegenError):
    """Raised when output directory is not writeable."""
    pass

class OutSchemaColumnCodegenError(CodegenError):
    """Raised when the out schema does not have the same number of columns as the query."""
    pass


class UnsupportedArgumentTypeError(CodegenError):
    """Raised when there is an unsupported type in a function parameter."""
    pass
