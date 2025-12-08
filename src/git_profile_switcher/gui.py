#!/usr/bin/env python3
import subprocess
import sys
from argparse import Namespace

from .cli import list_profiles, cmd_use


def main(argv=None) -> int:
    # Check zenity
    try:
        subprocess.run(["zenity", "--version"], check=False, stdout=subprocess.DEVNULL)
    except FileNotFoundError:
        print(
            "zenity not found. Please install it (e.g. `sudo apt install zenity`).",
            file=sys.stderr,
        )
        return 1

    profiles = list_profiles()
    if not profiles:
        subprocess.run(
            [
                "zenity",
                "--error",
                "--title=Git Profile Switcher",
                "--text=No profiles found.\nRun `git-profile init` and create profiles.",
            ]
        )
        return 1

    zenity_args = [
        "zenity",
        "--list",
        "--title=Git Profile Switcher",
        "--text=Choose a Git profile to activate:",
        "--column=Profile",
    ]
    zenity_args.extend(profiles)

    result = subprocess.run(
        zenity_args,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return 0  # cancelled

    choice = result.stdout.strip()
    if not choice:
        return 0

    # Activate profile
    ns = Namespace(name=choice)
    cmd_use(ns)

    uname = subprocess.run(
        ["git", "config", "--global", "user.name"],
        capture_output=True,
        text=True,
    ).stdout.strip() or "(no name)"

    uemail = subprocess.run(
        ["git", "config", "--global", "user.email"],
        capture_output=True,
        text=True,
    ).stdout.strip() or "(no email)"

    info_text = (
        f"Activated profile: <b>{choice}</b>\n\n"
        f"Current identity:\n<b>Name:</b> {uname}\n<b>Email:</b> {uemail}"
    )

    subprocess.run(
        [
            "zenity",
            "--info",
            "--title=Git Profile Updated",
            f"--text={info_text}",
        ]
    )

    return 0
