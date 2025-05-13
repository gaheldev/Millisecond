# Development

## Build
### Flatpak

Use [gnome-builder](https://flathub.org/apps/org.gnome.Builder)

```bash
# add flathub
flatpak remote-add --if-not-exists --user flathub https://dl.flathub.org/repo/flathub.flatpakrepo
# may have to manually install sdk 48 if not working from builder
flatpak install org.gnome.Sdk/x86_64/48
```

TODO: build from CLI

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
Install [docker](https://docs.docker.com/engine/install/) for testing and the following dependencies:

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

```bash
make test-deb
```

## TODO
### GUI
- [ ] contact rtcqs author

- [x] pick license (GPL by default, rtcqs is MIT)
- [ ] specify license in deb
- [ ] pick flatpak url
- [ ] fill metainfo in data/
- [ ] name
- [ ] icons
- [ ] make flatpak distributable
    - [x] set up basic export
    - [x] properly require runner / system dependencies
    - [ ] setup for flathub

- [ ] Readme
- [ ] Credit rtcqs
    - [ ] in README + current version
    - [x] in app

- [ ] use homemade dimmed for older gnome versions
- [x] refresh diagnostic on fix
- [x] refresh all button
- [x] refresh diagnostics on refresh all
- [ ] In-app explanations
- [ ] link to full doc
- [x] expanding row with:
    - [x] check emoji
    - [x] Title from rtcqs
    - [ ] Subtitle ?
    - [x] autofix button if autofix implemented
    - [x] info emoji for doc
    - [x] expandable area with rtcqs output
- [x] group by importance? by type?
- [ ] warning or error depending on importance of diagnostic
- [x] only close button
- [x] autofix

- [x] Handle case where kernel configuration is not found

### rtfix
- [ ] autofix
    - [ ] audio group
    - [ ] preempt=full
    - [x] swappiness `sysctl -p` to update
        - [ ] new ubuntu distributions (and others?) do not use /etc/sysctl.conf anymore: see [ubuntu discusion](https://bugs.launchpad.net/ubuntu/+source/systemd/+bug/2084376)
- [ ] tests
    - [ ] swappiness

### Flatpak
- [x] Need access to system to perform checks (see [sandbox permissions](https://docs.flatpak.org/en/latest/sandbox-permissions.html))
- [ ] Fix filesystem check in flatpak
- [ ] Fix /proc access?


