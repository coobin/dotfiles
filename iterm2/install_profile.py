#!/usr/bin/env python3
import json
import plistlib
import subprocess
import sys
from pathlib import Path


def read_preferences():
    try:
        raw = subprocess.check_output(
            ["defaults", "export", "com.googlecode.iterm2", "-"],
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return {}
    return plistlib.loads(raw)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: install_profile.py <profile.json>")

    profile_path = Path(sys.argv[1]).expanduser().resolve()
    profile = dict(json.loads(profile_path.read_text())["Profiles"][0])
    profile.pop("Dynamic Profile Filename", None)
    profile.pop("Rewritable", None)

    prefs = read_preferences()
    bookmarks = prefs.get("New Bookmarks", [])
    bookmarks = [
        bookmark
        for bookmark in bookmarks
        if bookmark.get("Guid") != profile.get("Guid")
        and bookmark.get("Name") != profile.get("Name")
    ]
    bookmarks.append(profile)

    prefs["New Bookmarks"] = bookmarks
    prefs["Default Bookmark Guid"] = profile["Guid"]

    output = Path("/tmp/com.googlecode.iterm2.dotfiles-profile.plist")
    output.write_bytes(plistlib.dumps(prefs, fmt=plistlib.FMT_XML, sort_keys=False))
    subprocess.check_call(["defaults", "import", "com.googlecode.iterm2", str(output)])


if __name__ == "__main__":
    main()
