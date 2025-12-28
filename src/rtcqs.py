#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2021 Jeremy Jongepier
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import getpass
import re
import gzip
import resource


class Rtcqs:
    def __init__(self):
        self.user = getpass.getuser()
        self.wiki_url = "https://wiki.linuxaudio.org/wiki/system_configuration"
        self.gui_status = False
        self.version = "0.6.6"
        self.headline = {}
        self.kernel = {}
        self.output = {}
        self.status = {}

    def print_cli(self, message):
        if not self.gui_status:
            print(message)

    def print_version(self):
        self.print_cli(f"rtcqs - version {self.version}")
        self.print_cli("")

    def print_status(self, check):
        if not self.gui_status:
            if self.status[check]:
                print("[ \033[32mOK\033[00m ] ", end="")
            else:
                print("[ \033[31mWARNING\033[00m ] ", end="")

    def format_output(self, check):
        char_count = int(len(self.headline[check]))
        self.print_cli(self.headline[check])
        self.print_cli(char_count * "=")
        self.print_status(check)
        self.print_cli(self.output[check])
        self.print_cli("")

    def root_check(self):
        check = "root"
        self.headline[check] = "Root User"

        if self.user == "root":
            self.status[check] = False
            self.output[check] = "You are running this script as root. " \
                "Please run it as a regular user for the most reliable "\
                "results."

        else:
            self.status[check] = True
            self.output[check] = "Not running as root."

        self.format_output(check)

    def audio_group_check(self):
        check = "audio_group"
        self.headline[check] = "Group Limits"
        wiki_anchor = "#audio_group"
        limit_rtprio = resource.getrlimit(resource.RLIMIT_RTPRIO)[1]
        limit_memlock = resource.getrlimit(resource.RLIMIT_MEMLOCK)[1]

        if limit_rtprio >= 75 and limit_memlock == -1:
            self.status[check] = True
            self.output[check] = f"User {self.user} is member of a group " \
                                 "that has sufficient rtprio " \
                                 f"({limit_rtprio}) and memlock (unlimited) " \
                                 "limits set."
        else:
            self.status[check] = False
            self.output[check] = f"User {self.user} is currently not member " \
                                 "of a group that has sufficient rtprio " \
                                 f"({limit_rtprio}) and memlock " \
                                 f"({limit_memlock}) set. Add yourself to a " \
                                 "group with sufficent limits set, i.e. " \
                                 "audio or realtime, with 'sudo usermod -a " \
                                 f"-G <group_name> {self.user}. See also " \
                                 f"{self.wiki_url}{wiki_anchor}"

        self.format_output(check)

    def governor_check(self):
        check = "governor"
        self.headline[check] = "CPU Frequency Scaling"
        wiki_anchor = "#cpu_frequency_scaling"
        cpu_count = os.cpu_count()
        cpu_dir = "/sys/devices/system/cpu"
        cpu_list = []
        cpu_governor = {}
        bad_governor = 0

        if os.path.exists("/sys/devices/system/cpu/smt/active"):
            with open("/sys/devices/system/cpu/smt/active", "r") as f:
                self.cpu_smt = int(f.readline().strip())

        for cpu_nr in range(cpu_count):
            governor_path = f"{cpu_dir}/cpu{cpu_nr}/cpufreq/scaling_governor"

            try:
                with open(governor_path, "r") as f:
                    cpu_governor[cpu_nr] = f.readline().strip()
                    cpu_list.append(f"CPU {cpu_nr}: {cpu_governor[cpu_nr]}")
            except OSError as e:
                if e.errno == 16 and self.cpu_smt == 0:
                    pass

        for value in cpu_governor.values():
            if value != "performance":
                bad_governor += 1

        if bad_governor > 0:
            self.status[check] = False
            self.output[check] = "The scaling governor of one or more CPUs " \
                "is not set to 'performance'. You can set the scaling " \
                "governor to 'performance' with 'cpupower frequency-set " \
                "-g performance' or 'cpufreq-set -r -g performance' " \
                f"(Debian/Ubuntu). See also {self.wiki_url}{wiki_anchor}"
        else:
            self.status[check] = True
            self.output[check] = "The scaling governor of all CPUs is set " \
                "to performance."

        self.format_output(check)

    def smt_check(self):
        check = "smt"
        self.headline[check] = "Simultaneous Multithreading"
        wiki_anchor = "#simultaneous_multithreading"

        if self.cpu_smt != 0:
            self.status[check] = False
            self.output[check] = "Simultaneous Multithreading (SMT, also " \
                "called hyper-threading) is enabled. This can cause spikes " \
                "in DSP load at higher DSP loads. Consider disabling SMT " \
                "when experiencing such spikes with 'echo off | sudo tee " \
                "/sys/devices/system/cpu/smt/control'. See also " \
                f"{self.wiki_url}{wiki_anchor}"
        else:
            self.status[check] = True
            self.output[check] = "Simultaneous Multithreading (SMT, also " \
                "called hyper-threading) is disabled."

        self.format_output(check)


    def get_kernel_config_path(self) -> str:
        kernel_release = self.kernel['release']
        possible_paths = [
            "/proc/config.gz",
            f"/boot/config-{kernel_release}" + k.kernelRelease,
            f"/usr/src/linux-{kernel_release}/.config",
            "/usr/src/linux/.config",
            f"/usr/lib/modules/{kernel_release}/config",
            f"/usr/lib/ostree-boot/config-{kernel_release}",
            f"/usr/lib/kernel/config-{kernel_release}",
            f"/usr/src/linux-headers-{kernel_release}/.config",
            f"/lib/modules/{kernel_release}/build/.config",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return ""


    def kernel_config_check(self):
        check = "kernel_config"
        self.headline[check] = "Kernel Configuration"
        self.kernel["release"] = os.uname().release

        with open("/proc/cmdline", "r") as f:
            self.kernel["cmdline"] = f.readline().strip().split()

        self.status[check] = False
        self.output[check] = "Could not find kernel configuration."

        kernel_config_path = self.get_kernel_config_path()
        if kernel_config_path:
            self.status[check] = True
            self.output[check] = "Valid kernel configuration found."

            if kernel_config_path.endswith('.gz'):
                with gzip.open(kernel_config_path, "r") as f:
                    self.kernel["config"] = [
                        line.strip().decode() for line in f.readlines()]
            else:
                with open(kernel_config_path, "r") as f:
                    self.kernel["config"] = [
                        line.strip() for line in f.readlines()]

        self.format_output(check)


    def high_res_timers_check(self):
        check = "high_res_timers"
        self.headline[check] = "High Resolution Timers"
        wiki_anchor = "#installing_a_real-time_kernel"

        if "CONFIG_HIGH_RES_TIMERS=y" not in self.kernel["config"]:
            self.status[check] = False
            self.output[check] = "High resolution timers are not " \
                "enabled. Try enabling high-resolution timers " \
                "(CONFIG_HIGH_RES_TIMERS) under 'Processor type and " \
                f"features'). See also: {self.wiki_url}{wiki_anchor}"
        else:
            self.status[check] = True
            self.output[check] = "High resolution timers are enabled."

        self.format_output(check)

    def tickless_check(self):
        check = "tickless"
        self.headline[check] = "Tickless Kernel"
        wiki_anchor = "#installing_a_real-time_kernel"
        conf_nohz_list = [
            "CONFIG_NO_HZ=y",
            "CONFIG_NO_HZ_IDLE=y",
            "CONFIG_NO_HZ_COMMON=y",
            "CONFIG_NO_HZ_FULL=y"]

        conf_nohz_match = [
            match for match in conf_nohz_list if match in
            self.kernel["config"]]

        if int(len(conf_nohz_match)) > 0 or \
                os.path.exists("/sys/devices/system/cpu/nohz_full"):
            self.status[check] = True
            self.output[check] = "System is using a tickless kernel."
        else:
            self.status[check] = False
            self.output[check] = "Tickless timer support is not set. Try " \
                "enabling tickless timer support (CONFIG_NO_HZ_IDLE, or " \
                "CONFIG_NO_HZ in older kernels). See also " \
                f"{self.wiki_url}{wiki_anchor}"

        self.format_output(check)

    def preempt_rt_check(self):
        check = "preempt_rt"
        self.headline[check] = "Preempt RT"
        wiki_anchor = "#do_i_really_need_a_real-time_kernel"
        threadirqs = preempt = False

        if "threadirqs" in self.kernel["cmdline"]:
            threadirqs = True

        if "CONFIG_PREEMPT_RT=y" in self.kernel["config"] or \
                "CONFIG_PREEMPT_RT_FULL=y" in self.kernel["config"] or \
                "preempt=full" in self.kernel["cmdline"]:
            preempt = True

        if not threadirqs and not preempt:
            self.status[check] = False
            self.output[check] = f"Kernel {self.kernel['release']} without " \
                "'threadirqs' parameter or real-time capabilities found. " \
                f"See also {self.wiki_url}{wiki_anchor}"
        elif threadirqs:
            self.status[check] = True
            self.output[check] = f"Kernel {self.kernel['release']} is using " \
                "threaded IRQs."
        elif preempt:
            self.status[check] = True
            self.output[check] = f"Kernel {self.kernel['release']} is a " \
                "real-time kernel."

        self.format_output(check)

    def mitigations_check(self):
        check = "mitigations"
        self.headline[check] = "Spectre/Meltdown Mitigations"
        wiki_anchor = "#disabling_spectre_and_meltdown_mitigations"

        if "mitigations=off" not in self.kernel["cmdline"]:
            self.status[check] = False
            self.output[check] = "Kernel with Spectre/Meltdown mitigations " \
                "found. This could have a negative impact on the " \
                "performance of your system. " \
                "Disabling mitigations compromises your computer's security. " \
                "Only consider it for fully offline systems. See also " \
                f"{self.wiki_url}{wiki_anchor}"
        else:
            self.status[check] = True
            self.output[check] = "Spectre/Meltdown mitigations are " \
                "disabled. Be warned that this makes your system more " \
                "vulnerable to Spectre/Meltdown attacks."

        self.format_output(check)

    def rt_prio_check(self):
        check = "rt_prio"
        self.headline[check] = "RT Priorities"
        wiki_anchor = "#limitsconfaudioconf"
        param = os.sched_param(80)
        sched = os.SCHED_FIFO

        try:
            os.sched_setscheduler(0, sched, param)
        except PermissionError as e:
            self.status[check] = False
            self.output[check] = "Could not assign a 80 rtprio SCHED_FIFO " \
                f"value due to the following error: {e}. Set up " \
                f"limits.conf. See also {self.wiki_url}{wiki_anchor}"
        else:
            self.status[check] = True
            self.output[check] = "Realtime priorities can be set."

        self.format_output(check)

    def swappiness_check(self):
        check = "swappiness"
        self.headline[check] = "Swappiness"
        wiki_anchor = "#sysctlconf"

        with open("/proc/swaps", "r") as f:
            lines = f.readlines()

        if len(lines) < 2:
            swap = False
            self.status[check] = True
            self.output[check] = "Your system is configured without swap, " \
                "setting swappiness does not apply."
        else:
            swap = True

        if swap:
            with open("/proc/sys/vm/swappiness", "r") as f:
                swappiness = int(f.readline().strip())

            if swappiness > 10:
                self.status[check] = False
                self.output[check] = f"vm.swappiness is set to {swappiness} " \
                    "which is too high. Set swappiness to a lower value by " \
                    "adding 'vm.swappiness=10' to /etc/sysctl.conf and run " \
                    f"'sysctl --system'. See also {self.wiki_url}{wiki_anchor}"
            else:
                self.status[check] = True
                self.output[check] = f"Swappiness is set at {swappiness}."

        self.format_output(check)

    def filesystems_check(self):
        check = "filesystems"
        self.headline[check] = "Filesystems"
        wiki_anchor = "#filesystems"
        good_fs = ["ext4", "xfs", "zfs", "btrfs"]
        bad_fs = ["fuse", "reiserfs", "nfs", "cifs"]
        bad_mounts = ["/boot"]
        ignore_mounts = ["/run"]
        good_mounts_list = []
        bad_mounts_list = []

        with open("/proc/mounts", "r") as f:
            mounts = [line.split() for line in f.readlines()]

        for mount in mounts:
            mount_split = mount[2].split(".")[0]
            mount_point = mount[1]
            mount_top_dir = f"/{mount_point.split('/')[1]}"
            if mount_split in good_fs and mount_point not in bad_mounts:
                good_mounts_list.append(mount_point)
            elif (mount_split in bad_fs or mount_point in bad_mounts) and \
                    mount_top_dir not in ignore_mounts:
                bad_mounts_list.append(mount_point)

        self.print_cli(self.headline[check])
        self.print_cli("===========")

        if len(good_mounts_list) > 0:
            good_mounts = ", ".join(good_mounts_list)
            self.status[check] = True
            self.output[check] = "The following mounts can be used for " \
                f"audio purposes: {good_mounts}"
            self.print_status('filesystems')
            self.print_cli(self.output['filesystems'])

        if len(bad_mounts_list) > 0:
            bad_mounts = ', '.join(bad_mounts_list)
            self.status[check] = False
            self.output[check] = "The following mounts should be avoided " \
                f"for audio purposes: {bad_mounts}. See also " \
                f"{self.wiki_url}{wiki_anchor}"
            self.print_status(check)
            self.print_cli(self.output[check])

        self.print_cli("")

    def irq_check(self):
        check = "irqs"
        self.headline[check] = "IRQs"
        bad_irq_list = []
        good_irq_list = []
        snd_list = ["audiodsp", "snd_.*"]
        snd_re = "|".join(snd_list)
        usb_re = "[e,u,x]hci_hcd"
        snd_compiled_re = re.compile(snd_re)
        usb_compiled_re = re.compile(usb_re)
        output_irq = {}
        irq_path = "/sys/kernel/irq"
        irq_path_list = os.listdir(irq_path)

        for irq in irq_path_list:
            with open(f"{irq_path}/{irq}/actions", "r") as f:
                devices = f.readline().strip()

            device_list = devices.split(", ")

            if snd_compiled_re.search(devices):
                if len(device_list) > 1:
                    bad_irq_list.append(irq)
                    self.status["snd_irqs"] = False
                    output_irq[irq] = f"Soundcard {device_list[0]} with IRQ " \
                        f"{irq} shares its IRQ with the following other " \
                        f"devices {devices}"
                else:
                    good_irq_list.append(irq)
                    self.status["snd_irqs"] = True
                    output_irq[irq] = f"Soundcard {device_list[0]} with IRQ " \
                        f"{irq} does not share its IRQ."
            if usb_compiled_re.search(devices):
                if len(device_list) > 1:
                    bad_irq_list.append(irq)
                    self.status["usb_irqs"] = False
                    output_irq[irq] = f"Found USB port {device_list[0]} " \
                        f"with IRQ {irq} that shares its IRQ with the " \
                        f"following other devices: {devices}"
                else:
                    good_irq_list.append(irq)
                    self.status["usb_irqs"] = True
                    output_irq[irq] = f"USB port {device_list[0]} with IRQ " \
                        f"{irq} does not share its IRQ."

        self.print_cli(self.headline[check])
        self.print_cli("====")

        if len(good_irq_list) > 0:
            self.status[check] = True
            self.output[check] = "\n".join(
                [output_irq[good_irq] for good_irq in good_irq_list])

            for good_irq in good_irq_list:
                self.print_status(check)
                self.print_cli(output_irq[good_irq])

        if len(bad_irq_list) > 0:
            self.status[check] = False
            self.output[check] = "\n".join(
                [output_irq[bad_irq] for bad_irq in bad_irq_list])

            for bad_irq in bad_irq_list:
                self.print_status(check)
                self.print_cli(output_irq[bad_irq])

        self.print_cli("")

    def power_management_check(self):
        check = "power_management"
        self.headline[check] = "Power Management"
        wiki_anchor = "#quality_of_service_interface"

        if os.access("/dev/cpu_dma_latency", os.W_OK):
            self.status[check] = True
            self.output[check] = "Power management can be controlled from " \
                "user space. This enables DAWs like Ardour and Reaper to " \
                "set CPU DMA latency which could help prevent xruns."
        else:
            self.status[check] = False
            self.output[check] = "Power management can't be controlled from " \
                "user space, the device node /dev/cpu_dma_latency can't be " \
                "accessed by your user. This prohibits DAWs like Ardour and " \
                "Reaper to set CPU DMA latency which could help prevent " \
                "xruns. For enabling access see " \
                f"{self.wiki_url}{wiki_anchor}"

        self.format_output(check)

    def main(self):
        self.print_version()
        self.root_check()
        self.audio_group_check()
        self.governor_check()
        self.smt_check()
        self.kernel_config_check()
        if self.status["kernel_config"]:
            self.high_res_timers_check()
            self.tickless_check()
            self.preempt_rt_check()
            self.mitigations_check()
        self.rt_prio_check()
        self.swappiness_check()
        self.filesystems_check()
        self.irq_check()
        self.power_management_check()


def main():
    app = Rtcqs()
    app.main()


if __name__ == "__main__":
    main()
