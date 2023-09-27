# Nix Best-Effort (`nix-be`)

Create a low cost Nix environment from what is already in your /nix/store.

**Warning**: of course there are no guarantee on which version of the package you ask you will get.

## Run

For example, a shell with `python3` and `R`:

```
nix run github:GuilloteauQ/nix-be -- python3 R
```

You can run a command and exit the shell with the `-c/--command` flag:

```
nix run github:GuilloteauQ/nix-be -- python3 R --command "R --version"
```

## Usage

```
$ nix run github:GuilloteauQ/nix-be -- --help
usage: nix-be [-h] [-c COMMAND] [-v] package [package ...]

Create a low cost environment from what is already in your /nix/store

positional arguments:
  package               Package to include in the environment

options:
  -h, --help            show this help message and exit
  -c COMMAND, --command COMMAND
                        command to execute in the shell
  -v, --verbose         backstage access
```
