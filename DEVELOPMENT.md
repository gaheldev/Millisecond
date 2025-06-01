# Development

## Build

Install all dev dependencies, for example on Ubuntu:
```bash
sudo apt install meson ninja-build build-essential
sudo apt install python3-all
sudo apt install libgtk-4-dev libadwaita-1-dev python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 adwaita-icon-theme
sudo apt install devscripts debhelper dh-make dh-python
sudo apt install flatpak flatpak-builder
```

### Flatpak

#### Using Gnome-Builder

Install [gnome-builder](https://flathub.org/apps/org.gnome.Builder)

```bash
# add flathub
flatpak remote-add --if-not-exists --user flathub https://dl.flathub.org/repo/flathub.flatpakrepo
# may have to manually install sdk 48 if not working from builder
flatpak install org.gnome.Sdk/x86_64/48
```

#### From CLI
```bash
sudo apt install flatpak flatpak-builder
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install org.gnome.Sdk/x86_64/48
make flatpak
```

Install and run the built flatpak
```bash
flatpak install build-aux/flatpak/release/<version>/Millisecond.flatpak
flatpak run io.github.gaheldev.Millisecond
```

### Direct installation

```bash
meson setup build/ # required the first time
meson install -C build/
```

You can now run millisecond from your app launcher or from the terminal using:
```bash
millisecond
```

### Deb

#### First initialization

```bash
sudo apt-get install debhelper build-essential dh-make dh-python
meson setup build/
make deb
```

#### updates

If necessary, complete the debian/control file with required info and dependencies then build the deb again.

```bash
make deb
```

#### test

Install [docker](https://docs.docker.com/engine/install/) for testing and the following dependencies:

```bash
make test-deb
```

## TODO
### GUI
- [ ] icons
- [ ] update metainfo theme when icon is ready
- [ ] make flatpak distributable
    - [x] bump flatpak version and changelog
    - [x] set up basic export
    - [x] properly require runner / system dependencies
    - [ ] setup for flathub

- [ ] use homemade dimmed for older gnome versions
- [ ] warning or error depending on importance of diagnostic

### rtfix
- [ ] autofix
    - [ ] setup tests
    - [ ] implement and test dma latency: find group with correct rtprio and memlock
    - [ ] audio group
    - [ ] preempt=full

### Flatpak
- [x] Need access to system to perform checks (see [sandbox permissions](https://docs.flatpak.org/en/latest/sandbox-permissions.html))
- [ ] Fix filesystem check in flatpak
- [ ] Fix /proc access?

### Issues
- [ ] referencing pkexec problem on at least ubuntu 24.10 (pkexec hangs, for example `pkexec gedit`)
