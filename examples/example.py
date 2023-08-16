from awsgitops import awsgitops

config = 'gen_config.yaml'
inputs = ['first.yaml', 'second.yaml']
# Load generators
generator_config, input_yamls, output_yamls = awsgitops.load(config, inputs)
# Run generators
status, log, threads, program_config = awsgitops.start_generators(generator_config, output_yamls)
# Wait for generators to finish
while awsgitops.threads_are_alive(threads):
	pass
# Write the output to 
for i in range(len((inputs)):
  # Only write if the file has been changed
  if input_yamls[i] != output_yamls[i]:
	  awsgitops.write_output(output_yamls[i], inputs[i])

