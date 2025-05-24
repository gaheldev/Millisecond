# rtfix.py
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
import re
import resource
import subprocess

from gi.repository import Adw, Gtk, GObject

from .utils import is_flatpak, run_cmd

class Swappiness:
    def __init__(self) -> None:
        # FIXME: doesn't exist or not read on startup in some systems
        self.conf_path = "/etc/sysctl.conf"
        self.proc_path = "/proc/sys/vm/swappiness"
        self.tmp_file = "/tmp/sysctl.conf"
    
    def get(self) -> int:
        with open(self.proc_path) as f:
            return int(f.read())

    def set(self, value: int) -> None:
        assert value >= 0
        assert value <= 100

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

        if is_flatpak():
            subprocess.run(["flatpak-spawn", "--host", "pkexec", "bash", "-c" , f"cp {self.tmp_file} {self.conf_path} && sysctl -p"])
        else:
            subprocess.run(["pkexec", "bash", "-c" , f"cp {self.tmp_file} {self.conf_path} && sysctl -p"])


class SwappinessDialog(Adw.AlertDialog):
    __gtype_name__ = "SwappinessDialog"

    fixed = GObject.Signal('fixed')
    fixing = GObject.Signal('fixing')

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.swap = Swappiness()
        super().set_heading("Set swappiness to 10?")
        super().set_body("This will modify /etc/sysctl.conf, changes are definitive.")

        # Add response buttons
        super().add_response("cancel", "Cancel")
        super().add_response("ok", "OK")
        
        # Set "ok" as the default response
        super().set_default_response("ok")
        super().set_close_response("cancel")
        
        # Set "ok" as the suggested (highlighted) action
        super().set_response_appearance("ok", Adw.ResponseAppearance.SUGGESTED)
        
        # Connect to the response signal
        super().connect("response", self.on_dialog_response)

    def on_dialog_response(self, _, response):
        if response == 'ok':
            self.fix()

    def fix(self) -> None:
        self.fixing.emit()
        self.swap.set(10)
        self.fixed.emit()


class Governor:
    def __init__(self) -> None:
        # FIXME: check for all possible utilities and use the best installed one?
        self.utility: str = "cpupower"

    def set_performance(self):
        cmd = ["pkexec", "bash", "-c" , "cpupower frequency-set -g performance"]
        _ = run_cmd(cmd)

    def set_powersave(self):
        cmd = ["pkexec", "bash", "-c" , "cpupower frequency-set -g powersave"]
        _ = run_cmd(cmd)


# FIXME: allow to open dialog even when fixed but don't empasize button
class GovernorDialog(Adw.PreferencesDialog):
    __gtype_name__ = "GovernorDialog"

    updated = GObject.Signal('updated')
    fixed = GObject.Signal('fixed')
    fixing = GObject.Signal('fixing')

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.governor = Governor()
        super().set_title("Governor")

        self.preferences_page = Adw.PreferencesPage()
        self.preferences_group = Adw.PreferencesGroup()

        self.performance_switch = Adw.SwitchRow()
        self.performance_switch.set_title('Use performance governor')
        self.performance_switch.connect("notify::active", self.on_performance_changed)

        self.persistence_switch = Adw.SwitchRow()
        self.persistence_switch.set_title('Persist over restart')

        # FIXME: implement persistence over reboot
        self.preferences_group.add(self.performance_switch)
        self.preferences_group.add(self.persistence_switch)

        self.preferences_page.add(self.preferences_group)
        super().add(self.preferences_page)

    def on_performance_changed(self, switch, _):
        if switch.get_active():
            self.governor.set_performance()
        else:
            self.governor.set_powersave()
        self.updated.emit()
