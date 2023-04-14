import os
import fnmatch


class Docker:
	def __init__(self, input_file: str, output_file: str, source_directory: str):
		self.input_file = open(input_file, "r")
		self.output_file = open(output_file, "w")
		self.src_dir = source_directory
		self.globals = {}
		self.lua_mapping = {}
		self.debug = False

	def close(self):
		self.input_file.close()
		self.output_file.close()

	def index_sources(self):
		for root, dirs, files in os.walk(self.src_dir):
			for file in files:
				if not fnmatch.fnmatch(file, "*.h"):
					continue

				file_path = os.path.join(root, file)

				if self.debug:
					print(f"Indexing: {file_path}")

				f = open(file_path, "r")

				for line in f:
					if "(" not in line:
						continue
					if " " not in line:
						continue

					line: str = line.replace("\t", "")
					line: str = line.replace("\n", "")
					
					func = line.split("(")
					func_data = func[0].split(" ")
					length = len(func_data)

					if length < 2 or length > 2:
						continue

					self.globals[func_data[1]] = {
						"type": func_data[0]
					}

				f.close()

	def create_mapping(self):
		for line in self.input_file:
			if "addFunction" in line:
				a = line.split("(")[1]
				a = a.replace(")", "")
				a = a.replace(" ", "")
				b = a.split(",")

				name = b[0].replace("\"", "")
				func = "ERROR"
				print(b[1])
				if b[1] in self.globals:
					func = b[1]

				self.lua_mapping[name] = {
					"type": "function",
					"return_type": "",
					"function": func
				}

	def write_output(self):
		for key in self.lua_mapping:
			mapping = self.lua_mapping[key]

			print(mapping)

			text = f"# Function: {key}\n"
			text += f"Return type: {mapping['return_type']}\n"
			text += f"Linked C++ function: {mapping['function']}\n"
			text += "\n"

			self.output_file.write(text)

	def process(self):
		print("[1/3]: Indexing sources(this may take a long time)")
		self.index_sources()
		print("[2/3]: Create mapping based on lua")
		self.create_mapping()
		print("[3/3]: Writing output file")
		self.write_output()
