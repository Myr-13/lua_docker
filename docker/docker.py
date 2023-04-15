import os
import fnmatch
from docker.indexer import Indexer


def progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end='\r'):
	percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
	filled_length = int(length * iteration // total)
	bar = fill * filled_length + '-' * (length - filled_length)
	print(f'\r{prefix} {iteration}/{total} |{bar}| {percent}% {suffix}', end=print_end)
	# Print New Line on Complete
	if iteration == total:
		print()


def count_header_files(directory):
	count = 0
	for root, dirs, files in os.walk(directory):
		for file in files:
			if not fnmatch.fnmatch(file, "*.h") and not fnmatch.fnmatch(file, "*.hpp"):
				continue
			count += 1
	return count


class Docker:
	def __init__(self, input_file: str, output_file: str, source_directory: str):
		self.input_file = open(input_file, "r")
		self.output_file = open(output_file, "w")
		self.src_dir = source_directory
		self.globals = {}
		self.lua_mapping = {}

	def close(self):
		self.input_file.close()
		self.output_file.close()

	def index_sources(self):
		indexer = Indexer()

		# Count of .h and .hpp files for progress bar
		total_count = count_header_files(self.src_dir)

		# Indexing
		count = 0
		for root, dirs, files in os.walk(self.src_dir):
			for file in files:
				if not fnmatch.fnmatch(file, "*.h") and not fnmatch.fnmatch(file, "*.hpp"):
					continue

				# Progress bar
				count += 1
				progress_bar(count, total_count, prefix="Progress:", suffix="Done", length=50)

				file_path = os.path.join(root, file)

				f = open(file_path, "r")

				for line in f:
					is_class, class_name = indexer.c_class(line)
					is_func, func_name, func_type, func_args = indexer.c_function(line)

					if is_class:
						self.globals[class_name] = {
							"type": "class"
						}
					elif is_func:
						self.globals[func_name] = {
							"type": "function",
							"return_type": func_type,
							"args": func_args
						}

				f.close()

	def create_mapping(self):
		for line in self.input_file:
			if "addFunction" in line:
				a = line.split("(")[1]
				a = a.replace(")", "")
				a = a.replace(" ", "")
				a = a.replace("&", "")
				a = a.replace("\n", "")
				b = a.split(",")

				name = b[0].replace("\"", "")
				name = name.replace("\'", "")
				func = "ERROR"
				return_type = "NONE"
				if b[1] in self.globals:
					func = b[1]
					return_type = self.globals[b[1]]["return_type"]

				self.lua_mapping[name] = {
					"type": "function",
					"return_type": return_type,
					"function": func
				}

	def write_output(self):
		for key in self.lua_mapping:
			mapping = self.lua_mapping[key]

			text = f"# Function: {key}\n"
			text += f"Return type: {mapping['return_type']}\n"
			text += f"Linked C++ function: {mapping['function']}\n"
			text += "\n"

			self.output_file.write(text)

	def process(self):
		print("[1/3]: Indexing sources(this may take a long time)")
		self.index_sources()
		print("[2/3]: Creating mapping")
		self.create_mapping()
		print("[3/3]: Writing output file")
		self.write_output()
