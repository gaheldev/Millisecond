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
import subprocess as sp

def is_flatpak():
    """Detect if the current process is running inside a Flatpak sandbox.
    Returns True if in Flatpak, False otherwise.
    """
    return os.path.exists('/.flatpak-info')

def run_cmd(cmd: list[str]) -> sp.CompletedProcess[bytes]:
    if is_flatpak():
        cmd = ["flatpak-spawn", "--host"] + cmd
    return sp.run(cmd)

def cmd_exists(cmd: str) -> bool:
    """Check if command line tool `cmd` exists"""
    return run_cmd(["which", "cpupower"]).returncode == 0

