// Standalone process: reads a PNG on stdin, makes rectangles of it transparent
// and writes the PNG to stdout. Rectangles are in stage coordinates, which the
// stage width converts to image pixels.
//
// Usage: gjs -m clearGaps.js STAGE_WIDTH X,Y,WIDTH,HEIGHT...

import GdkPixbuf from 'gi://GdkPixbuf';
import GioUnix from 'gi://GioUnix';
import System from 'system';

const [stageWidth, ...gaps] = System.programArgs;

const stdin = new GioUnix.InputStream({fd: 0, close_fd: false});
const loader = new GdkPixbuf.PixbufLoader();
for (;;) {
    const chunk = stdin.read_bytes(1 << 20, null);
    if (chunk.get_size() === 0)
        break;
    loader.write_bytes(chunk);
}
loader.close();

const pixbuf = loader.get_pixbuf().add_alpha(false, 0, 0, 0);
const scale = pixbuf.width / Number(stageWidth);
for (const gap of gaps) {
    const [x, y, width, height] = gap.split(',').map(n => Math.round(Number(n) * scale));
    pixbuf.new_subpixbuf(x, y, width, height).fill(0);
}

const [, png] = pixbuf.save_to_bufferv('png', [], []);
new GioUnix.OutputStream({fd: 1, close_fd: false}).write_all(png, null);
