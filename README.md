<h1 align='center'>
Millisecond
</h1>

<p align='center'>
<img src=https://raw.githubusercontent.com/gaheldev/Millisecond/refs/heads/main/data/icons/hicolor/scalable/apps/io.github.gaheldev.Millisecond.svg>
</p>

<p align='center'>
Optimize your system for low latency audio.
</p>

<br/>

<div align="center">
<a href=https://github.com/gaheldev/Millisecond/releases/latest alt="Latest release">
	<img src=https://img.shields.io/github/v/release/gaheldev/Millisecond>
</a>
</div>

![image](https://github.com/user-attachments/assets/fa0408b3-013e-4aaf-a587-cfe90938f9bd)


Millisecond is a gtk app based on [rtcqs](https://codeberg.org/rtcqs/rtcqs). \
It provides system diagnostics and offers tips to improve low latency performance for audio production, with links to detailed documentation from [linuxaudio wiki](https://wiki.linuxaudio.org/wiki/system_configuration).

In future releases, I intend to allow running fixes from the app whenever possible.


# 🛠️ Installation

>[!NOTE]
> flatpak is recommended although some minor functionnalities may not be available in the flatpak release

<a href="https://flathub.org/apps/details/io.github.gaheldev.Millisecond"><img src="https://flathub.org/assets/badges/flathub-badge-en.png" width="300"/></a>

### From repositories

[![Packaging status](https://repology.org/badge/vertical-allrepos/millisecond.svg)](https://repology.org/project/millisecond/versions)

### From package releases
Install the [latest](https://github.com/gaheldev/Millisecond/releases/latest) deb (Ubuntu >= 24.04) or flatpak release. \
If you need to install flatpak on your system, follow [flathub's instructions](https://flathub.org/setup).

### Manual installation

You'll need to install dev dependencies first, for reference on Ubuntu:
```bash
sudo apt install meson ninja-build build-essential
sudo apt install python3-all
sudo apt install libgtk-4-dev libadwaita-1-dev python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 adwaita-icon-theme
```

Then clone the repo and install:

```bash
git clone https://github.com/gaheldev/Millisecond.git
cd millisecond
meson setup build/
meson install -C build/
```

# 🧑‍🤝‍🧑 Contributions
Please open issues or submit a pull request if something doesn't work.\
Modifications to the `rtcqs.py` script should preferably be submitted upstream to [rtcqs](https://codeberg.org/rtcqs/rtcqs). 

### Acknowledgements
- icons by [Jakub Steiner](https://github.com/jimmac)
- NixOS doc by [@backtail](https://github.com/backtail)
