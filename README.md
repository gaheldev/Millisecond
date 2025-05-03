# Millisecond

- [ ] desc
- [ ] cite rtcqs
- [ ] linuxaudio

# Installation
## Flatpak 

<!-- ### From Flathub (recommended) -->

### From github release

Download flatpak archive (TODO) and run:
```bash
# add flathub
flatpak remote-add --if-not-exists --user flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install io.github.gaheldev.Millisecond.flatpak
```

## Direct compilation/installation

You'll need to install dev dependencies first (TODO) then run:
```
git clone TODO
cd millisecond
meson setup build/
meson install -C build/
```

