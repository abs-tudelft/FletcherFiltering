// Copyright 2018 Delft University of Technology
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <arrow/api.h>
#include <fletcher/api.h>

#include <memory>
#include <iostream>

/// @brief Prepare a RecordBatch to hold the output data.
std::shared_ptr<arrow::RecordBatch> PrepareRecordBatch(const std::shared_ptr<arrow::Schema> &schema,
                                                       int64_t num_items) {
  //std::shared_ptr<arrow::Buffer> values;

  //if (!arrow::AllocateBuffer(arrow::default_memory_pool(), sizeof(uint32_t) * num_items, &values).ok()) {
  //  throw std::runtime_error("Could not allocate buffer.");
  //}  
  
  //auto type = arrow::uint32();

  //auto array = std::make_shared<arrow::UInt64Array>(num_items, values);
  std::unique_ptr<arrow::RecordBatchBuilder> builder;
  if (!arrow::RecordBatchBuilder::Make(schema, arrow::default_memory_pool(), num_items, &builder).ok()){
    throw std::runtime_error("Could not create RecordBatchBuilder.");
  }
  std::shared_ptr<arrow::RecordBatch> batch;
  if (!builder->Flush(&batch).ok()){
    throw std::runtime_error("Could not create RecordBatch from Builder.");
  }
  //auto rb = arrow::RecordBatch::Make(schema, num_items, {array});
  //auto rb = arrow::RecordBatch::RecordBatch(schema, num_items);

  return batch;
}


/**
 * Main function for the Simple example.
 */
int main(int argc, char **argv) {
  // Check number of arguments.
  if (argc != 4) {
    std::cerr << "Incorrect number of arguments. Usage: run-snap path/to/output_schema.fbs path/to/input.rb path/to/output.rb" << std::endl;
    return -1;
  }

  std::vector<std::shared_ptr<arrow::RecordBatch>> batches;
  std::shared_ptr<arrow::Schema> schema;
  std::shared_ptr<arrow::RecordBatch> input_batch;
  std::shared_ptr<arrow::RecordBatch> output_batch;

  fletcher::Timer t;

  int64_t num_items = 0;

  t.start();
  fletcher::ReadSchemaFromFile(argv[1], &schema);

  // Attempt to read the RecordBatch from the supplied argument.
  fletcher::ReadRecordBatchesFromFile(argv[2], &batches);

  // RecordBatch should contain exactly one batch.
  if (batches.size() != 1) {
    std::cerr << "File did not contain any Arrow RecordBatches." << std::endl;
    return -1;
  }

  // The only RecordBatch in the file is our input RecordBatch.
  input_batch = batches[0];

  num_items = input_batch->num_rows();
  
  output_batch = PrepareRecordBatch(schema, num_items);
  std::cout << "Created output record batch with " << num_items << " rows." << std::endl;
  fletcher::Status status;
  std::shared_ptr<fletcher::Platform> platform;
  std::shared_ptr<fletcher::Context> context;
  

  fletcher::RecordBatchDescription input_desc;
  fletcher::RecordBatchAnalyzer input_analyzer(&input_desc);
  input_analyzer.Analyze(*input_batch);

  int64_t input_size = 0;
  for (const auto &b : input_desc.buffers) {
      input_size+=b.size_;
  }

  fletcher::RecordBatchDescription output_desc;
  fletcher::RecordBatchAnalyzer output_analyzer(&output_desc);
  output_analyzer.Analyze(*output_batch);

  int64_t output_size = 0;
  for (const auto &b : output_desc.buffers) {
      output_size+=b.size_;
  }
  t.stop();
  std::cout << "Dataset setup                    : " << t.seconds() << std::endl;
  std::cout << "Input dataset size               : " << input_size << std::endl;
  std::cout << "Output dataset size              : " << output_size << std::endl;
  t.start();
  // Create a Fletcher platform object, attempting to autodetect the platform.
  status = fletcher::Platform::Make(&platform);

  if (!status.ok()) {
    std::cerr << "Could not create Fletcher platform." << std::endl;
    return -1;
  }

  // Initialize the platform.
  status = platform->Init();

  if (!status.ok()) {
    std::cerr << "Could not create Fletcher platform." << std::endl;
    return -1;
  }

  // Create a context for our application on the platform.
  status = fletcher::Context::Make(&context, platform);

  if (!status.ok()) {
    std::cerr << "Could not create Fletcher context." << std::endl;
    return -1;
  }
  t.stop();
  std::cout << "Platform and context setup       : " << t.seconds() << std::endl;
  t.start();
  // Queue the recordbatch to our context.
  status = context->QueueRecordBatch(input_batch);

  if (!status.ok()) {
    std::cerr << "Could not queue the input RecordBatch to the context." << std::endl;
    return -1;
  }

  // Queue the recordbatch to our context.
  status = context->QueueRecordBatch(output_batch);

  if (!status.ok()) {
    std::cerr << "Could not queue the output RecordBatch to the context." << std::endl;
    return -1;
  }
  t.stop();
  std::cout << "Record bacth queueing            : " << t.seconds() << std::endl;
  t.start();

  // "Enable" the context, potentially copying the recordbatch to the device. This depends on your platform.
  // AWS EC2 F1 requires a copy, but OpenPOWER SNAP doesn't.
  context->Enable();

  if (!status.ok()) {
    std::cerr << "Could not enable the context." << std::endl;
    return -1;
  }

  // Create a kernel based on the context.
  fletcher::Kernel kernel(context);

  // Reset the kernel.
  status = kernel.Reset();

  if (!status.ok()) {
    std::cerr << "Could not reset the kernel." << std::endl;
    return -1;
  }

  t.stop();
  std::cout << "Enable context and setup kernel  : " << t.seconds() << std::endl;
  t.start();

  // Start the kernel.
  status = kernel.Start();

  if (!status.ok()) {
    std::cerr << "Could not start the kernel." << std::endl;
    return -1;
  }

  // Wait for the kernel to finish.
  status = kernel.WaitForFinish();

  if (!status.ok()) {
    std::cerr << "Something went wrong waiting for the kernel to finish." << std::endl;
    return -1;
  }
  t.stop();
  double execution_time = t.seconds();
  std::cout << "Kernel execution time            : " << t.seconds() << " s" << std::endl;  
  t.start();
  //Write the record batch to a file
  fletcher::WriteRecordBatchesToFile(argv[3], {output_batch});

  std::cout << "Wrote output record batch to file..." << std::endl;

  // Obtain the return value.
  uint32_t passed_records;
  uint32_t total_records;
  status = kernel.GetReturn(&passed_records, &total_records);

  if (!status.ok()) {
    std::cerr << "Could not obtain the return value." << std::endl;
    return -1;
  }
  t.stop();
  std::cout << "Cleanup and saving output        : " << t.seconds() << " s" << std::endl;  
  // Print the return value.
  std::cout << "Passed records: " << *reinterpret_cast<uint32_t*>(&passed_records) << std::endl;
  std::cout << "Total records: " << *reinterpret_cast<uint32_t*>(&total_records) << std::endl;
  std::cout << "Kernel input bandwitdh           : " << (((double)input_size)/(num_items)*(*reinterpret_cast<uint32_t*>(&passed_records))/execution_time) << " b/s" << std::endl;
  std::cout << "Kernel output bandwitdh          : " << (((double)input_size)/(num_items)*(*reinterpret_cast<uint32_t*>(&total_records))/execution_time) << " b/s" << std::endl;
  return 0;
}