.PHONY: install run uninstall setup-deb deb compile test-deb release


all: install run


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


compile:
	meson compile -C build


VERSION := $(shell ./version)


release: 
	@echo "current version is: $(VERSION)"
	@read -p "new version: " new_version; \
		echo $$new_version > NEW_VERSION
	@make setup-deb
	@echo ====================================
	@git status
	@echo ====================================
	@git add -p
	@git commit -m "Bump version to $$(cat NEW_VERSION)"
	@git tag v$$(cat NEW_VERSION)
	@rm NEW_VERSION


setup-deb: compile
	# potentially need to reconfigure
	dh_make --createorig -c gpl3 -s -p millisecond_$(VERSION) || echo "continue anyway"
	dh_auto_configure --buildsystem=meson
	dch -b --newversion "$(VERSION)-1" "Automated release of $(VERSION)"
	nvim debian/changelog


deb: setup-deb
	# actually build
	dpkg-buildpackage -rfakeroot -us -uc
	# move deb files from parent directory to build-aux/deb/
	mkdir -p build-aux/deb/$(VERSION)/
	# xargs magic to move deb files (makefile doesn't get bash regex)
	ls ../ | grep millisecond_$(VERSION) | xargs -I % mv ../% build-aux/deb/$(VERSION)/


test-deb:
	cd test/deb/ && ./test-all-distros ../../build-aux/deb/$(VERSION)/millisecond_$(VERSION)-1_amd64.deb
