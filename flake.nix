{
  description = "html2nix – Convert Firefox bookmarks HTML export into Home Manager Nix syntax";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs { inherit system; };
      pypkgs = pkgs.python3.pkgs;

      html2nix = pypkgs.buildPythonApplication rec {
        pname = "html2nix";
        version = "0.0.2";
        src = ./.;
        format = "pyproject";

        # pythonRuntimeDepsCheck fails for wheels that have missing version specifiers in METADATA
        # https://github.com/NixOS/nixpkgs/issues/285234
        dontCheckRuntimeDeps = true;

        propagatedBuildInputs = with pypkgs; [
          setuptools
          (buildPythonPackage rec {
            pname = "NetscapeBookmarksFileParser";
            version = "1.2";
            src = pkgs.fetchFromGitHub {
              owner = "ReedClanton";
              repo = "Netscape-Bookmarks-File-Parser";
              rev = "v${version}";
              hash = "sha256-b4AFTHNMv0aMy25URe22cIAZvAL3pkP0oas//SMWCHY=";
            };
            format = "setuptools";
            propagatedBuildInputs = [setuptools];
          })
        ];
      };
    in {
      packages.default = html2nix;

      apps.default = flake-utils.lib.mkApp {
        drv = html2nix;
        exePath = "/bin/html2nix";
      };
    });
}

