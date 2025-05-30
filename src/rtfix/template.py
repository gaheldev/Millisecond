# rtfix/template.py
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

from gi.repository import Adw, GObject


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
