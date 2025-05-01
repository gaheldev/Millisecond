# proaudio-setup

## Flatpak

- [x] Need access to system to perform checks (see [sandbox permissions](https://docs.flatpak.org/en/latest/sandbox-permissions.html))
- [ ] Fix /proc access?

## Direct compilation/installation

```
meson setup build/
meson compile -C build/
meson install -C build/
```

