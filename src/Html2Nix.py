import logging
from NetscapeBookmarksFileParser import *
from NetscapeBookmarksFileParser import parser
import os
from sys import argv, stdout

log = logging.getLogger(__name__)
# TODO: Reset to INFO.
log.setLevel(logging.DEBUG)
#log.setLevel(logging.INFO)
s_handler = logging.StreamHandler(stdout)
log.addHandler(s_handler)


class Html2Nix:
	def __init__(self, input_file_path: str = "./bookmarks.html", output_file_path: str = None, indent_size: int = 2, include_brackets: bool = True) -> None:
		'''
		Converts `NETSCAPE bookmark file HTML https://discourse.nixos.org/t/error-reading-symbolic-link-nix-var-nix-profiles-per-user-root-channels-no-such-file-or-directory/34838https://learn.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/aa753582(v=vs.85)`_
		to Nix syntax accepted by Home Manager's
		`programs.firefox.profiles.<name>.bookmarks https://discourse.nixos.org/t/error-reading-symbolic-link-nix-var-nix-profiles-per-user-root-channels-no-such-file-or-directory/34838https://nix-community.github.io/home-manager/options.xhtml#opt-programs.firefox.profiles._name_.bookmarks`_.

		:param input_file_path: Path to HTML file exported from brower, including file name, that caller would like converted to Nix.
		:type input_file_path: str
		:param output_file_path: Path to file caller would like resulting text written to. When not provided, stdout will be used.
		:type output_file_path: str
		:param indent_size: Number of space(s) each indent should represent.
		:type indent_size: int
		:param include_brackets: 'True' when caller would like nix syntax surounded by brackets ([]).
		:type include_brackets: bool
		'''
		log.debug("html2nix starting...")
		
		# Get list of bookmarks from provided input file.
		try:
			self.bookmarks = input_file_path
		except IOError:
			return
		# Ensures provided output path is valid.
		try:
			self.output_path = output_file_path
		except IOError:
			return
		# Configure indentation.
		if indent_size >= 0:
			self.indent_string = " " * indent_size
		else:
			log.error(f"'{indent_size}' is an invalid indent size. It must be non-negative.")
			return
		# Configure Nix syntax.
		self.include_brackets = include_brackets
		# Convert from HTML to Nix.
		self.nix = self.to_nix(self.convert())
		# Write resulting Nix syntax.
		self.produce_output()

	@property
	def bookmarks(self) -> list():
		'''
		:return: Returns list of :py:class:`BookmarkShortcut` and :py:class:`BookmarkFolder` objects, among other types.
		:rtype: list()
		'''
		return self._bookmarks

	@bookmarks.setter
	def bookmarks(self, path: str) -> None:
		'''
		Reads in file at provided path and converts file contents to a list of :py:class:`BookmarkShortcut`
		and :py:class:`BookmarkFolder` object(s) (among other type(s)).

		:param path: Path to file caller would like input to be read from.
		:type path: str
		:raises IOError: Occurs when provided file path can't be read.
		'''
		log.debug(f"Attempting to open input bookmarks file from '{path}'...")
		try:
			with open(path, "r") as f:
				log.debug("Input file opened, attempting to read contents...")
				self._bookmarks = NetscapeBookmarksFile(f).parse().bookmarks.items
		except IOError as e:
			log.error(f"Failed to open input HTML file '{path}'. If no path was provided, do so. If one was, then correct it.")
			raise e
	
	@property
	def output_path(self) -> str:
		'''
		Will be `None` when stdout is being used.

		:return: Retruns path to file output will be written to.
		:rtype: str/None
		'''
		return self._output_path

	@output_path.setter
	def output_path(self, path: str) -> None:
		'''
		:param path: Path to file caller would like output written to.
		:type path: str
		:raises OSError: Occurs when file pointer for writting can't be created to provided file path.
		'''
		if path:
			log.debug(f"Checking if output file path '{path}' can be opened with write privileges...")
			try:
				with open(path, "w") as f:
					self._output_path = path
			except IOError as e:
				log.error(f"Failed to open output file '{path}'. Ensure provided output path is valid and can be written to, or leave out output option.")
				raise e
		else:
			self._output_path = None

	def convert_shortcut(self, shortcut: BookmarkShortcut) -> dict():
		'''
		Converts provided :py:class:`BookmarkShortcut` object into a dictionary.

		:param shortcut: :py:class:`BookmarkShortcut` caller would like converted into a dictionary.
		:type shortcut: :py:class:`BookmarkShortcut'
		:return: Dictionary of provided object's contents.
		:rtype: dict()
		'''
		log.debug(f"Converting '{shortcut.name}' to native Python object type...")
		if shortcut.tags:
			return {
				"name": shortcut.name.replace('"', ''),
				"url": shortcut.href,
				"tags": shortcut.tags
			}
		return {
			"name": shortcut.name.replace('"', ''),
			"url": shortcut.href
		}

	def convert_folder(self, folder: BookmarkFolder) -> dict():
		'''
		Converts provided :py:class:`BookmarkFolder` object into a dictionary.

		:param folder: :py:class:`BookmarkFolder` caller would like converted into a dictionary.
		:type folder: :py:class:`BookmarkFolder`
		:return: Dictionary of provided object's contents.
		:rtype: dict()
		'''
		log.debug(f"Converting '{folder.name}' to native Python object type...")
		if folder.personal_toolbar:
			return {
				"name": folder.name.replace('"', ''),
				"toolbar": folder.personal_toolbar,
				"bookmarks": self.convert(folder.items)
			}
		return {
			"name": folder.name.replace('"', ''),
			"bookmarks": self.convert(folder.items)
		}

	def convert(self, bookmarks: list() = None) -> list():
		'''
		Converts list of :py:class:`NetscapeBookmarkFile` objects into native Python variables contained in a list.

		:param bookmarks: List of Netscape HTML file contents as parsed by :py:class:`NetscapeBookmarkFile`.
		:type bookmarks: list()
		:return: List of shortcuts and folder from bookmark HTML file stored in Python native variables in a list.
		:rtype: list()
		'''
		# Check if default value need be used.
		if bookmarks == None:
			bookmarks = self.bookmarks
		# Stores and returns converted bookmark data.
		rt_b = list()

		for b in bookmarks:
			log.debug(f"Checking if '{b.name}' should be converted to Nix syntax...")
			if isinstance(b, BookmarkShortcut) and b.name != "Recent Tags":
				rt_b.append(self.convert_shortcut(b))
			elif isinstance(b, BookmarkFolder):
				rt_b.append(self.convert_folder(b))

		return rt_b

	def shortcut_to_nix(self, shortcut: dict(), indent_amount: int) -> str:
		'''
		Converts provided shortcut data to Nix formatted string.

		:param shortcut: Shortcut data to be converted to Nix string.
		:type shortcut: dict()
		:param indent_amount: Number of indent(s) returned text should use.
		:type indent_amount: int
		:return: Provided shortcut as Nix syntax formatted string.
		:rtype: str
		'''
		indent = self.indent_string * indent_amount

		# Name.
		msg = f"{indent}{self.indent_string}name = \"{shortcut['name']}\";\n"
		# URL.
		msg += f"{indent}{self.indent_string}url = \"{shortcut['url']}\";\n"
		# Format tags when provided.
		if "tags" in shortcut.keys():
			tags_msg = "[ "
			for t in shortcut["tags"]:
				tags_msg += f'"{t}" '
			tags_msg += "]"
			msg += f"{indent}{self.indent_string}tags = {tags_msg};\n"

		return f"{indent}" + "{\n" + msg + f"{indent}" + "}\n"

	def folder_to_nix(self, folder: dict(), indent_amount: int) -> str:
		'''
		Converts provided folder data to Nix formatted string.

		:param folder: Folder data to be converted to Nix string.
		:type folder: dict()
		:param indent_amount: Number of indent(s) returned text should use.
		:type indent_amount: int
		:return: Provided folder as Nix syntax formatted string.
		:rtype: str
		'''
		indent = self.indent_string * indent_amount

		# Name.
		msg = f"{indent}{self.indent_string}name = \"{folder['name']}\";\n"
		# Toolbar status.
		if "toolbar" in folder.keys():
			msg += f"{indent}{self.indent_string}toolbar = {str(folder['toolbar']).lower()};\n"
		# Folder contents.
		msg += f"{indent}{self.indent_string}bookmarks = [\n"
		msg += self.bookmarks_to_nix(folder["bookmarks"], indent_amount+2)

		return f"{indent}" + "{\n" + msg + f"{indent}{self.indent_string}];\n" + f"{indent}" + "}\n"

	def bookmarks_to_nix(self, bookmarks: list(), indent_amount: int) -> str:
		'''
		Converts provided list of bookmarks to Nix formatted text.

		:param bookmarks: List of bookmarks caller would like converted to Nix syntax.
		:type bookmarks: list()
		:param indent_amount: Number of indent(s) the returned text should use.
		:type indent_amount: int
		:return: Provided bookmark list as a Nix syntax formatted string.
		:rtype: str
		'''
		rt_nix = ""

		for b in bookmarks:
			if "url" in b.keys():
				rt_nix += self.shortcut_to_nix(b, indent_amount)
			else:
				rt_nix += self.folder_to_nix(b, indent_amount)
	
		return rt_nix

	def to_nix(self, bookmarks: list(), indent_amount: int = 0) -> str:
		'''
		Handles formatting of suronding Nix syntax.

		:param folder: Folder data to be converted to Nix string.
		:type folder: dict()
		:param indent_amount: Number of indent(s) returned text should use.
		:type indent_amount: int
		:return: Provided folder as Nix syntax formatted string.
		:rtype: str
		'''
		# Add brackets when requested.
		if self.include_brackets:
			return indent_amount * self.indent_string + "[\n" + self.bookmarks_to_nix(bookmarks, indent_amount+1) + indent_amount * self.indent_string + "]\n"
		else:
			return self.bookmarks_to_nix(bookmarks, indent_amount)

	def produce_output(self) -> None:
		'''
		Writes Nix syntax output to stdout or a file when provided.
		'''
		if self.nix:
			if self.output_path != None:
				with open(self.output_path, "w") as f:
					f.write(self.nix)
			else:
				print(self.nix)
		else:
			log.warn("Can't produce output because none yet exists.")


def main():
	parameters = dict()
	# Process command line argument(s).
	i = 1
	argv_len = len(argv)
	while i < argv_len:
		if argv[i] in ["-i", "--input"]:
			if i + 1 < argv_len:
				i += 1
				parameters["input_file_path"] = argv[i]
			else:
				raise ValueError("Input option provided with no path.")
		elif argv[i] in ["-o", "--output"]:
			if i + 1 < argv_len:
				i += 1
				parameters["output_file_path"] = argv[i]
			else:
				raise ValueError("Output option provided with no path.")
		i += 1

	Html2Nix(**parameters)

if __name__ == "__main__":
	main()


