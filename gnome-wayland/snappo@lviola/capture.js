// What to grab, decided before the delay and captured after it.
// A target is {getArea(), capture()}: getArea() is the on-screen rectangle to
// flash, capture() resolves to the PNG as GLib.Bytes.

import Gio from 'gi://Gio';
import Shell from 'gi://Shell';

import * as Main from 'resource:///org/gnome/shell/ui/main.js';

Gio._promisify(Shell.Screenshot.prototype, 'screenshot');
Gio._promisify(Shell.Screenshot.prototype, 'screenshot_area');
Gio._promisify(Shell.Screenshot, 'composite_to_stream');
Gio._promisify(Gio.Subprocess.prototype, 'communicate_async');

const CLEAR_GAPS = Gio.File.new_for_uri(import.meta.url)
    .get_parent().get_child('clearGaps.js').get_path();

async function toBytes(writeTo) {
    const stream = Gio.MemoryOutputStream.new_resizable();
    await writeTo(stream);
    stream.close(null);
    return stream.steal_as_bytes();
}

// The parts of the stage no monitor covers, when monitors differ in size. Cuts
// the stage into a grid along the monitor edges and keeps the uncovered cells.
function findGaps(monitors, stageWidth, stageHeight) {
    const cuts = (start, size, end) => [...new Set([
        0, end, ...monitors.flatMap(m => [m[start], m[start] + m[size]]),
    ])].sort((a, b) => a - b);
    const xs = cuts('x', 'width', stageWidth);
    const ys = cuts('y', 'height', stageHeight);

    const gaps = [];
    for (let i = 0; i + 1 < xs.length; i++) {
        for (let j = 0; j + 1 < ys.length; j++) {
            const covered = monitors.some(m =>
                xs[i] >= m.x && xs[i + 1] <= m.x + m.width &&
                ys[j] >= m.y && ys[j + 1] <= m.y + m.height);
            if (!covered)
                gaps.push([xs[i], ys[j], xs[i + 1] - xs[i], ys[j + 1] - ys[j]]);
        }
    }
    return gaps;
}

// Those parts come back as undefined pixels, so they're made transparent. A
// separate process does it because re-encoding the PNG here would freeze the
// whole desktop for a moment.
async function clearGaps(png, gaps, stageWidth) {
    const process = Gio.Subprocess.new(
        ['gjs', '-m', CLEAR_GAPS, `${stageWidth}`, ...gaps.map(gap => gap.join(','))],
        Gio.SubprocessFlags.STDIN_PIPE | Gio.SubprocessFlags.STDOUT_PIPE);
    const [output] = await process.communicate_async(png, null);
    if (!process.get_successful())
        throw new Error('Could not process the screenshot.');
    return output;
}

export function desktopTarget() {
    return {
        getArea: () => ({
            x: 0,
            y: 0,
            width: global.stage.width,
            height: global.stage.height,
        }),
        capture: async () => {
            const {width, height} = global.stage;
            const png = await toBytes(stream => new Shell.Screenshot().screenshot(false, stream));
            const gaps = findGaps(Main.layoutManager.monitors, width, height);
            return gaps.length > 0 ? clearGaps(png, gaps, width) : png;
        },
    };
}

// `rect` is in stage coordinates.
export function areaTarget({x, y, width, height}) {
    return {
        getArea: () => ({x, y, width, height}),
        capture: () => toBytes(stream =>
            new Shell.Screenshot().screenshot_area(x, y, width, height, stream)),
    };
}

// Paints the window itself rather than cropping the screen, so the result is
// right even if the window gets covered during the delay.
export function windowTarget(metaWindow) {
    return {
        getArea: () => metaWindow.get_frame_rect(),
        capture: () => {
            const actor = metaWindow.get_compositor_private();
            if (!actor)
                throw new Error('The window was closed.');

            const texture = actor.paint_to_content(null).get_texture();
            return toBytes(stream => Shell.Screenshot.composite_to_stream(
                texture, 0, 0, -1, -1, 1, null, 0, 0, 1, stream));
        },
    };
}
