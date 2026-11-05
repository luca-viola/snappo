UUID := snappo@lviola
SRC := $(UUID)
DEST := $(HOME)/.local/share/gnome-shell/extensions/$(UUID)

.PHONY: schemas install uninstall pack clean

schemas:
	glib-compile-schemas $(SRC)/schemas

install: schemas
	mkdir -p $(DEST)
	cp -r $(SRC)/. $(DEST)/

uninstall:
	rm -rf $(DEST)

pack: schemas
	mkdir -p dist  # gnome-extensions crashes if the directory is missing
	gnome-extensions pack --force --out-dir=dist \
		--extra-source=capture.js --extra-source=selector.js \
		--extra-source=snapshot.js --extra-source=ocr.js \
		--extra-source=saveDialog.js --extra-source=clearGaps.js \
		--extra-source=aboutDialog.js \
		--extra-source=indicator.js --extra-source=icons $(SRC)
	# gnome-extensions leaves out the compiled schema, without which Snappo can't load
	cd $(SRC) && zip -q ../dist/$(UUID).shell-extension.zip schemas/gschemas.compiled

clean:
	rm -rf dist $(SRC)/schemas/gschemas.compiled
