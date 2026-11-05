import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import GObject from 'gi://GObject';
import St from 'gi://St';

import * as ModalDialog from 'resource:///org/gnome/shell/ui/modalDialog.js';

const LICENSE_URL = 'https://www.gnu.org/licenses/gpl-3.0.html';

export const AboutDialog = GObject.registerClass(
class AboutDialog extends ModalDialog.ModalDialog {
    _init(extension) {
        super._init({styleClass: 'snappo-about'});
        const {metadata, path} = extension;

        this.contentLayout.add_child(new St.Icon({
            gicon: Gio.icon_new_for_string(`${path}/icons/camera.svg`),
            icon_size: 96,
            x_align: Clutter.ActorAlign.CENTER,
        }));
        this._addLabel('Snappo', 'snappo-about-title');
        this._addLabel('A Screenshot tool with Barcode/OCR capabilities');
        this._addLabel(`Ver: ${metadata['version-name']}`, 'snappo-about-section');
        this._addLabel('© 2021-2026 by Luca Viola', 'snappo-about-section');
        this._addLink('Snappo on github', metadata.url, 'snappo-about-section');
        this._addLink('License: GPL V3', LICENSE_URL);

        this.setButtons([{
            label: 'OK',
            action: () => this.close(),
            key: Clutter.KEY_Escape,
            default: true,
        }]);
    }

    _addLabel(text, styleClass = null) {
        this.contentLayout.add_child(new St.Label({
            text,
            style_class: styleClass,
            x_align: Clutter.ActorAlign.CENTER,
        }));
    }

    _addLink(text, url, styleClass = '') {
        const button = new St.Button({
            label: text,
            style_class: `snappo-about-link ${styleClass}`,
            x_align: Clutter.ActorAlign.CENTER,
        });
        button.connect('clicked', () => {
            Gio.AppInfo.launch_default_for_uri(url, global.create_app_launch_context(0, -1));
            this.close();
        });
        this.contentLayout.add_child(button);
    }
});
