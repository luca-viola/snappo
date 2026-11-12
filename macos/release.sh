#!/usr/bin/env bash
# Build a standalone snappo.app, sign it with a Developer ID, notarize and staple it.
#
# Needs a "Developer ID Application" certificate in the keychain and notarytool
# credentials stored with:
#   xcrun notarytool store-credentials snappo-notary --apple-id <id> --team-id <team>
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

IDENTITY="${IDENTITY:-Developer ID Application}"
PROFILE="${NOTARY_PROFILE:-snappo-notary}"
PYTHON="${PYTHON:-.venv/bin/python}"
APP="dist/snappo.app"
ZIP="dist/snappo.zip"

rm -rf build dist
"$PYTHON" setup.py py2app --emulate-shell-environment > /dev/null

# Sign every Mach-O file inside the bundle, innermost first, then the bundle.
# --deep would skip the .so files in Resources, and library validation would then
# refuse to load them.
find "$APP" -type f | while read -r f; do
  if file "$f" | grep -q "Mach-O"; then echo "$f"; fi
done | awk '{print length, $0}' | sort -rn | cut -d' ' -f2- | while read -r f; do
  codesign --force --timestamp --options runtime --sign "$IDENTITY" "$f"
done
codesign --force --timestamp --options runtime --sign "$IDENTITY" "$APP"
codesign --verify --deep --strict "$APP"

ditto -c -k --keepParent "$APP" "$ZIP"
xcrun notarytool submit "$ZIP" --keychain-profile "$PROFILE" --wait
xcrun stapler staple "$APP"
spctl --assess --type execute --verbose "$APP"

# Re-zip with the ticket stapled, ready to hand out.
rm "$ZIP"
ditto -c -k --keepParent "$APP" "$ZIP"
echo "Done: $APP and $ZIP"
