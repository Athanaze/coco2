"""
This script handles the interactions for Com-301 assignments 1.
You can run this script with '--help' argument to get additional information.

Warning: You should not modify this script.
"""

import argparse
import subprocess
import sys

from grp import getgrgid
from pathlib import Path
from pwd import getpwuid
from stat import filemode
from time import sleep
from typing import List

import requests


BASE_URI = "https://springsrv4.epfl.ch/hw01"
EDITOR = "pluma"
EMAIL_FILE = "mail.txt"
EXERCISE_DIR = "fiveNine"
SCIPER_FILE = ".sciper"

ERR_CONNECTION_FAILED = """Failed to connect to the server.
Ensures that you are on site, or that you are using the VPN.
Otherwise, call an assistant."""


def get_email(sciper: int) -> str:
    """Retrieve the email from the company."""

    uri = BASE_URI + "/pop3"
    content = {
        "sciper": sciper
    }
    try:
        response = requests.get(uri, json=content, timeout=5.0)
    except Exception:
        raise Exception(ERR_CONNECTION_FAILED)

    return response.text


def validate_solution(sciper: int, answer: str) -> str:
    """Validate the solution."""

    uri = BASE_URI + "/validate"
    content = {
        "sciper": sciper,
        "answer": answer
    }
    try:
        response = requests.post(uri, json=content, timeout=5.0)
    except Exception:
        raise Exception(ERR_CONNECTION_FAILED)

    return response.text


def validate_sciper(sciper: int) -> None:
    """Ensures the SCIPER is valid."""
    err_str = "Invalid SCIPER!"
    if sciper < 100000:
        raise Exception(err_str)


def retrieve_email_handler(namespace):
    """Retrieve the email on the server."""

    print("Welcome to the E corp's mail service.")
    sys.stdout.write("Login: ")
    sys.stdout.flush()

    login = "Elliot Alderson"
    for character in login:
        sys.stdout.write("{}".format(character))
        sys.stdout.flush()
        sleep(0.06)

    sciper = namespace.sciper
    validate_sciper(sciper)

    sciper_file = Path.home() / SCIPER_FILE

    with sciper_file.open("w+") as sciper_fd:
        sciper_fd.write(str(sciper))

    response = get_email(sciper)

    file_path = Path(EMAIL_FILE)

    if file_path.exists() and (not file_path.is_file()):
        raise Exception("Can not save email as {} already exists!".format(EMAIL_FILE))

    with file_path.open("w+") as mail_fd:
        mail_fd.write(response)

    try:
        subprocess.run([EDITOR, str(file_path), "&"], check=True)
    except Exception:
        # If a problem occurred when displaying the email,
        # fall back by displaying it on the standard output.
        print("You have 1 email:")
        print(response)


def share_solution_handler(namespace):
    """Verify solution for homework 01."""

    print("Welcome to the share system of the company, Mr Alderson.")

    try:
        sciper_path = Path.home() / SCIPER_FILE
        with sciper_path.open("r") as sciper_fd:
            sciper = int(sciper_fd.read())
            validate_sciper(sciper)
    except FileNotFoundError:
        raise Exception("First check your mail!")

    dir_path = Path(EXERCISE_DIR)
    if not dir_path.exists():
        raise Exception("{} directory not found!".format(EXERCISE_DIR))

    if not dir_path.is_dir():
        raise Exception("{} is not a directory!".format(EXERCISE_DIR))

    # Retrieve the owner, group, and mode for each file,
    # and represent them as a string similar to the output of "ls -l".
    files = list()
    for hw1_file in dir_path.iterdir():
        name = hw1_file.name

        lstat = hw1_file.lstat()
        mode = filemode(lstat.st_mode)
        owner = getpwuid(lstat.st_uid).pw_name
        group = getgrgid(lstat.st_gid).gr_name

        ls_str = "{} {} {} {}".format(mode, owner, group, name)
        files.append(ls_str)

    files.sort()

    files_str = "\n".join(files)

    response = validate_solution(sciper, files_str)

    print(response)


def main(args: List[str]) -> None:
    """Entrypoint of the program."""

    parser = argparse.ArgumentParser(
        description="Script to retrieve and submit solution for homework 01."
    )

    subparsers = parser.add_subparsers(dest="cmd")

    parser_email = subparsers.add_parser(
        "get-email",
        help="Retrieve your instruction emails."
    )
    parser_email.add_argument(
        "sciper",
        type=int,
        help="Your SCIPER number."
    )
    parser_email.set_defaults(callback=retrieve_email_handler)

    parser_share = subparsers.add_parser(
        "share",
        help="Check your solution."
    )
    parser_share.set_defaults(callback=share_solution_handler)

    # Parse arguments
    namespace = parser.parse_args(args)

    if "callback" in namespace:
        try:
            namespace.callback(namespace)
        except Exception as err:
            sys.stderr.write('{}\n'.format(err))
            sys.stderr.flush()
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
