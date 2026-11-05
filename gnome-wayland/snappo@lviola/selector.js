// Full-screen modal overlays for choosing what to grab.
// select() resolves to the choice, or to null if cancelled with Escape.

import Clutter from 'gi://Clutter';
import GObject from 'gi://GObject';
import Meta from 'gi://Meta';
import Shell from 'gi://Shell';
import St from 'gi://St';

import * as Main from 'resource:///org/gnome/shell/ui/main.js';

// A click without a drag gives an area this small; treat it as a cancel.
const MIN_AREA_SIZE = 4;

const Selector = GObject.registerClass(
class Selector extends St.Widget {
    _init() {
        super._init({reactive: true, x: 0, y: 0});
        this.add_constraint(new Clutter.BindConstraint({
            source: global.stage,
            coordinate: Clutter.BindCoordinate.ALL,
        }));

        this._highlight = new St.Widget({
            style_class: 'select-area-rubberband',
            visible: false,
        });
        this.add_child(this._highlight);

        this._gesture = new Clutter.PanGesture();
        this._gesture.set_begin_threshold(0);
        this._gesture.connect('recognize', () => this._onPressed(this._pointer()));
        this._gesture.connect('pan-update', () => this._onDragged(this._pointer()));
        this._gesture.connect('end', () => this._onReleased(this._pointer()));
        this.add_action(this._gesture);

        this.set_cursor_type(Clutter.CursorType.CROSSHAIR);
    }

    select() {
        Main.uiGroup.add_child(this);
        Main.uiGroup.set_child_above_sibling(this, null);

        this._grab = Main.pushModal(this, {actionMode: Shell.ActionMode.POPUP});
        this.grab_key_focus();

        return new Promise(resolve => {
            this._resolve = resolve;
        });
    }

    cancel() {
        this._finish(null);
    }

    _finish(result) {
        if (!this._resolve)
            return;

        const resolve = this._resolve;
        this._resolve = null;
        Main.popModal(this._grab);
        this.destroy();
        resolve(result);
    }

    _pointer() {
        const coords = this._gesture.get_centroid_abs();
        return {x: Math.floor(coords.x), y: Math.floor(coords.y)};
    }

    _showHighlight({x, y, width, height}) {
        this._highlight.set_position(x, y);
        this._highlight.set_size(width, height);
        this._highlight.show();
    }

    _onPressed(_point) {}

    _onDragged(_point) {}

    _onReleased(_point) {}

    vfunc_key_press_event(event) {
        if (event.get_key_symbol() === Clutter.KEY_Escape) {
            this.cancel();
            return Clutter.EVENT_STOP;
        }
        return Clutter.EVENT_PROPAGATE;
    }
});

// Drag a rectangle; resolves to {x, y, width, height} in stage coordinates.
export const AreaSelector = GObject.registerClass(
class AreaSelector extends Selector {
    _rectTo({x, y}) {
        return {
            x: Math.min(this._start.x, x),
            y: Math.min(this._start.y, y),
            width: Math.abs(this._start.x - x) + 1,
            height: Math.abs(this._start.y - y) + 1,
        };
    }

    _onPressed(point) {
        this._start = point;
    }

    _onDragged(point) {
        this._showHighlight(this._rectTo(point));
    }

    _onReleased(point) {
        const rect = this._rectTo(point);
        const bigEnough = rect.width >= MIN_AREA_SIZE && rect.height >= MIN_AREA_SIZE;
        this._finish(bigEnough ? rect : null);
    }
});

const PICKABLE_TYPES = [
    Meta.WindowType.NORMAL,
    Meta.WindowType.DIALOG,
    Meta.WindowType.MODAL_DIALOG,
    Meta.WindowType.UTILITY,
];

// The topmost window at a point; the actors are listed bottom to top.
function windowAt(x, y) {
    const workspace = global.workspace_manager.get_active_workspace();
    const actors = global.get_window_actors();
    for (let i = actors.length - 1; i >= 0; i--) {
        const window = actors[i].get_meta_window();
        if (!PICKABLE_TYPES.includes(window.get_window_type()) ||
            !window.located_on_workspace(workspace) ||
            !window.showing_on_its_workspace())
            continue;

        const rect = window.get_frame_rect();
        if (x >= rect.x && x < rect.x + rect.width &&
            y >= rect.y && y < rect.y + rect.height)
            return window;
    }
    return null;
}

// Hover to highlight a window, click to pick it; resolves to its Meta.Window.
export const WindowSelector = GObject.registerClass(
class WindowSelector extends Selector {
    select() {
        const result = super.select();
        const [x, y] = global.get_pointer();
        this._hover(x, y);
        return result;
    }

    _hover(x, y) {
        const window = windowAt(x, y);
        if (window)
            this._showHighlight(window.get_frame_rect());
        else
            this._highlight.hide();
    }

    vfunc_motion_event(event) {
        const [x, y] = event.get_coords();
        this._hover(x, y);
        return Clutter.EVENT_STOP;
    }

    _onReleased({x, y}) {
        // Clicking the empty desktop keeps the picker open.
        const window = windowAt(x, y);
        if (window)
            this._finish(window);
    }
});
