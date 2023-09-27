import argparse
import tempfile
import subprocess
import sqlite3
import re
import os
from packaging.version import Version

import logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.ERROR)

def functionRegex(value, package):
    c_pattern = re.compile(f"/nix/store/[a-zA-Z0-9]{{32}}-{package}-(\d+\.)?(\d+\.)?(\*|\d+)$")
    return c_pattern.search(value) is not None

def extract_version(path, package):
    c_pattern = re.compile(f"/nix/store/([a-zA-Z0-9]{{32}})-{package}-((\d+\.)?(\d+\.)?(\*|\d+))$")
    return c_pattern.search(path).group(2)

def generate_rcfile(env_variables):
    other_envs = "\n".join(f"declare -x {name}=\"{':'.join(value)}\"" for (name, value) in env_variables.items())
    return f"""
declare -x PS1="[\\u@\\h:(nix-best-effort) \\w]\\$ "
{other_envs}
"""

def main():
    parser = argparse.ArgumentParser(
                    prog='nix-be',
                    description='Create a low cost Nix environment from what is already in your /nix/store')
    parser.add_argument('package', help="Package to include in the environment", nargs='+')
    parser.add_argument('-c', '--command', help="command to execute in the shell")
    parser.add_argument('-l', '--limit', help="number of results to fetch in the DB (default: 1)", default=1)
    parser.add_argument('-v', '--verbose', help="backstage access", action='store_true')

    args = parser.parse_args()
    packages = args.package
    verbose = args.verbose
    user_command = args.command
    limit = args.limit

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    connection = sqlite3.connect("file:///nix/var/nix/db/db.sqlite?immutable=1", uri=True)
    logging.info("Connected to Nix DB")

    connection.create_function("REGEXP", 2, functionRegex)
    cursor = connection.cursor()

    env_variables = {"PKG_CONFIG_PATH": [], "PATH": ["$PATH"]}

    need_pkg_config = "pkg-config" in packages

    for package in packages:
        logging.info(f"Now considering package '{package}'")

        rows = cursor.execute(f"SELECT path FROM ValidPaths WHERE REGEXP(path, ?) LIMIT {limit}", (package,)).fetchall()
        if len(rows) == 0:
            logging.error(f"No package '{package}' found in store")
            continue
        latest = rows[0][0]
        if limit > 1:
            latest = max(rows, key=lambda x: Version(extract_version(x[0], package)))[0]
        logging.info(f"Most recent version of '{package}' found: {latest}")

        if os.path.isdir(os.path.join(latest, "bin")):
            env_variables["PATH"].append(os.path.join(latest, "bin"))
        if need_pkg_config and os.path.isdir(os.path.join(latest, "lib/pkgconfig")):
            env_variables["PKG_CONFIG_PATH"].append(os.path.join(latest, "lib/pkgconfig"))

    logging.info(f"Environment: {env_variables}")
    if len(env_variables["PATH"]) == 1:
        logging.error("Empty environment: Aborting")
        return 1

    rc_file = tempfile.NamedTemporaryFile(mode="wb")
    rc_content = generate_rcfile(env_variables)
    logging.info(f"RC content: {rc_content}\nRC file location: {rc_file.name}")
    with open(rc_file.name, "wb") as rc:
        rc.write(rc_content.encode('utf8'))

    command = ["bash", "--rcfile", rc_file.name]
    if user_command:
        command += ["-ci", user_command]
    subprocess.run(command)

    return 0

if __name__ == "__main__":
    main()
