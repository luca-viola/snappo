#!/bin/env bash

TARGET_FILE="/tmp/snappo"
SCREENSHOT_CMD="/usr/bin/gnome-screenshot"
CLIPBOARD_CMD="/usr/bin/xclip -i -selection clipboard -target image/png"
CLIPBOARD_TXT_CMD="/usr/bin/xclip -sel c"
WIN_CMD='/usr/bin/xdotool'
DISPLAY_CMD='/usr/bin/eog'
BARCODE_SCAN_CMD='/usr/bin/zbarimg --raw -q'
OCR_CMD="/usr/bin/tesseract"

param=""
what="$1"

function snapshot()
{
  local param="$1"
  ${SCREENSHOT_CMD} -c${param}f ${TARGET_FILE} && cat ${TARGET_FILE} | ${CLIPBOARD_CMD}
}

case "$what" in
   window)
     if [ "$XDG_SESSION_TYPE" == "x11" ]; then
       ${WIN_CMD} windowactivate $(${WIN_CMD} selectwindow)
     fi
     snapshot "w"
     ;;
   area)
     snapshot "a"
     ;;
   desktop)
     snapshot
     ;;
   display)
     ${DISPLAY_CMD} ${TARGET_FILE}
     ;;
   copy)
      ${CLIPBOARD_CMD} < ${TARGET_FILE}
      ;;
    clear)
      echo "" | $CLIPBOARD_TXT_CMD
      rm ${TARGET_FILE}
      ;;
   ocr)
     if [ -f "${TARGET_FILE}" ]; then
       text=$(${BARCODE_SCAN_CMD}  ${TARGET_FILE})
       if [ $? -eq 4 ]; then
         text=$(${OCR_CMD} ${TARGET_FILE} stdout 2>/dev/null)
       fi
       echo -n "$text" |  ${CLIPBOARD_TXT_CMD}
     else
       exit 1
     fi
     ;;
   default)
     ;;
esac
