// Standalone GTK process: GTK can't run inside GNOME Shell, so the extension
// spawns this to show a file chooser. Prints the chosen path; prints nothing if
// cancelled. Overwrite confirmation is part of the chooser.
//
// Usage: gjs -m saveDialog.js SUGGESTED_NAME

import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import Gtk from 'gi://Gtk?version=4.0';
import System from 'system';

Gio._promisify(Gtk.FileDialog.prototype, 'save', 'save_finish');

Gtk.init();

const dialog = new Gtk.FileDialog({
    title: 'Save Clipboard as..',
    initial_name: System.programArgs[0],
});
const pictures = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES);
if (pictures)
    dialog.initial_folder = Gio.File.new_for_path(pictures);

const loop = new GLib.MainLoop(null, false);
dialog.save(null, null)
    .then(file => print(file.get_path()))
    .catch(e => {
        if (!e.matches(Gtk.DialogError, Gtk.DialogError.DISMISSED))
            printerr(e.message);
    })
    .finally(() => loop.quit());
loop.run();
