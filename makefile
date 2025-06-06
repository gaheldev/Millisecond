.PHONY: install run uninstall setup-deb deb bump-deb setup compile test-deb release


all: setup compile install run


run: 
	millisecond


install:
	meson install -C build


uninstall:
	sudo rm /usr/local/share/metainfo/io.github.gaheldev.Millisecond.metainfo.xml
	sudo rm /usr/local/share/glib-2.0/schemas/io.github.gaheldev.Millisecond.gschema.xml
	sudo rm /usr/local/share/applications/io.github.gaheldev.Millisecond.desktop
	sudo rm -rf /usr/local/share/millisecond/
	sudo rm /usr/local/share/dbus-1/services/io.github.gaheldev.Millisecond.service
	sudo rm /usr/local/bin/millisecond


setup:
	meson setup --reconfigure build


compile:
	meson compile -C build


VERSION := $(shell ./version)


release: 
	@echo "current version is: $(VERSION)"
	@read -p "new version: " new_version; \
		echo $$new_version > NEW_VERSION
	@make bump-deb
	@echo ====================================
	@git status
	@echo ====================================
	@git add -p
	@git commit -m "Bump version to $$(cat NEW_VERSION)"
	@git commit --amend
	@git tag v$$(cat NEW_VERSION)
	@rm NEW_VERSION


setup-deb: compile
	# potentially need to reconfigure
	dh_make -y --createorig -c gpl3 -s -p millisecond_$(VERSION) || echo "continue anyway"
	dh_auto_configure --buildsystem=meson
	dch -b --newversion "$(VERSION)" "Automated release of $(VERSION)"
	nvim debian/changelog


bump-deb:
	nvim data/io.github.gaheldev.Millisecond.metainfo.xml.in
	dch -b --newversion "$(VERSION)" "Automated release of $(VERSION)"
	nvim debian/changelog
	# actually build
	dpkg-buildpackage -rfakeroot -us -uc
	# move deb files from parent directory to build-aux/deb/
	mkdir -p build-aux/deb/$(VERSION)/
	# xargs magic to move deb files (makefile doesn't get bash regex)
	ls ../ | grep millisecond_$(VERSION) | xargs -I % mv ../% build-aux/deb/$(VERSION)/

deb:
	# actually build
	dpkg-buildpackage -rfakeroot -us -uc
	# move deb files from parent directory to build-aux/deb/
	mkdir -p build-aux/deb/$(VERSION)/
	# xargs magic to move deb files (makefile doesn't get bash regex)
	ls ../ | grep millisecond_$(VERSION) | xargs -I % mv ../% build-aux/deb/$(VERSION)/


test-deb:
	cd test/deb/ && ./test-all-distros ../../build-aux/deb/$(VERSION)/millisecond_$(VERSION)_amd64.deb


flatpak:
	mkdir -p build-aux/flatpak/build/$(VERSION)
	mkdir -p build-aux/flatpak/release/$(VERSION)
	mkdir -p build-aux/flatpak/tmp-repo
	flatpak-builder --user --repo=build-aux/flatpak/tmp-repo --force-clean --install-deps-from=flathub build-aux/flatpak/build/$(VERSION) io.github.gaheldev.Millisecond.json
	flatpak build-bundle build-aux/flatpak/tmp-repo build-aux/flatpak/release/$(VERSION)/Millisecond.flatpak io.github.gaheldev.Millisecond --runtime-repo=https://flathub.org/repo/flathub.flatpakrepo
	rm -r .flatpak-builder
