import argparse
import tempfile
import subprocess
import sqlite3
import re
from packaging.version import Version

import logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.ERROR)

def functionRegex(value, package):
    c_pattern = re.compile(f"/nix/store/[a-zA-Z0-9]{{32}}-{package}-(\d+\.)?(\d+\.)?(\*|\d+)$")
    return c_pattern.search(value) is not None

def extract_version(path, package):
    c_pattern = re.compile(f"/nix/store/([a-zA-Z0-9]{{32}})-{package}-((\d+\.)?(\d+\.)?(\*|\d+))$")
    return c_pattern.search(path).group(2)

def generate_rcfile(paths):
    add_to_path_env = ":".join(f"{path}/bin" for path in paths)
    return f"""
declare -x PS1="[\\u@\\h:(nix-best-effort) \\W]\\$ "
declare -x PATH="$PATH:{add_to_path_env}"
"""

def main():
    parser = argparse.ArgumentParser(
                    prog='nix-be',
                    description='Create a low cost environment from what is already in your /nix/store')
    parser.add_argument('package', help="Package to include in the environment", nargs='*')
    parser.add_argument('-v', '--verbose', help="backstage access", action='store_true')

    args = parser.parse_args()
    packages = args.package
    verbose = args.verbose

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    connection = sqlite3.connect("file:///nix/var/nix/db/db.sqlite?immutable=1", uri=True)
    logging.info("Connected to Nix DB")

    connection.create_function("REGEXP", 2, functionRegex)
    cursor = connection.cursor()

    env = []

    for package in packages:
        logging.info(f"Now considering package '{package}'")

        rows = cursor.execute(f"SELECT path FROM ValidPaths WHERE REGEXP(path, ?)", (package,)).fetchall()
        if len(rows) == 0:
            logging.error(f"No package '{package}' found in store")
            continue
        if verbose:
            for find in rows:
                logging.info(f"Found package: {find[0]}")
        latest = max(rows, key=lambda x: Version(extract_version(x[0], package)))[0]
        if verbose: logging.info(f"Most recent version of '{package}' found: {latest}")
        env.append(latest)

    logging.info(f"Environment: {env}")
    if len(env) == 0:
        logging.error("Empty environment: Aborting")
        return 1

    rc_file = tempfile.NamedTemporaryFile(mode="wb")
    rc_content = generate_rcfile(env)
    logging.info(f"RC content: {rc_content}")
    logging.info(f"RC file location: {rc_file.name}")
    with open(rc_file.name, "wb") as rc:
        rc.write(rc_content.encode('utf8'))
    subprocess.run(["bash", "--rcfile", rc_file.name])

    return 0

if __name__ == "__main__":
    main()
