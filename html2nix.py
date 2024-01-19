from NetscapeBookmarksFileParser import *
from NetscapeBookmarksFileParser import parser


def html2nix(input_path: str = "./input/bookmarks.html", indent: int = 0) -> str:
	'''
	Converts `NETSCAPE bookmark file HTML https://discourse.nixos.org/t/error-reading-symbolic-link-nix-var-nix-profiles-per-user-root-channels-no-such-file-or-directory/34838https://learn.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/aa753582(v=vs.85)`_
	to Nix syntax accepted by Home Manager's
	`programs.firefox.profiles.<name>.bookmarks https://discourse.nixos.org/t/error-reading-symbolic-link-nix-var-nix-profiles-per-user-root-channels-no-such-file-or-directory/34838https://nix-community.github.io/home-manager/options.xhtml#opt-programs.firefox.profiles._name_.bookmarks`_.

	:param input_path: Path to bookmark.html file, including file name. Default: `./input/bookmarks.html`.
	:type input_path: str
	:param indent: See :py:func:`bookmark_to_nix()` Default: 0.
	:return: Nix formatted representation of provided bookmark HTML.
	:rtype: str
	'''
	with open(input_path, "r") as file:
		bookmarks = NetscapeBookmarksFile(file).parse()
	print([method_name for method_name in dir(bookmarks)])
	return bookmark_to_nix(convert_bookmarks(bookmarks.bookmarks.items), indent)

def bookmark_to_nix(bookmarks: list(), indent: int = 0) -> str:
	'''
	Converts provided list of bookmarks to Nix formatted text.

	:param bookmarks: List of bookmarks caller would like converted to Nix syntax.
	:type bookmarks: list()
	:param indent: Starting indent of returned Nix syntax in number of tabs. Default: 0.
	:type indent: int
	:return: Provided bookmark list as a Nix syntax formatted string.
	:rtype: str
	'''
	rt_nix = ""

	for b in bookmarks:
		if "url" in b.keys():
			rt_nix += shortcut_to_nix(b, indent)
		else:
			rt_nix += folder_to_nix(b, indent)
	
	return rt_nix

def shortcut_to_nix(shortcut: dict(), indent: int = 0) -> str:
	'''
	Converts provided shortcut data to Nix formatted string.

	:param shortcut: Shortcut data to be converted to Nix string.
	:type shortcut: dict()
	:param indent: Starting indent of returned Nix syntax in number of tabs. Default: 0.
	:type indent: int
	:return: Provided shortcut as Nix syntax formatted string.
	:rtype: str
	'''
	tab = "\t" * indent

	# Name.
	msg = f"{tab}\tname = \"{shortcut['name']}\";\n"
	# URL.
	msg += f"{tab}\turl = \"{shortcut['url']}\";\n"
	# Format tags when provided.
	if "tags" in shortcut.keys():
		tags_msg = "[ "
		for t in shortcut["tags"]:
			tags_msg += f'"{t}" '
		tags_msg += "]"
		msg += f"{tab}\ttags = {tags_msg};\n"
	
	return f"{tab}" + "{\n" + msg + f"{tab}" + "}\n"

def folder_to_nix(folder: dict(), indent: int = 0) -> str:
	'''
	Converts provided folder data to Nix formatted string.

	:param folder: Folder data to be converted to Nix string.
	:type folder: dict()
	:param indent: Starting indent of returned Nix syntax in number of tabs. Default: 0.
	:type indent: int
	:return: Provided folder as Nix syntax formatted string.
	:rtype: str
	'''
	tab = "\t" * indent

	# Name.
	msg = f"{tab}\tname = \"{folder['name']}\";\n"
	# Toolbar status.
	if "toolbar" in folder.keys():
		msg += f"{tab}\ttoolbar = {str(folder['toolbar']).lower()};\n"
	# Folder contents.
	msg += f"{tab}\tbookmarks = [\n"
	msg += bookmark_to_nix(folder["bookmarks"], indent+2)
	
	return f"{tab}" + "{\n" + msg + f"{tab}\t];\n" + f"{tab}" + "}\n"

def convert_bookmarks(bookmarks: list()) -> list():
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
			rt_b.append(convert_shortcut(b))
		elif isinstance(b, BookmarkFolder):
			rt_b.append(convert_folder(b))
	
	return rt_b

def convert_shortcut(shortcut: BookmarkShortcut) -> dict():
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

def convert_folder(folder: BookmarkFolder) -> dict():
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
			"bookmarks": convert_bookmarks(folder.items)
		}
	return {
		"name": folder.name.replace('"', ''),
		"bookmarks": convert_bookmarks(folder.items)
	}


print(html2nix())


