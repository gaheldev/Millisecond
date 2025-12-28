# Simple configuration: Musnix

 Adding [musnix](https://github.com/musnix/musnix/) to your configuration (possibly also as a flake) will result in most bottlenecks being resolved:

```nix
# /etc/nixos/configuration.nix
{
  imports =
    [ # ...
      /path/to/musnix/git-clone
    ];

  musnix.enable = true;
  users.users.<user_name>.extraGroups = [ "audio" ];
}
```

# Advanced configuration: Individual modules

In case you want to have more fine grained control over each setting being applied.

### Group Limits & RT Priorities

Add yourself to audio group in case you didn't already:
```nix
# /etc/nixos/configuration.nix
users.users.<user_name>.extraGroups = [ "audio" ];
```

Enable the limits of the audio group:
```nix
# /etc/nixos/configuration.nix
security.pam.loginLimits = [
      {
        domain = "@audio";
        item = "memlock";
        type = "-";
        value = "unlimited";
      }
      {
        domain = "@audio";
        item = "rtprio";
        type = "-";
        value = "99";
      }
      {
        domain = "@audio";
        item = "nofile";
        type = "soft";
        value = "99999";
      }
      {
        domain = "@audio";
        item = "nofile";
        type = "hard";
        value = "99999";
      }
    ];
```

### CPU Frequency Scaling

Set scaling governor to performance:

```nix
# /etc/nixos/configuration.nix
powerManagement.cpuFreqGovernor = "performance";
```

### Simultaneous Multithreading

Change this on the fly, to see if it actually makes a difference in your specifc application:
```bash
echo off | sudo tee /sys/devices/system/cpu/smt/control
```

Add it permanently:

```nix
# /etc/nixos/configuration.nix
boot.kernelParams = [ 
  "nosmt"
];
```

### Power Management

Add the following udev rule:
```nix
# /etc/nixos/configuration.nix
services.udev = {
      extraRules = ''
        KERNEL=="rtc0", GROUP="audio"
        KERNEL=="hpet", GROUP="audio"
        DEVPATH=="/devices/virtual/misc/cpu_dma_latency", OWNER="root", GROUP="audio", MODE="0660"
      '';
    };
```

### Kernel

Use any real-time capable kernel, i.e. zen comes with `PREEMPT_RT` or consult the [wiki](https://wiki.linuxaudio.org/wiki/system_configuration#installing_a_real-time_kernel) for a good choice:

 ```nix
# /etc/nixos/configuration.nix
boot.kernelPackages = pkgs.linuxPackages_zen; 
```

### Swappiness

Only applies if you have swap defined in `/etc/nixos/hardware-configuration.nix`. Then you may apply:

 ```nix
# /etc/nixos/configuration.nix
boot = {
      kernel.sysctl = {
        "vm.swappiness" = 10;
      };
      kernelParams = [ "threadirqs" ];
    };
```

