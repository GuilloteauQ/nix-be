{
  description = "A very basic flake";

  inputs = { nixpkgs.url = "github:nixos/nixpkgs/23.05"; };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in {
      packages.${system} = rec {
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

      devShells.${system} = {
        default = pkgs.mkShell { buildInputs = with pkgs; [ gcc clang ]; };
      };

    };
}
