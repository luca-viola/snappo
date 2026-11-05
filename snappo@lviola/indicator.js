import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import GObject from 'gi://GObject';
import St from 'gi://St';

import * as BoxPointer from 'resource:///org/gnome/shell/ui/boxpointer.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as MessageTray from 'resource:///org/gnome/shell/ui/messageTray.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';
import {Flashspot} from 'resource:///org/gnome/shell/ui/screenshot.js';
import {Slider} from 'resource:///org/gnome/shell/ui/slider.js';

import {AboutDialog} from './aboutDialog.js';
import {areaTarget, desktopTarget, windowTarget} from './capture.js';
import {installCommand, recognize} from './ocr.js';
import {AreaSelector, WindowSelector} from './selector.js';
import {setClipboardText, Snapshot} from './snapshot.js';

const MAX_DELAY = 100; // seconds, matches the schema's range
const SETTLE_MS = 100; // lets the panel repaint so the shot shows no menu or countdown

Gio._promisify(Gio.Subprocess.prototype, 'communicate_utf8_async');

class GrabCancelled extends Error {}

export const SnappoIndicator = GObject.registerClass(
class SnappoIndicator extends PanelMenu.Button {
    _init(extension) {
        super._init(0.5, extension.metadata.name);

        this._extension = extension;
        this._settings = extension.getSettings();
        this._snapshot = new Snapshot();
        this._cancellable = new Gio.Cancellable();
        this._cameraIcon = this._gicon('camera.svg');
        this._busyIcon = this._gicon('hour_glass.svg');

        const box = new St.BoxLayout({style_class: 'panel-status-menu-box'});
        // Full-color art needs more room than the panel's 16px symbolic size.
        this._icon = new St.Icon({
            gicon: this._cameraIcon,
            style_class: 'system-status-icon',
            icon_size: 22,
        });
        this._countdownLabel = new St.Label({
            style_class: 'snappo-countdown',
            y_align: Clutter.ActorAlign.CENTER,
            visible: false,
        });
        box.add_child(this._icon);
        box.add_child(this._countdownLabel);
        this.add_child(box);

        this._buildMenu();
        this._syncSnapshotItems();

        this.connect('destroy', () => this._onDestroy());
    }

    _gicon(name) {
        return Gio.icon_new_for_string(`${this._extension.path}/icons/${name}`);
    }

    // Menu

    _buildMenu() {
        this._addItem('Grab Desktop..', () => this._grab(desktopTarget));
        this._monitorItems = new PopupMenu.PopupMenuSection();
        this.menu.addMenuItem(this._monitorItems);
        this._rebuildMonitorItems();
        Main.layoutManager.connectObject('monitors-changed',
            () => this._rebuildMonitorItems(), this);
        this._addItem('Grab Window..', () => this._grab(() => this._pickWindow()));
        this._addItem('Grab Area..', () => this._grab(() => this._pickArea()));

        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        this._buildDelayItems();

        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        this._clipboardItem = this._addImageItem('Clipboard..', 'action-unavailable-symbolic',
            () => this._showSnapshot());
        this._copyItem = this._addImageItem('Copy..', 'edit-copy-symbolic',
            () => this._copySnapshot());
        this._saveItem = this._addImageItem('Save as..', 'document-save-as-symbolic',
            () => this._saveSnapshot());
        this._clearItem = this._addImageItem('Clear..', 'edit-clear-symbolic',
            () => this._clearSnapshot());

        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        this._ocrItem = this._addItem('OCR', () => this._ocr());

        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        this._addItem('About..', () => this._showAbout());
    }

    _addItem(label, callback, menu = this.menu) {
        const item = new PopupMenu.PopupMenuItem(label);
        item.connect('activate', callback);
        menu.addMenuItem(item);
        return item;
    }

    _addImageItem(label, icon, callback) {
        const item = new PopupMenu.PopupImageMenuItem(label, icon);
        item.connect('activate', callback);
        this.menu.addMenuItem(item);
        return item;
    }

    // One entry per monitor, only when there is a choice. The size is in real
    // pixels, the coordinates used to grab are logical.
    _rebuildMonitorItems() {
        this._monitorItems.removeAll();

        const {monitors, primaryIndex} = Main.layoutManager;
        if (monitors.length < 2)
            return;

        monitors.forEach((monitor, index) => {
            const width = Math.round(monitor.width * monitor.geometry_scale);
            const height = Math.round(monitor.height * monitor.geometry_scale);
            const star = index === primaryIndex ? '*' : '';
            this._addItem(`   ${index + 1}  ${star}${width}x${height}`,
                () => this._grab(() => areaTarget(monitor)), this._monitorItems);
        });
    }

    _buildDelayItems() {
        this._delayLabel = new PopupMenu.PopupMenuItem('', {activate: false, hover: false, can_focus: false});
        this.menu.addMenuItem(this._delayLabel);

        const delay = this._settings.get_int('delay');
        const slider = new Slider(delay / MAX_DELAY);
        slider.accessible_name = 'Screenshot delay';
        slider.connect('notify::value', () => {
            this._settings.set_int('delay', Math.round(slider.value * MAX_DELAY));
            this._syncDelayLabel();
        });
        this._syncDelayLabel();

        const sliderItem = new PopupMenu.PopupBaseMenuItem({activate: false, can_focus: false});
        sliderItem.add_child(slider);
        this.menu.addMenuItem(sliderItem);
    }

    _syncDelayLabel() {
        const delay = this._settings.get_int('delay');
        this._delayLabel.label.text = delay > 0 ? `Set Delay.. (${delay}s)` : 'Set Delay..';
    }

    _syncSnapshotItems() {
        const {exists} = this._snapshot;
        this._clipboardItem.setIcon(exists ? 'system-search-symbolic' : 'action-unavailable-symbolic');
        if (exists)
            this._clipboardItem.remove_style_class_name('snappo-empty');
        else
            this._clipboardItem.add_style_class_name('snappo-empty');

        for (const item of [this._clipboardItem, this._copyItem, this._saveItem, this._clearItem, this._ocrItem])
            item.setSensitive(exists);
    }

    // Grabbing

    // Choose first, then wait, then capture: the delay is there to arrange the
    // screen, and opening a selector would close whatever was arranged.
    async _grab(chooseTarget) {
        this._cancelPending();
        this.menu.close(BoxPointer.PopupAnimation.NONE);

        try {
            await this._sleep(SETTLE_MS);
            const target = await chooseTarget();
            if (!target)
                return;

            await this._countdown(this._settings.get_int('delay'));
            const bytes = await target.capture();
            if (this._cancellable.is_cancelled())
                return;

            await this._snapshot.store(bytes);
            this._syncSnapshotItems();
            this._celebrate(target.getArea());
            this._notify('Grab complete.', 'The snapshot is in the clipboard.');
        } catch (e) {
            if (!(e instanceof GrabCancelled))
                this._notifyError('Grab Error.', e);
        }
    }

    async _pickArea() {
        const rect = await this._select(new AreaSelector());
        return rect ? areaTarget(rect) : null;
    }

    async _pickWindow() {
        const window = await this._select(new WindowSelector());
        return window ? windowTarget(window) : null;
    }

    async _select(selector) {
        this._selector = selector;
        try {
            return await selector.select();
        } finally {
            this._selector = null;
        }
    }

    async _countdown(seconds) {
        if (seconds === 0)
            return;

        this._icon.gicon = this._busyIcon;
        this._countdownLabel.show();
        try {
            for (let left = seconds; left > 0; left--) {
                this._countdownLabel.text = `${left}`;
                // eslint-disable-next-line no-await-in-loop
                await this._sleep(1000);
            }
        } finally {
            if (!this._cancellable.is_cancelled()) {
                this._countdownLabel.hide();
                this._icon.gicon = this._cameraIcon;
            }
        }
        await this._sleep(SETTLE_MS);
    }

    _sleep(ms) {
        return new Promise((resolve, reject) => {
            const id = GLib.timeout_add(GLib.PRIORITY_DEFAULT, ms, () => {
                this._pendingWait = null;
                resolve();
                return GLib.SOURCE_REMOVE;
            });
            this._pendingWait = {id, reject};
        });
    }

    // Starting another grab replaces the one still waiting or selecting.
    _cancelPending() {
        this._selector?.cancel();
        if (this._pendingWait) {
            const {id, reject} = this._pendingWait;
            this._pendingWait = null;
            GLib.source_remove(id);
            reject(new GrabCancelled());
        }
    }

    _celebrate(area) {
        global.display.get_sound_player().play_from_file(
            Gio.File.new_for_path(`${global.datadir}/sounds/screen-capture.oga`),
            'Screenshot taken', null);
        new Flashspot(area).fire();
    }

    // Snapshot actions

    _showSnapshot() {
        try {
            Gio.AppInfo.launch_default_for_uri(this._snapshot.uri,
                global.create_app_launch_context(0, -1));
        } catch (e) {
            this._notifyError('Clipboard Error.', e);
        }
    }

    async _copySnapshot() {
        try {
            await this._snapshot.copyToClipboard();
        } catch (e) {
            this._notifyError('Clipboard Error.', e);
        }
    }

    async _saveSnapshot() {
        const stamp = GLib.DateTime.new_now_local().format('%Y-%m-%d-%H-%M-%S');
        try {
            this._saveProcess?.force_exit();
            const process = Gio.Subprocess.new(
                ['gjs', '-m', `${this._extension.path}/saveDialog.js`, `Snappo-${stamp}.png`],
                Gio.SubprocessFlags.STDOUT_PIPE);
            this._saveProcess = process;

            const [stdout] = await process.communicate_utf8_async(null, this._cancellable);
            if (this._saveProcess === process)
                this._saveProcess = null;

            const path = stdout.trim();
            if (path)
                await this._snapshot.saveTo(path);
        } catch (e) {
            if (!e.matches?.(Gio.IOErrorEnum, Gio.IOErrorEnum.CANCELLED))
                this._notifyError('Save Error.', e);
        }
    }

    async _clearSnapshot() {
        try {
            await this._snapshot.clear();
        } catch (e) {
            this._notifyError('Clipboard Error.', e);
        }
        this._syncSnapshotItems();
    }

    async _ocr() {
        this._icon.gicon = this._busyIcon;
        try {
            const {text, missing} = await recognize(this._snapshot.path, this._cancellable);
            if (text)
                setClipboardText(text);
            this._reportOcr(text, missing);
        } catch (e) {
            if (!e.matches?.(Gio.IOErrorEnum, Gio.IOErrorEnum.CANCELLED))
                this._notifyError('OCR Error.', e);
        } finally {
            if (!this._cancellable.is_cancelled())
                this._icon.gicon = this._cameraIcon;
        }
    }

    _reportOcr(text, missing) {
        const command = missing.length > 0 ? installCommand(missing) : null;
        const install = command ? `To install: ${command}` : '';
        const canRead = !missing.includes('tesseract');
        const tools = missing.join(' and ');

        let title, lines;
        if (text) {
            title = 'OCR Completed.';
            lines = ['You can now press CTRL+V to paste text.'];
        } else if (canRead) {
            title = 'OCR Completed.';
            lines = ['No text or barcode was found, the clipboard is unchanged.'];
        } else {
            title = 'OCR Error.';
            lines = [`OCR needs ${tools}, which ${missing.length > 1 ? 'are' : 'is'} not installed.`];
        }
        if (canRead && missing.length > 0)
            lines.push(`Barcodes were skipped: ${tools} is not installed.`);
        if (install)
            lines.push(install);

        this._notify(title, lines.join('\n'), {
            actions: command ? [['Copy command', () => setClipboardText(command)]] : [],
        });
    }

    _showAbout() {
        this._aboutDialog?.close();
        this._aboutDialog = new AboutDialog(this._extension);
        this._aboutDialog.connect('destroy', dialog => {
            if (this._aboutDialog === dialog)
                this._aboutDialog = null;
        });
        this._aboutDialog.open();
    }

    // Notifications

    _notify(title, body, {actions = []} = {}) {
        if (!this._source) {
            this._source = new MessageTray.Source({title: 'Snappo', icon: this._cameraIcon});
            this._source.connect('destroy', () => {
                this._source = null;
            });
            Main.messageTray.add(this._source);
        }

        const notification = new MessageTray.Notification({
            source: this._source,
            title,
            body,
            isTransient: actions.length === 0,
        });
        for (const [label, callback] of actions)
            notification.addAction(label, callback);
        this._source.addNotification(notification);
    }

    _notifyError(title, error) {
        console.error(`Snappo: ${title}`, error);
        this._notify(title, error.message);
    }

    _onDestroy() {
        this._cancelPending();
        this._cancellable.cancel();
        this._saveProcess?.force_exit();
        this._aboutDialog?.close();
        this._source?.destroy();
    }
});
