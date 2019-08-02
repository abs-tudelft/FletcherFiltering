# Copyright 2018 Delft University of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pyarrow as pa
import pyfletcher as pf
import numpy as np
import timeit
import sys
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("schema_path")
    parser.add_argument("input_path")
    parser.add_argument("output_path")
    args = parser.parse_args()

    schema = pa.read_schema(args.schema_path)
    # Set up a RecordBatch reader and read the RecordBatch.
    reader = pa.RecordBatchFileReader(args.input_path)
    input_batch = reader.get_batch(0)

    output_batch = pa.RecordBatch.from_arrays([pa.array([0] * input_batch.num_rows, pa.uint32())],schema)

    print("Got the batches.")

    platform = pf.Platform("snap", False)                         # Create an interface to an auto-detected FPGA Platform.
    platform.init()                                  # Initialize the Platform.

    print("Initialized platform.")
    context = pf.Context(platform)                   # Create a Context for our data on the Platform.
    print("Created context.")
    context.queue_record_batch(input_batch)                # Queue the RecordBatch to the Context.
    print("Queued record output batch.")
    context.queue_record_batch(output_batch)                # Queue the RecordBatch to the Context.
    print("Queued record output batch.")
    context.enable()                                 # Enable the Context, (potentially transferring the data to FPGA).
    
    print("Enabled context.")                             

    kernel = pf.Kernel(context)                      # Set up an interface to the Kernel, supplying the Context.
    kernel.reset()
    print("Reset kernel.") 
    kernel.start()                                   # Start the kernel.
    print("Started kernel.")   
    kernel.wait_for_finish()                         # Wait for the kernel to finish.

    print("Finished kernel.")
    result = kernel.get_return(np.dtype(np.uint32))  # Obtain the result.

    writer = pa.RecordBatchFileWriter(args.output_path)

    writer.write(output_batch)

    writer.close()

    print("Result: " + str(result))                     # Print the result.