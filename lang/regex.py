
import re, os
from KVUtils import KVLog, correct_path
import random
import string
from kivy.lang.builder import Builder

""" SEARCHS

- GET BINDS -=> ^(\s*)([a-zA-Z_.]+.(bind|schedule_once|schedule_interval)\(.+(\)|\s+\)))
- GET COMMENTED BINDS -=> ^(\s*)# ?([a-zA-Z_.]+.(bind|schedule_once|schedule_interval)\(.+(\)|\s+\)))

"""


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


class RegEx(object):

	line = ""
	path = ""
	destin_pah = ""
	index = -1
	n_lines = 0
	lines = None
	last_regex = None

	has_clock = False
	has_window_bind = False
	init_index_in_kv = 0

	def __init__(self, lines, path, destin_pah):
		self.lines = lines
		self.path = correct_path(path)
		self.destin_pah = correct_path(destin_pah)
		self.n_lines = len(lines)
		self.line = lines[0]

		self.imports = []

	def new(self, pattern, repl):
		last_line = self.line
		self.line = re.sub(pattern, repl, self.line)
		return last_line != self.line
	
	def sub(self, pattern, repl):
		self.last_regex = re.sub(pattern, repl, self.line)
		return self.last_regex
	
	def exist(self, pattern):
		self.search(pattern)
		return self.last_regex != None

	def search(self, pattern):
		self.last_regex = re.search(pattern, self.line)
		return self.last_regex

	def findall(self, pattern):
		self.last_regex = re.findall(pattern, self.line)
		return self.last_regex

	def get_last(self):
		if self.last_regex == None:
			return []
		return self.last_regex

	def result(self):
		return '\n'.join(self.lines)
	
	def next(self):
		if self.index > -1: 
			self.lines[self.index] = self.line
		if self.index == self.n_lines-1:
			return False
		
		self.index += 1
		self.line = self.lines[self.index]
		return True

	def insert_line(self, index, line):
		self.lines.insert(index, line)
		self.n_lines += 1
		self.index += 1
	

def get_app_class(regex, parser):
	""" Get the names of the App class and replace it by KVApp

			class MyProgram(App):
					V
			class MyProgram(SimulateApp):
			name_of_class = "MyProgram"
	"""
	if regex.exist(r"SimulateApp") and parser.find_class:
		return None

	if regex.exist(r"^\s*class\s+([a-zA-Z_]\w*)\(((MDApp)|(App))\)\s*:"):
		parser.name_of_class = regex.get_last().groups()[0]
		KVLog('NAME-APP-CLASS', parser.name_of_class)
		
		if not regex.new(r"\(\s*(MDApp|App)\s*\)\s*:", "(SimulateApp):"):
			KVLog("ERRO", f"NÃO FOI POSSÍVEL TROCAR A CLASS APP -=> '{regex.line}'")
		parser.find_class = True


def process_kv_line(regex:RegEx, parser):
	""" Get the names of the imports

			#:import ButtonEffect uix.buttons.ButtonEffect
					V
			uix/buttons.py
			uix/buttons/ButtonEffect.py

	"""
	paths = []
	if regex.exist(r"#:\s*import\s+\w+\s+(\.?\w+\.)*\w+"):
		
		regex.findall(r"((\.?\w+)\.)|((\w+))\s*$")

		names = map(lambda x: filter(lambda v: v != "", x), regex.get_last())
		names = list(map(lambda n: list(n), names))
		
		paths.append('/'.join(map(lambda n: n[-1], names)))
		paths.append('/'.join(map(lambda n: n[-1], names[0:-1])))
	
	for path in paths:
		for ext in {".py", ".kv", ".pxd", ".pyd"}:
			local = parser.get_correct_import(path + ext, regex)
			if local != None:
				regex.imports.append(local)




