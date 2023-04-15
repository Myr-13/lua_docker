import re
from typing import Tuple, Any, Union


class Indexer:
	def __init__(self):
		self.func_pattern = r"^(\w+)\s+(\w+)\s*\(\s*((\w+)\s+(\w+)\s*(,\s*(\w+)\s+(\w+)\s*)*)?\)$"
		self.class_pattern = r"^class\s+(\w+)$"

	def c_function(self, line: str) -> Tuple[bool, Union[str, Any], Union[str, Any], Tuple[Union[str, Any], ...]]:
		line = line.replace("\n", "")
		line = line.replace("\t", "")
		line = line.replace(";", "")
		line = line.replace("const", "")
		line = line.replace("virtual", "")
		line = line.replace("override", "")
		line = line.replace("{", "")
		line = line.replace("*", "")
		line = line.replace("}", "")

		match = re.match(self.func_pattern, line)

		if not match:
			return False, "", "", ()

		raw_args = match.groups()[3:]
		args = tuple(filter(lambda x: x is not None, raw_args))

		return True, match.group(2), match.group(1), args

	def c_class(self, line: str) -> Tuple[bool, str]:
		match = re.match(self.class_pattern, line)

		if not match:
			return False, ""

		return True, match.group(1)
