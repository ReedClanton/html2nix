with import <nixpkgs> {};
with pkgs.python3Packages;

buildPythonPackage rec {
	pname = "html2nix";
	version = "0.0.2";
  # Set build method.
  format = "pyproject";
	src = ./src/.;

	propagatedBuildInputs = [
		setuptools
		(buildPythonPackage rec {
			pname = "NetscapeBookmarksFileParser";
			version = "1.2";
      # Set build method.
      format = "setuptools";
			src = fetchFromGitHub {
				owner = "ReedClanton";
				repo = "Netscape-Bookmarks-File-Parser";
				rev = "v${version}";
				hash = "sha256-b4AFTHNMv0aMy25URe22cIAZvAL3pkP0oas//SMWCHY=";
			};
		})
	];
}
