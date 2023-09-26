# nix-be

Create a low cost environment from what is already in your /nix/store.

Warning: of course there are no guarantee on which version of the package you ask.

## Run

For example, a shell with `python3` and `R`:

```
nix run github:GuilloteauQ/nix-be -- python3 R
```

## Usage

```
$ nix run github:GuilloteauQ/nix-be -- --help
usage: nix-be [-h] [-v] [package ...]

Create a low cost environment from what is already in your /nix/store

positional arguments:
  package        Package to include in the environment

options:
  -h, --help     show this help message and exit
  -v, --verbose  backstage access
```


