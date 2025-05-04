.PHONY: install run uninstall

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
