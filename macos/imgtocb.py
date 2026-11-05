#!/usr/bin/env python3
import sys
from AppKit import *


def copy_to_clipboard(path):
    if path == "-":
        input = sys.stdin.buffer.read()
        image = NSImage.alloc().initWithData_(input)
    else:
        image = NSImage.alloc().initWithContentsOfFile_(path)
    copied = False
    if image != None:
        pasteboard = NSPasteboard.generalPasteboard()
        pasteboard.clearContents()
        copiedObjects = NSArray.arrayWithObject_(image)
        copied = pasteboard.writeObjects_(copiedObjects)
        pasteboard.release()
        image.release()
    return copied


def main():
    if len(sys.argv) < 2:
        print("Usage:\n\n" +
              "Copy file to clipboard:\n    ./imgtocb path/to/file\n\n" +
              "Copy stdin to clipboard:\n    cat /path/to/file | ./imgtovb -")
        return 1;
    path = sys.argv[1]
    ret = copy_to_clipboard(path)
    return 0 if ret == True else 1


if __name__ == "__main__":
    main()
