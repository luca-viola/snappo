// Snappo - a screenshot tool with barcode and OCR capabilities.
// Copyright (C) 2021-2026 Luca Viola
// SPDX-License-Identifier: GPL-3.0-or-later

import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

import {SnappoIndicator} from './indicator.js';

export default class SnappoExtension extends Extension {
    enable() {
        this._indicator = new SnappoIndicator(this);
        Main.panel.addToStatusArea(this.uuid, this._indicator);
    }

    // Also runs when the screen locks. Pending grabs are cancelled, so nothing
    // can capture the lock screen, but the snapshot itself is kept on disk.
    disable() {
        this._indicator.destroy();
        this._indicator = null;
    }
}