def process_py_line(regex:RegEx, parser, caller, init_file):

	if regex.has_clock:
		if parser.in_kv_string:
			regex.insert_line(regex.init_index_in_kv+1, "#:import KVClock lang.KivyApp.KVClock")
		else:
			regex.insert_line(0, "from lang.KivyApp import KVClock")
		regex.has_clock = None
	
	funcs = "(schedule_once|schedule_interval)"
	if regex.new(r"Clock\." + funcs + r"\(", "KVClock.\\1(") and regex.has_clock != None:
		regex.has_clock = True
	

	if regex.has_window_bind:
		regex.insert_line(0, "from lang.KivyApp import KVWindow")
		regex.has_window_bind = None

	if regex.new(r"Window\.bind\(", "KVWindow.bind(") and regex.has_window_bind != None:
		regex.has_window_bind = True
	
	
	""" Get 

			load_string('''
			...
			
			''')
					OR
			'''
				...

			'''
	"""
	if parser.in_kv_string:
		if regex.exist(r"filename\s*=\s*(\"|'|'''|\"\"\")(.+)(\"|'|'''|\"\"\")"):
			parser.has_string_filename = True
			

	""" Verify if the line is multiple commentary

			load_string('''
			...
			
			''')
					OR
			'''
				...

			'''
	"""
	if regex.exist(r"^s*Builder.load_file\(.*['\"](.+)['\"].*\)"):
		path = regex.get_last().group(1)
		slash = "" if sum(map(path.startswith, ["/", "\\"])) > 0 else "/"
		new_file = f"{os.path.split(regex.destin_pah)[0]}{slash}{path}"

		regex.insert_line(regex.index-1, f"Builder.unload_file(r'{new_file}')\n")
		KVLog("NEW-KIVY-FILE-BY-PATH", new_file)
		parser.local_kivy_files.append(new_file)

	if parser.in_kv_string:
		process_kv_line(regex, parser)
		
	if regex.exist(r"^\s*('''|\"\"\")") or regex.exist(r".+('''|\"\"\")\s*,?\s*.*\)"):
		parser.commented = not parser.commented
		if parser.in_kv_string:
			parser.in_kv_string = False
			parser.has_string_filename = False

			name_file = f"nk{get_random_string(random.randint(7, 40))}load_string_KV.kv"
			completed_path = f"{os.path.split(regex.destin_pah)[0]}/{name_file}"
			KVLog("NEW-KIVY-FILE-BY-STRING", completed_path)

			lines = list(regex.lines[regex.init_index_in_kv+1:regex.index])
			print("LINES -=> ", lines[0:5])
			
			del regex.lines[regex.init_index_in_kv:regex.index]
			regex.index -= len(lines) + 1
			regex.n_lines -= len(lines) + 1


			if lines and lines[0].startswith("Builder.load_string"):
				del lines[0]
			# regex.line = f"Builder.unload_file(r'{name_file}')\n"
			regex.line = f"\nBuilder.unload_file(r'{completed_path}')\n"
			regex.line += f"Builder.load_file(r'{completed_path}')"

			with open(completed_path, "w", encoding="UTF-8") as kivy_file:
				kivy_file.write("\n".join(lines))
			
			parser.local_kivy_files.append(completed_path)
			if not init_file:
				# Load before beacause the file can have ids that is not acessable
				# and if it will be used, will get an error.
				# to resolve this, we can reload the kvlang before and reload again later.
				Builder.load_file(completed_path)

	
	elif regex.exist(r"^\s*(\w+\.)?[a-zA-Z_]\w*\(\s*('''|\"\"\")"):
		parser.commented = not parser.commented
		parser.in_kv_string = True
		regex.init_index_in_kv = regex.index

	if regex.exist(r"^\s*#") or parser.commented:
		return None
	
	# Only for the __main__ file
	if caller == "main":
		get_app_class(regex, parser)
	

	""" Get the names of the imports

			from uix.button import XButton, XToggle
					V
			uix/button.py

			import xpath, get_path
					V
			/xpath.py
			/get_path
	"""
	paths = []
	if regex.exist(r"from ((\.?\w+)\.)*(\w+)\s+import"):
		
		regex.findall(r"((\.?\w+)\.)|((\w+)\s+import)")
		
		names = map(lambda x: filter(lambda v: v != "", x), regex.get_last())
		names = list(map(lambda n: list(n), names))
		
		paths.append('/'.join(map(lambda n: n[-1], names)))

	elif regex.exist(r"^\s*import\s+(([a-zA-Z_]\w*)\s*,\s*){0,}([a-zA-Z_]\w*)"):
		for name_import in regex.get_last().groups():
			if name_import == None or name_import[-1] in {" ", "."}:
				continue
			paths.append("/" + name_import)

	for path in paths:
		# print("ACHOU -=> ", path)
		for ext in {".py", ".pxd", ".pyd"}:
			local = parser.get_correct_import(path + ext, regex)
			if local != None:
				regex.imports.append(local)

