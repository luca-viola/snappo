// The last grab. It lives in the private runtime directory, which is wiped at
// logout, and survives the extension being disabled when the screen locks.

import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import St from 'gi://St';

Gio._promisify(Gio.File.prototype, 'replace_contents_bytes_async', 'replace_contents_finish');
Gio._promisify(Gio.File.prototype, 'load_contents_async');
Gio._promisify(Gio.File.prototype, 'delete_async');

async function writeBytes(file, bytes) {
    await file.replace_contents_bytes_async(
        bytes, null, false, Gio.FileCreateFlags.REPLACE_DESTINATION, null);
}

export function setClipboardText(text) {
    St.Clipboard.get_default().set_text(St.ClipboardType.CLIPBOARD, text);
}

export class Snapshot {
    constructor() {
        const dir = GLib.build_filenamev([GLib.get_user_runtime_dir(), 'snappo']);
        GLib.mkdir_with_parents(dir, 0o700);
        this.path = GLib.build_filenamev([dir, 'snapshot.png']);
        this._file = Gio.File.new_for_path(this.path);
        this.exists = this._file.query_exists(null);
    }

    get uri() {
        return this._file.get_uri();
    }

    async store(bytes) {
        await writeBytes(this._file, bytes);
        this.exists = true;
        this._setClipboardImage(bytes);
    }

    async copyToClipboard() {
        this._setClipboardImage(await this._read());
    }

    async saveTo(path) {
        await writeBytes(Gio.File.new_for_path(path), await this._read());
    }

    async clear() {
        setClipboardText('');
        this.exists = false;
        try {
            await this._file.delete_async(GLib.PRIORITY_DEFAULT, null);
        } catch (e) {
            if (!e.matches(Gio.IOErrorEnum, Gio.IOErrorEnum.NOT_FOUND))
                throw e;
        }
    }

    async _read() {
        const [contents] = await this._file.load_contents_async(null);
        return new GLib.Bytes(contents);
    }

    _setClipboardImage(bytes) {
        St.Clipboard.get_default().set_content(St.ClipboardType.CLIPBOARD, 'image/png', bytes);
    }
}
