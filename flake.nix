{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/23.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = import nixpkgs { inherit system; };
      in {
        packages = rec {
          default = nix-be;
          nix-be = pkgs.python3Packages.buildPythonApplication {
            name = "nix-be";
            version = "0.0.1";
            src = ./.;
            propagatedBuildInputs = with (pkgs.python3Packages); [
              sqlite-utils
              packaging
            ];
            doCheck = false;
          };
        };

        devShells = {
          default =
            pkgs.mkShell { buildInputs = with pkgs; [ sqlite rlwrap ]; };
        };
      });
}
