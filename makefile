.PHONY: install run uninstall deb compile

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

# TODO: handle version number
deb: compile
	# potentially need to reconfigure
	dh_make --createorig -s -p millisecond_0.1.0 || echo "continue anyway"
	dh_auto_configure --buildsystem=meson
	# # actually build
	dpkg-buildpackage -rfakeroot -us -uc

	mkdir -p build-aux/deb/
	# xargs magic to move deb files (makefile doesn't get bash regex)
	ls ../ | grep millisecond_0.1.0 | xargs -I % mv ../% build-aux/deb/
