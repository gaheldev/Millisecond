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

import re
import resource
import subprocess

from gi.repository import Adw, Gtk, GObject

from .utils import is_flatpak, run_cmd, cmd_exists, dir_exists



def autofix(cls):
    """Decorator to enforce autofix dialog implements required properties and methods"""
    if not callable(getattr(cls, 'refresh')):
        raise TypeError(f"{cls.__name__} must implement a callable method 'refresh'")

    signals = ["updated", "fixed", "fixing"]
    for signal in signals:
        if not hasattr(cls, signal):
            raise TypeError(f"{cls.__name__} must implement a \"{signal}\" signal")

    # TODO: find a way to check for properties initilized in __init__
    properties = ["rtcqs", "check_name", "is_fix_permanent"]

    return cls

###############################################################################
# due to pygobject not supporting multiple inheritance we can't use abstract
# class to enforce some properties and methods
# @autofix decorator checks for required method and signals, but not for properties
# use the example below to create a new autofix dialog (can inherit from any kind of dialog)

@autofix # checks that required method and signals are implemented
class ExampleDialog(Adw.Dialog):
    __gtype_name__ = "ExampleDialog"

    # required signals
    updated = GObject.Signal('updated')
    fixed = GObject.Signal('fixed')
    fixing = GObject.Signal('fixing')

    def __init__(self, cqs, check_name, **kwargs) -> None:
        super().__init__(**kwargs)

        # required properties
        self.rtcqs = cqs
        self.check_name = check_name
        self.is_fix_permanent = True # if dialog can be shown again once fixed

        # implement the rest of init afterwards

    # required
    def refresh(self) -> None:
        ...

###############################################################################

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
        self.is_fix_permanent = True

        self.swap = Swappiness()
        super().set_heading("Set swappiness to 10?")
        super().set_body("This will modify /etc/sysctl.conf, changes are definitive.")

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
            self.performance_switch.set_title('Use performance governor')
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
