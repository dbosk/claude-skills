"""Stand-in for a program that reaches a service by itself.

offline_run.py puts a shim for each such program first on PATH; the shim
runs this as `python -I refuse.py NAME REAL [ARG ...]`, where REAL is the
program's path or empty when it is not installed.  git and rsync run as
usual unless they would talk to another host; everything else is refused.
"""

import os
import re
import sys

REMOTE_SUBCOMMANDS = {"push", "fetch", "pull", "ls-remote", "send-email"}
GIT_OPTIONS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace",
                          "--exec-path", "--config-env"}
URL = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")


def remote(arg: str) -> bool:
    """A URL other than file://, or git/rsync's host:path and user@host:path."""
    if arg.startswith("-"):
        return False
    if URL.match(arg):
        return not arg.startswith("file://")
    head = arg.split("/", 1)[0]  # rsync's host::module and scp-style host:path
    return ":" in head and not re.fullmatch(r"[A-Za-z]:", head)


def git_subcommand(args: list[str]) -> tuple[str, list[str]]:
    i = 0
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] in GIT_OPTIONS_WITH_VALUE else 1
    return (args[i], args[i + 1:]) if i < len(args) else ("", [])


def allowed(name: str, args: list[str]) -> bool:
    if name == "rsync":
        return not any(remote(a) for a in args)
    if name == "git":
        sub, rest = git_subcommand(args)
        if sub in REMOTE_SUBCOMMANDS or (sub, rest[:1]) == ("remote", ["update"]):
            return False
        if sub in ("clone", "submodule"):
            return not any(remote(a) for a in rest)
        return True
    return False


def main() -> None:
    name, real, args = sys.argv[1], sys.argv[2], sys.argv[3:]
    if not allowed(name, args):
        print(f"offline_run: refused to run {name} {' '.join(args)}: it would reach "
              "a service; run it outside offline_run if that is intended",
              file=sys.stderr)
        sys.exit(1)
    if not real:
        print(f"{name}: command not found", file=sys.stderr)
        sys.exit(127)
    os.execv(real, [name, *args])


if __name__ == "__main__":
    main()
