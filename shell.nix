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
			version = "1.2";
			src = fetchFromGitHub {
				owner = "ReedClanton";
				repo = "Netscape-Bookmarks-File-Parser";
				rev = "v1.2";
				hash = "sha256-b4AFTHNMv0aMy25URe22cIAZvAL3pkP0oas//SMWCHY=";
			};
		})
	];

	shellHook = ''
		python3 -c "import html2nix" > bookmarks.nix
	'';
}
