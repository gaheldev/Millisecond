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

from .utils import is_flatpak, run_cmd, cmd_exists

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

    updated = GObject.Signal('updated')
    fixed = GObject.Signal('fixed')
    fixing = GObject.Signal('fixing')

    def __init__(self, cqs, check_name, **kwargs) -> None:
        super().__init__(**kwargs)

        # abstract
        self.rtcqs = cqs
        # abstract
        self.check_name = check_name
        # abstract
        self.is_fix_permanent = True

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

    def refresh(self) -> None:
        pass


class Governor:
    def __init__(self) -> None:
        # FIXME: check for all possible utilities and use the best installed one?
        self.utility = "cpupower" if cmd_exists("cpupower") else None

    def utility_found(self) -> bool:
        return cmd_exists("cpupower")

    def set_performance(self) -> bool:
        cmd = ["pkexec", "bash", "-c" , "cpupower frequency-set -g performance"]
        return run_cmd(cmd).returncode == 0

    def set_powersave(self):
        cmd = ["pkexec", "bash", "-c" , "cpupower frequency-set -g powersave"]
        return run_cmd(cmd).returncode == 0


# FIXME: use interface for what is common to all Dialogs
class GovernorDialog(Adw.PreferencesDialog):
    __gtype_name__ = "GovernorDialog"

    # abstract
    updated = GObject.Signal('updated')
    fixed = GObject.Signal('fixed')
    fixing = GObject.Signal('fixing')

    def __init__(self, cqs, check_name, **kwargs) -> None:
        super().__init__(**kwargs)

        # abstract
        self.rtcqs = cqs
        # abstract
        self.check_name = check_name
        # abstract
        self.is_fix_permanent = False

        self.governor = Governor()
        super().set_title("Governor")

        self.preferences_page = Adw.PreferencesPage()
        self.preferences_group = Adw.PreferencesGroup()

        if self.governor.utility_found():
            self.label = Gtk.Label()
            self.label.set_text(" Performance mode will continuously run your CPU at higher frequencies.\nYou can change this back later.")
            self.preferences_group.add(self.label)

            self.performance_switch = Adw.SwitchRow()
            self.performance_switch.set_title('Use performance governor')
            self.performance_switch.set_active(self.rtcqs.status[self.check_name])
            self.performance_switch.connect("notify::active", self.on_switch_changed)
            self.switch_guard = False # blocks recursion

            self.preferences_group.add(self.performance_switch)

        else:
            self.error_label = Gtk.Label()
            self.error_label.set_text("cpupower utility not found")
            self.preferences_group.add(self.error_label)

        self.preferences_page.add(self.preferences_group)
        super().add(self.preferences_page)

    def on_switch_changed(self, switch, _):
        if self.switch_guard:
            self.switch_guard = False
            return

        if switch.get_active():
            ok = self.governor.set_performance()
            if not ok:
                self.switch_guard = True
                switch.set_active(False)
        else:
            ok = self.governor.set_powersave()
            if not ok:
                self.switch_guard = True
                switch.set_active(True)
        self.updated.emit()

    # abstract
    def refresh(self):
        self.switch_guard = True
        self.performance_switch.set_active(self.rtcqs.status[self.check_name])
