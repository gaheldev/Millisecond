# rtfix/governor.py
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

from .utils import run_cmd, cmd_exists
from .template import autofix


class Governor:
    def __init__(self) -> None:
        # FIXME: check for all possible utilities and use the best installed one?
        self.utility = "cpupower" if cmd_exists("cpupower") else None

    def utility_found(self) -> bool:
        return cmd_exists("cpupower")

    def set_performance(self) -> bool:
        cmd = ["pkexec", "bash", "-c" , "cpupower frequency-set -g performance"]
        return run_cmd(cmd).returncode == 0

    def set_powersave(self) -> bool:
        cmd = ["pkexec", "bash", "-c" , "cpupower frequency-set -g powersave"]
        return run_cmd(cmd).returncode == 0


@autofix
class GovernorDialog(Adw.PreferencesDialog):
    __gtype_name__ = "GovernorDialog"

    updated = GObject.Signal('updated')
    fixed = GObject.Signal('fixed')
    fixing = GObject.Signal('fixing')

    def __init__(self, cqs, check_name, **kwargs) -> None:
        super().__init__(**kwargs)

        self.rtcqs = cqs
        self.check_name = check_name
        self.is_fix_permanent = False

        self.governor = Governor()
        super().set_title("Governor")

        self.preferences_page = Adw.PreferencesPage()
        self.explanations_group = Adw.PreferencesGroup()
        self.preferences_group = Adw.PreferencesGroup()

        if self.governor.utility_found():
            self.label = Gtk.Label()
            self.label.set_text("Performance governor will use more power and generate more heat.\nWhen enabled, this overrides your desktop environment's governor.\n\nDisable it when you don't need it.")
            self.label.set_wrap(True)
            self.label.set_justify(Gtk.Justification.CENTER)
            self.explanations_group.add(self.label)

            self.performance_switch = Adw.SwitchRow()
            self.performance_switch.set_title('Use Performance Governor')
            self.performance_switch.set_subtitle('Continuously run CPU at high frequency')
            self.performance_switch.set_active(self.rtcqs.status[self.check_name])
            self.performance_switch.connect("notify::active", self.on_switch_changed)
            self.switch_guard = False # blocks recursion

            self.preferences_group.add(self.performance_switch)

        else:
            self.error_label = Gtk.Label()
            self.error_label.set_text("cpupower utility not found")
            self.preferences_group.add(self.error_label)

        self.preferences_page.add(self.explanations_group)
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

    def refresh(self):
        check_status = self.rtcqs.status[self.check_name]
        if self.performance_switch.get_active() != check_status:
            self.switch_guard = True
            self.performance_switch.set_active(check_status)
