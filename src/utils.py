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


def is_distribution_nixos():
    os_release_path = '/etc/os-release'

    if is_flatpak():
        os_release_path = '/run/host/etc/os-release'

    if not os.path.isfile(os_release_path):
        print_red(f"Couldn't check if OS is NixOS, {os_release_path} is not a valid file or permissions are not granted to read it.")
        return False

    with open(os_release_path) as f:
        for line in f:
            if 'nixos' in line.lower():
                return True
    return False


def print_red(s):
    print("\033[91m" + s + "\033[00m")

