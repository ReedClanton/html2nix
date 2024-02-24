from NetscapeBookmarksFileParser import *
from NetscapeBookmarksFileParser import parser


class Html2Nix:
	def __init__(self, input_path: str = "./bookmarks.html", indent_size: int = 2) -> None:
		'''
		Converts `NETSCAPE bookmark file HTML https://discourse.nixos.org/t/error-reading-symbolic-link-nix-var-nix-profiles-per-user-root-channels-no-such-file-or-directory/34838https://learn.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/aa753582(v=vs.85)`_
		to Nix syntax accepted by Home Manager's
		`programs.firefox.profiles.<name>.bookmarks https://discourse.nixos.org/t/error-reading-symbolic-link-nix-var-nix-profiles-per-user-root-channels-no-such-file-or-directory/34838https://nix-community.github.io/home-manager/options.xhtml#opt-programs.firefox.profiles._name_.bookmarks`_.

		:param input_path: Path to HTML file exported from brower including file name.
		:type input_path: str
		:param indent_size: Number of space(s) each indent should represent.
		:type indent_size: int
		'''
		self.input_path = input_path
		self.indent_size = indent_size
		self.indent_string = " " * self.indent_size

		with open(self.input_path, "r") as file:
			bookmarks = NetscapeBookmarksFile(file).parse()

		self.nix = self.to_nix(self.convert(bookmarks.bookmarks.items))

	@property
	def input_path(self) -> str:
		'''
		TODO

		:return: TODO
		:rtype: str
		'''
		return self._input_path

	@input_path.setter
	def input_path(self, path: str) -> None:
		'''
		TODO

		:param path: TODO
		:type path: str
		'''
		# TODO: Ensure provided value is a valid path to a file.
		self._input_path = path

	@property
	def indent_size(self) -> int:
		'''
		TODO

		:return: TODO
		:rtype: int
		'''
		return self._indent_size

	@indent_size.setter
	def indent_size(self, indent_size: int) -> None:
		'''
		TODO

		:param indent_size: TODO
		:type indent_size: int
		'''
		if indent_size < 1:
			raise ValueError(f"'{indent_size}' is an invalid indent size because it's less not positive.")
		self._indent_size = indent_size

	def convert_shortcut(self, shortcut: BookmarkShortcut) -> dict():
		'''
		Converts provided :py:class:`BookmarkShortcut` object into a dictionary.

		:param shortcut: :py:class:`BookmarkShortcut` caller would like converted into a dictionary.
		:type shortcut: :py:class:`BookmarkShortcut'
		:return: Dictionary of provided object's contents.
		:rtype: dict()
		'''
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

	def convert(self, bookmarks: list()) -> list():
		'''
		Converts :py:class:`NetscapeBookmarkFile` object into native Python variables contained in a list.

		:param bookmarks: Netscape bookmarks HTML file contents as parsed by :py:class:`NetscapeBookmarkFile`.
		:type bookmarks: list()
		:return: List of shortcuts and folder from bookmark HTML file stored in Python native variables in a list.
		:rtype: list()
		'''
		# Stores and returns converted bookmark data.
		rt_b = list()

		for b in bookmarks:
			if isinstance(b, BookmarkShortcut) and b.name != "Recent Tags":
				rt_b.append(self.convert_shortcut(b))
			elif isinstance(b, BookmarkFolder):
				rt_b.append(self.convert_folder(b))

		return rt_b

	def shortcut_to_nix(self, shortcut: dict(), indent: int) -> str:
		'''
		Converts provided shortcut data to Nix formatted string.

		:param shortcut: Shortcut data to be converted to Nix string.
		:type shortcut: dict()
		:param indent: Starting indent of returned Nix syntax in number of tabs.
		:type indent: int
		:return: Provided shortcut as Nix syntax formatted string.
		:rtype: str
		'''
		tab = self.indent_string * indent

		# Name.
		msg = f"{tab}{self.indent_string}name = \"{shortcut['name']}\";\n"
		# URL.
		msg += f"{tab}{self.indent_string}url = \"{shortcut['url']}\";\n"
		# Format tags when provided.
		if "tags" in shortcut.keys():
			tags_msg = "[ "
			for t in shortcut["tags"]:
				tags_msg += f'"{t}" '
			tags_msg += "]"
			msg += f"{tab}{self.indent_string}tags = {tags_msg};\n"

		return f"{tab}" + "{\n" + msg + f"{tab}" + "}\n"

	def folder_to_nix(self, folder: dict(), indent: int) -> str:
		'''
		Converts provided folder data to Nix formatted string.

		:param folder: Folder data to be converted to Nix string.
		:type folder: dict()
		:param indent: Starting indent of returned Nix syntax in number of tabs.
		:type indent: int
		:return: Provided folder as Nix syntax formatted string.
		:rtype: str
		'''
		tab = self.indent_string * indent

		# Name.
		msg = f"{tab}{self.indent_string}name = \"{folder['name']}\";\n"
		# Toolbar status.
		if "toolbar" in folder.keys():
			msg += f"{tab}{self.indent_string}toolbar = {str(folder['toolbar']).lower()};\n"
		# Folder contents.
		msg += f"{tab}{self.indent_string}bookmarks = [\n"
		msg += self.to_nix(folder["bookmarks"], indent+2)

		return f"{tab}" + "{\n" + msg + f"{tab}{self.indent_string}];\n" + f"{tab}" + "}\n"

	def to_nix(self, bookmarks: list(), indent: int = 0) -> str:
		'''
		Converts provided list of bookmarks to Nix formatted text.

		:param bookmarks: List of bookmarks caller would like converted to Nix syntax.
		:type bookmarks: list()
		:param indent: Starting indent of returned Nix syntax in number of tabs.
		:type indent: int
		:return: Provided bookmark list as a Nix syntax formatted string.
		:rtype: str
		'''
		rt_nix = ""

		for b in bookmarks:
			if "url" in b.keys():
				rt_nix += self.shortcut_to_nix(b, indent)
			else:
				rt_nix += self.folder_to_nix(b, indent)
	
		return rt_nix



html2nix = Html2Nix("./input/bookmarks.html")
print(html2nix.nix)

