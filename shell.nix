with import <nixpkgs> {};
with pkgs.python3Packages;

buildPythonPackage rec {
	pname = "html2nix";
	version = "0.0.1";
	src = ./.;

	format = "pyproject";

	propagatedBuildInputs = [
		setuptools
		fetchFromGitHub {
			owner = "FlyingWolFox";
			repo = "Netscape-Bookmarks-File-Parser";
			rev = "v1.1";
			hash = "112816d44bf4c0da8e8f442aed370020e16594e8888c8ddb10a699779dc666eb";
		}
	];
}
