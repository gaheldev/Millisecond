# rtfix/hyperthreading.py
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

from gi.repository import Adw, Gtk, GObject

from .utils import run_cmd, file_exists
from .template import autofix


class Hyperthreading:
    def __init__(self) -> None:
        self.control_file = "/sys/devices/system/cpu/smt/control"

    def exists(self) -> bool:
        return file_exists(self.control_file)

    def enable(self) -> bool:
        cmd = ["pkexec", "bash", "-c" , f"echo on | sudo tee {self.control_file}"]
        return run_cmd(cmd).returncode == 0

    def disable(self) -> bool:
        cmd = ["pkexec", "bash", "-c" , f"echo off | sudo tee {self.control_file}"]
        return run_cmd(cmd).returncode == 0


@autofix
class HyperthreadingDialog(Adw.PreferencesDialog):
    __gtype_name__ = "HyperthreadingDialog"

    updated = GObject.Signal('updated')
    fixed = GObject.Signal('fixed')
    fixing = GObject.Signal('fixing')

    def __init__(self, cqs, check_name, **kwargs) -> None:
        super().__init__(**kwargs)

        self.rtcqs = cqs
        self.check_name = check_name
        self.is_fix_permanent = False

        self.hyperthreading = Hyperthreading()
        super().set_title("Hyperthreading")

        self.preferences_page = Adw.PreferencesPage()
        self.explanations_group = Adw.PreferencesGroup()
        self.preferences_group = Adw.PreferencesGroup()

        if self.hyperthreading.exists():
            self.label = Gtk.Label()
            self.label.set_text("This will likely reduce overall performance of your system.\nKeep it enabled if you don't need it.")
            self.label.set_wrap(True)
            self.label.set_justify(Gtk.Justification.CENTER)
            self.explanations_group.add(self.label)

            self.switch = Adw.SwitchRow()
            self.switch.set_title('Disable Hyperthreading')
            self.switch.set_active(self.rtcqs.status[self.check_name])
            self.switch.connect("notify::active", self.on_switch_changed)
            self.switch_guard = False # blocks recursion

            self.preferences_group.add(self.switch)

        else:
            self.error_label = Gtk.Label()
            self.error_label.set_text("Couldn't find hyperthreading control")
            self.preferences_group.add(self.error_label)

        self.preferences_page.add(self.explanations_group)
        self.preferences_page.add(self.preferences_group)
        super().add(self.preferences_page)

    def on_switch_changed(self, switch, _):
        if self.switch_guard:
            self.switch_guard = False
            return

        if switch.get_active():
            ok = self.hyperthreading.disable()
            if not ok:
                self.switch_guard = True
                switch.set_active(False)
        else:
            ok = self.hyperthreading.enable()
            if not ok:
                self.switch_guard = True
                switch.set_active(True)
        self.updated.emit()

    def refresh(self):
        check_status = self.rtcqs.status[self.check_name]
        if self.switch.get_active() != check_status:
            self.switch_guard = True
            self.switch.set_active(check_status)
