# rtfix/swappiness.py
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

import re
import subprocess

from gi.repository import Adw, Gtk, GObject

from .template import autofix
from .utils import is_flatpak, run_cmd, dir_exists


class Swappiness:
    def __init__(self) -> None:
        self.conf_path = "/etc/sysctl.conf"
        self.multi_conf_dir = "/etc/sysctl.d"
        self.proc_path = "/proc/sys/vm/swappiness"
        self.tmp_file = "/tmp/sysctl.conf"
    
    def get(self) -> int:
        with open(self.proc_path) as f:
            return int(f.read())

    # FIXME: pkexec fails with manual installation on Ubuntu 24.10 (flatpak is fine)
    def set(self, value: int) -> None:
        assert value >= 0
        assert value <= 100

        # recent ubuntu use /etc/sysctl.d/ for configuration
        if dir_exists(self.multi_conf_dir):
            conf_file = "/etc/sysctl.d/11-millisecond-swappiness.conf"
            run_cmd(["pkexec", "bash", "-c" , f"echo vm.swappiness=10 > {conf_file} && sysctl -p {conf_file}"])

        # other systems should use /etc/sysctl.conf
        else:
            if is_flatpak():
                conf = subprocess.check_output(["flatpak-spawn", "--host", "bash", "-c" , f"cat {self.conf_path}"]).decode('utf-8')
            else:
                with open(self.conf_path) as f:
                    conf = f.read()

            new_swap = f"vm.swappiness={value}"
            vm_re = re.compile(r"vm.swappiness=\d+")

            if vm_re.search(conf) is None:
                conf = "\n".join([conf, new_swap])
            else:
                conf = vm_re.sub(new_swap, conf)

            with open(self.tmp_file, 'w') as f:
                f.write(conf)

            run_cmd(["pkexec", "bash", "-c" , f"cp {self.tmp_file} {self.conf_path} && sysctl -p"])



@autofix
class SwappinessDialog(Adw.AlertDialog):
    __gtype_name__ = "SwappinessDialog"

    updated = GObject.Signal('updated')
    fixed = GObject.Signal('fixed')
    fixing = GObject.Signal('fixing')

    def __init__(self, cqs, check_name, **kwargs) -> None:
        super().__init__(**kwargs)

        self.rtcqs = cqs
        self.check_name = check_name

        self.swap = Swappiness()
        super().set_heading("Set swappiness to 10?")
        super().set_body("This will modify sysctl configuration in /etc/sysctl.conf or /etc/sysclt.d/, changes are definitive.")

        super().add_response("cancel", "Cancel")
        super().add_response("ok", "OK")
        
        super().set_default_response("ok")
        super().set_close_response("cancel")
        
        super().set_response_appearance("ok", Adw.ResponseAppearance.SUGGESTED)
        
        super().connect("response", self.on_dialog_response)

    def on_dialog_response(self, _, response):
        if response == 'ok':
            self.fix()

    def fix(self) -> None:
        self.fixing.emit()
        self.swap.set(10)
        self.fixed.emit()

    def refresh(self) -> None:
        ...
