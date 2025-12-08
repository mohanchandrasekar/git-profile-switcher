#!/usr/bin/env python3
import argparse
import configparser
import os
import shutil
import subprocess
import sys
from textwrap import dedent

HOME = os.path.expanduser("~")
CONFIG_DIR = os.path.join(HOME, ".config", "git-profiles")
ACTIVE_CFG = os.path.join(HOME, ".gitconfig-active")
GLOBAL_CFG = os.path.join(HOME, ".gitconfig")  # kept for init/help only


def ensure_config_dir() -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)


def run_git_config(key: str) -> str | None:
    """Return `git config --global <key>` or None if not set/available."""
    try:
        result = subprocess.run(
            ["git", "config", "--global", key],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return None
        value = result.stdout.strip()
        return value or None
    except FileNotFoundError:
        return None


def cmd_init(args: argparse.Namespace) -> None:
    """Print instructions and create profile directory.

    We keep this simple now: we don't rely on includes for identity.
    Profiles live in ~/.config/git-profiles, and `git-profile use`
    will write directly to git's global config.
    """
    ensure_config_dir()

    print(f"✅ Profile directory ready: {CONFIG_DIR}")
    print()
    print("Create profiles like:")
    print(f"  {os.path.join(CONFIG_DIR, 'personal.gitconfig')}")
    print(f"  {os.path.join(CONFIG_DIR, 'work.gitconfig')}")
    print()
    print("Example profile content:")
    example = dedent(
        """
        [user]
            name = Your Name
            email = your_email@example.com
        [core]
            editor = nano
        """
    ).strip("\n")
    print(example)
    print()
    print("Or use:")
    print("  git-profile create personal --activate")
    print("  git-profile create work")


def list_profiles() -> list[str]:
    ensure_config_dir()
    if not os.path.isdir(CONFIG_DIR):
        return []
    files = [
        f
        for f in os.listdir(CONFIG_DIR)
        if f.endswith(".gitconfig")
        and os.path.isfile(os.path.join(CONFIG_DIR, f))
    ]
    files.sort()
    return [os.path.splitext(f)[0] for f in files]


def cmd_list(args: argparse.Namespace) -> None:
    profiles = list_profiles()
    if not profiles:
        print(f"No profiles found in {CONFIG_DIR}")
        print("Create one, e.g.:")
        print(f"  {os.path.join(CONFIG_DIR, 'personal.gitconfig')}")
        return
    print("Available profiles:")
    for name in profiles:
        print(f"  - {name}")


def cmd_use(args: argparse.Namespace) -> None:
    """Activate a profile: set git global user.name/user.email from the profile."""
    ensure_config_dir()
    name = args.name
    profile_path = os.path.join(CONFIG_DIR, f"{name}.gitconfig")
    if not os.path.isfile(profile_path):
        print(f"❌ Profile not found: {name}", file=sys.stderr)
        print(f"Expected file: {profile_path}", file=sys.stderr)
        sys.exit(1)

    # Parse profile as INI
    cfg = configparser.ConfigParser()
    cfg.read(profile_path)

    user_name = None
    user_email = None

    if cfg.has_section("user"):
        user_name = cfg.get("user", "name", fallback=None)
        user_email = cfg.get("user", "email", fallback=None)

    # Apply to git global config
    if user_name:
        subprocess.run(
            ["git", "config", "--global", "user.name", user_name],
            check=False,
        )
    if user_email:
        subprocess.run(
            ["git", "config", "--global", "user.email", user_email],
            check=False,
        )

    # Optional snapshot of active profile (not required for behavior)
    try:
        shutil.copy2(profile_path, ACTIVE_CFG)
    except OSError:
        pass

    print(f"✅ Activated profile: {name}")
    print()
    uname = run_git_config("user.name") or "(no name)"
    uemail = run_git_config("user.email") or "(no email)"
    print("Current global git identity:")
    print(f"  user.name  = {uname}")
    print(f"  user.email = {uemail}")


def cmd_current(args: argparse.Namespace) -> None:
    """Show the currently configured global identity and best-guess profile."""
    ensure_config_dir()
    uname = run_git_config("user.name") or "(no name)"
    uemail = run_git_config("user.email") or "(no email)"

    print("Current global git identity:")
    print(f"  user.name  = {uname}")
    print(f"  user.email = {uemail}")

    # Best-effort: try to match active config with a profile
    if os.path.isfile(ACTIVE_CFG):
        with open(ACTIVE_CFG, "rb") as f:
            active_bytes = f.read()
        for name in list_profiles():
            profile_path = os.path.join(CONFIG_DIR, f"{name}.gitconfig")
            try:
                with open(profile_path, "rb") as pf:
                    if pf.read() == active_bytes:
                        print(f"Guessed active profile: {name}")
                        break
            except FileNotFoundError:
                continue


def cmd_show(args: argparse.Namespace) -> None:
    """Print the contents of a profile."""
    ensure_config_dir()
    name = args.name
    profile_path = os.path.join(CONFIG_DIR, f"{name}.gitconfig")
    if not os.path.isfile(profile_path):
        print(f"❌ Profile not found: {name}", file=sys.stderr)
        print(f"Expected file: {profile_path}", file=sys.stderr)
        sys.exit(1)

    print(f"# Profile: {name}")
    print(f"# Path: {profile_path}")
    print()
    with open(profile_path, "r", encoding="utf-8") as f:
        sys.stdout.write(f.read())


def cmd_create(args: argparse.Namespace) -> None:
    """Interactively create a new profile."""
    ensure_config_dir()
    name = args.name
    profile_path = os.path.join(CONFIG_DIR, f"{name}.gitconfig")

    if os.path.exists(profile_path) and not args.force:
        print(f"❌ Profile already exists: {name}")
        print(f"Path: {profile_path}")
        print("Use --force to overwrite.")
        sys.exit(1)

    print(f"Creating profile: {name}")
    print("(Press Enter to accept default shown in brackets.)")

    default_name = run_git_config("user.name") or "Your Name"
    default_email = run_git_config("user.email") or "your_email@example.com"
    default_editor = "nano"

    user_name = input(f"Git user.name [{default_name}]: ").strip() or default_name
    user_email = input(f"Git user.email [{default_email}]: ").strip() or default_email
    editor = input(f"core.editor [{default_editor}]: ").strip() or default_editor

    content = dedent(
        f"""
        [user]
            name = {user_name}
            email = {user_email}
        [core]
            editor = {editor}
        """
    ).lstrip("\n")

    os.makedirs(os.path.dirname(profile_path), exist_ok=True)
    with open(profile_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Saved profile: {name}")
    print(f"   -> {profile_path}")

    if args.activate:
        # Reuse cmd_use logic to set git config + snapshot
        cmd_use(argparse.Namespace(name=name))


def build_parser() -> argparse.ArgumentParser:
    description = """\
    git-profile - simple Git identity switcher (Linux & macOS)

    Profiles are stored as:
      ~/.config/git-profiles/<name>.gitconfig

    Each profile can define:
      [user]
          name = ...
          email = ...
      [core]
          editor = ...

    `git-profile use <name>` will set:

      git config --global user.name
      git config --global user.email

    from the selected profile.
    """
    parser = argparse.ArgumentParser(
        prog="git-profile",
        description=dedent(description),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command")

    p_init = subparsers.add_parser(
        "init",
        help="Show setup instructions and create the profiles directory",
    )
    p_init.set_defaults(func=cmd_init)

    p_list = subparsers.add_parser(
        "list", help="List available profiles"
    )
    p_list.set_defaults(func=cmd_list)

    p_use = subparsers.add_parser(
        "use", help="Activate a profile by name"
    )
    p_use.add_argument("name", help="Profile name (e.g. personal, work)")
    p_use.set_defaults(func=cmd_use)

    p_current = subparsers.add_parser(
        "current", help="Show the current global identity"
    )
    p_current.set_defaults(func=cmd_current)

    p_show = subparsers.add_parser(
        "show", help="Show the contents of a profile"
    )
    p_show.add_argument("name", help="Profile name to show")
    p_show.set_defaults(func=cmd_show)

    p_create = subparsers.add_parser(
        "create", help="Interactively create a new profile"
    )
    p_create.add_argument("name", help="Profile name to create")
    p_create.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing profile if it exists",
    )
    p_create.add_argument(
        "--activate",
        action="store_true",
        help="Activate the profile immediately after creating it",
    )
    p_create.set_defaults(func=cmd_create)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 1
    return 0
