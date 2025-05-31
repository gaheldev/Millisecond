# rtfix/dma_latency.py
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


class DMALatency:
    def __init__(self) -> None:
        self.conf_path = "/etc/security/limits.conf"
        self.udev_path = "/etc/udev/rules.d/99-cpu-dma-latency.millisecond.rules"
    
    def get_audio_group(self) -> str|None:
        """
        return name of group with rt priority if it exists
        (preferably audio, then realtime, then anything else)
        """
        # TODO
        return 'audio'

    def allow(self) -> None:
        audio_group = self.get_audio_group()
        if audio_group is None:
            print("Couldn't find audio group")
            return

        # escape \ and " once for python string so that " is escaped in echo
        udev_rule = "DEVPATH==\\\"/devices/virtual/misc/cpu_dma_latency\\\", OWNER=\\\"root\\\", GROUP=\\\"" + audio_group + "\\\", MODE=\\\"0660\\\""

        run_cmd(["pkexec", "bash", "-c" , "echo " + udev_rule + f" | tee {self.udev_path} && udevadm control --reload-rules && udevadm trigger"])



@autofix
class DMALatencyDialog(Adw.AlertDialog):
    __gtype_name__ = "DMALatencyDialog"

    updated = GObject.Signal('updated')
    fixed = GObject.Signal('fixed')
    fixing = GObject.Signal('fixing')

    def __init__(self, cqs, check_name, **kwargs) -> None:
        super().__init__(**kwargs)

        self.rtcqs = cqs
        self.check_name = check_name
        self.is_fix_permanent = True

        self.dma_latency = DMALatency()
        super().set_heading("CPU DMA Latency")
        super().set_body("Allow DAWs to set CPU DMA latency?\nChanges are definitive.")

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
        self.dma_latency.allow()
        self.fixed.emit()

    def refresh(self) -> None:
        ...
