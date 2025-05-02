# proaudio-setup

- [ ] Credit rtcqs
    - [ ] in README + current version
    - [ ] in app
- [ ] link to full doc
- [x] expanding row with:
    - [x] check emoji
    - [x] Title from rtcqs
    - [ ] Subtitle ?
    - [x] autofix button if autofix implemented
    - [x] info emoji for doc
    - [x] expandable area with rtcqs output
- [x] group by importance? by type?
- [x] only close button
- [ ] autofix
    - [ ] audio group
    - [ ] preempt=full

## Flatpak

- [x] Need access to system to perform checks (see [sandbox permissions](https://docs.flatpak.org/en/latest/sandbox-permissions.html))
- [ ] Fix /proc access?

## Direct compilation/installation

```
meson setup build/
meson compile -C build/
meson install -C build/
```

