#!/bin/env bash

TARGET_FILE="/tmp/snappo"
SCREENSHOT_CMD="$(which gnome-screenshot)"
CLIPBOARD_CMD="$(which xclip) -i -selection clipboard -target image/png"
CLIPBOARD_TXT_CMD="$(which xclip) -sel c"
WIN_CMD="$(which xdotool)"
DISPLAY_CMD="$(which eog)"
BARCODE_SCAN_CMD="$(which zbarimg) --raw -q"
OCR_CMD="$(which tesseract)"

param=""
what="$1"
delay="$2"

function snapshot()
{
  local param="$1"
  local delay="$2"
  if [ "$param" == "d" ]; then
    param=""
  fi
  delay_opt="--delay=${delay}"
  ${SCREENSHOT_CMD} ${delay_opt} -c${param}f ${TARGET_FILE} && cat ${TARGET_FILE} | ${CLIPBOARD_CMD}
}

case "$what" in
   window)
     if [ "$XDG_SESSION_TYPE" == "x11" ]; then
       ${WIN_CMD} windowactivate $(${WIN_CMD} selectwindow)
     fi
     snapshot "w" "$delay"
     ;;
   area)
     snapshot "a" "$delay"
     ;;
   desktop)
     snapshot "d" "$delay"
     ;;
   display)
     if [ -f "${TARGET_FILE}" ]; then
       ${DISPLAY_CMD} ${TARGET_FILE}
     else
       exit 1
     fi
     ;;
   copy)
      if [ -f "${TARGET_FILE}" ]; then
        ${CLIPBOARD_CMD} < ${TARGET_FILE}
      else
        exit 1
      fi
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
