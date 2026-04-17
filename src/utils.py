# utils.py
#
# Copyright 2025 Gahel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os


def is_flatpak():
    """
    Detect if the current process is running inside a Flatpak sandbox.
    Returns True if in Flatpak, False otherwise.
    """
    return os.path.exists('/.flatpak-info')


def convert_path_to_flatpak_sandbox(path: str) -> str:
    sandboxed = ["/usr", "/etc", "/lib"]
    for sandboxed_path_root in sandboxed:
        if path.startswith(sandboxed_path_root):
            return "/run/host" + path
    return path


# This may fail in flatpak if os-release files are symlink,
# where permissions of the linked file may not be granted.
def is_distribution_nixos():
    native_candidates = [
        '/usr/lib/os-release',
        '/etc/os-release',
    ]

    flatpak_candidates = [
        '/run/host/usr/lib/os-release',
        '/run/host/etc/os-release',
    ]

    paths = flatpak_candidates if is_flatpak() else native_candidates

    for path in paths:
        try:
            with open(path) as f:
                for line in f:
                    if 'nixos' in line.lower():
                        return True
                return False
        except OSError:
            continue

    print_red(f"Couldn't check if OS is NixOS, {paths[0]} and {paths[1]} are not valid files or permissions are not granted to read them.")

    return False


def print_red(s):
    print("\033[91m" + s + "\033[00m")

