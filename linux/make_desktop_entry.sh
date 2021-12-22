#!/usr/bin/env bash

xdg_path="$HOME/.local/share/applications"
snappo_desktop="$xdg_path/snappo.desktop"

exepath=`realpath ../snappo.py`
iconpath=`realpath ../camera.svg`


desktopEntry="#!/usr/bin/env xdg-open  

[Desktop Entry]
Version=1.0
Name=snappo
GenericName=snappo
Terminal=false
Type=Application
Categories=Utility;Security;
Exec=\"${exepath}\"
Icon=${iconpath}
Icon[en_US]=${iconpath}"


if [ ! -f "$xdg_path/snappo.desktop" ]; then
  echo "${desktopEntry}" > "$xdg_path/snappo.desktop"
else
  echo "There is already a desktop file for snappo."
fi