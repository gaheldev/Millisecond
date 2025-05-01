# proaudio-setup

- [ ] Credit rtcqs
    - [ ] in README + current version
    - [ ] in app
- [ ] link to full doc
- [ ] expanding row with:
    - [ ] check emoji
    - [ ] Title from rtcqs
    - [ ] Subtitle ?
    - [ ] autofix button if autofix implemented
    - [ ] info emoji for doc
    - [ ] expandable area with rtcqs output
- [ ] group by importance? by type?
- [ ] only close button
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

