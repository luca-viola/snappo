// Barcode detection with zbarimg, falling back to text recognition with
// tesseract. Neither tool ships with GNOME, so a missing one is an expected
// state: it is reported with the command that installs it, never installed.

import Gio from 'gi://Gio';
import GLib from 'gi://GLib';

Gio._promisify(Gio.Subprocess.prototype, 'communicate_utf8_async');

const ZBAR = 'zbarimg';
const TESSERACT = 'tesseract';
const ZBAR_NO_SYMBOLS = 4;

const INSTALLERS = [
    {
        ids: ['fedora', 'rhel', 'centos'],
        command: 'sudo dnf install',
        packages: {[TESSERACT]: ['tesseract'], [ZBAR]: ['zbar']},
    },
    {
        ids: ['debian', 'ubuntu'],
        command: 'sudo apt install',
        packages: {[TESSERACT]: ['tesseract-ocr'], [ZBAR]: ['zbar-tools']},
    },
    {
        ids: ['arch'],
        command: 'sudo pacman -S',
        packages: {[TESSERACT]: ['tesseract', 'tesseract-data-eng'], [ZBAR]: ['zbar']},
    },
    {
        ids: ['opensuse', 'suse'],
        command: 'sudo zypper install',
        packages: {[TESSERACT]: ['tesseract-ocr'], [ZBAR]: ['zbar']},
    },
];

// The command installing `tools` on this distro, or null if it isn't known.
// Derivatives are matched through ID_LIKE, e.g. fedora-asahi-remix -> fedora.
export function installCommand(tools, osIds = [
    GLib.get_os_info('ID'),
    ...(GLib.get_os_info('ID_LIKE') ?? '').split(/\s+/),
]) {
    const installer = INSTALLERS.find(({ids}) => osIds.some(id => ids.includes(id)));
    if (!installer)
        return null;

    const packages = tools.flatMap(tool => installer.packages[tool]);
    return `${installer.command} ${packages.join(' ')}`;
}

async function run(argv, cancellable) {
    const proc = Gio.Subprocess.new(argv,
        Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_SILENCE);
    const [stdout] = await proc.communicate_utf8_async(null, cancellable);
    return {status: proc.get_exit_status(), text: stdout.trim()};
}

// Resolves to {text, missing}: the decoded text ('' if nothing was found) and
// the tools that could not be used.
export async function recognize(path, cancellable) {
    const missing = [ZBAR, TESSERACT].filter(tool => !GLib.find_program_in_path(tool));

    if (!missing.includes(ZBAR)) {
        const {status, text} = await run([ZBAR, '--raw', '-q', path], cancellable);
        if (status === 0 && text)
            return {text, missing};
        if (status !== ZBAR_NO_SYMBOLS)
            console.warn(`Snappo: ${ZBAR} exited with status ${status}`);
    }

    if (missing.includes(TESSERACT))
        return {text: '', missing};

    const {status, text} = await run([TESSERACT, path, 'stdout'], cancellable);
    if (status !== 0)
        throw new Error(`${TESSERACT} exited with status ${status}.`);
    return {text, missing};
}
