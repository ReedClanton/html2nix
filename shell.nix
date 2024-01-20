with import <nixpkgs> {};
with pkgs.python3Packages;

buildPythonPackage rec {
	pname = "html2nix";
	version = "0.0.1";
	src = ./.;

	format = "pyproject";

	propagatedBuildInputs = [
		setuptools
		(buildPythonPackage rec {
			pname = "NetscapeBookmarksFileParser";
			version = "1.1";
			src = fetchFromGitHub {
				owner = "FlyingWolFox";
				repo = "Netscape-Bookmarks-File-Parser";
				rev = "v1.1";
				hash = "sha256-zCdwfOkYvGPEdWYxo4Tas1JDK60zjyxWzfuflP4y38U=";
			};
		})
	];
}
