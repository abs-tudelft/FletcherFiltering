#  Copyright (c) 2019 Erwin de Haan. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#  This file is part of the FletcherFiltering project

class CodegenError(Exception):
    """Base class for other exceptions"""
    pass

class MetaLengthColumnError(CodegenError):
    """Raised when the given meta length count column does not exist in the input schema."""
    pass

class FletchgenError(CodegenError):
    """Raised when the fletchgen process exits with a non-zero value."""
    pass

class VivadoHLSError(CodegenError):
    """Raised when the Vivado HLS process exits with a non-zero value, or is not supported on the current platform."""
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

class MetaLengthColumnError(CodegenError):
    """Raised when the out schema does not have the same number of columns as the query."""
    pass

class UnsupportedArgumentTypeError(CodegenError):
    """Raised when there is an unsupported type in a function parameter."""
    pass
