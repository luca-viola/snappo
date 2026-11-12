#!/usr/bin/env bash

DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
cd ${DIR}

TARGET_FILE="/tmp/snappo.png"
SCREENSHOT_CMD="$(which screencapture)"
# Inside the .app, use its own Python, which has PyObjC.
BUNDLED_PYTHON="../MacOS/python"
if [ -x "${BUNDLED_PYTHON}" ]; then
  CLIPBOARD_CMD="env RESOURCEPATH=${DIR} ${BUNDLED_PYTHON} ./imgtocb.py -"
else
  CLIPBOARD_CMD="./imgtocb.py -"
fi
CLIPBOARD_TXT_CMD="$(which pbcopy)"
DISPLAY_CMD="$(which open)"
BARCODE_SCAN_CMD="$(which zbarimg) --raw -q"
OCR_CMD="$(which tesseract)"

param=""
what="$1"
delay="$2"
desktop="$3"

function snapshot()
{
  local param="$1"
  local delay="$2"
  local desktop="$3"
  local opt="-c"
  local delay_opt=""

  case $param in
    d)
      if [ "$desktop" != "" ]; then
        opt="${opt} -D ${desktop}"
      fi
      ;;
    w)
        opt="${opt} -o -W"
      ;;
    a)
        opt="${opt} -s -i"
      ;;
    default)
      ;;
  esac
  if [ "$delay" != "" ]; then
     delay_opt="-T ${delay}"
  fi

  ${SCREENSHOT_CMD} ${delay_opt} ${opt} -f ${TARGET_FILE} && cat ${TARGET_FILE} | ${CLIPBOARD_CMD} &
}

case "$what" in
   window)
     snapshot "w" "$delay"
     ;;
   area)
     snapshot "a" "$delay"
     ;;
   desktop)
     snapshot "d" "$delay" "$desktop"
     ;;
   display)
     if [ -f "${TARGET_FILE}" ]; then
       ${DISPLAY_CMD} ${TARGET_FILE}
     else
       exit 1
     fi
     ;;
   copyto)
     if [ -f "${TARGET_FILE}" ]; then
       cp "${TARGET_FILE}" "$2"
       if [ $? -gt 0 ]; then
         exit 2
       fi
     else
       exit 1
     fi
     ;;
   copy)
      if [ -f "${TARGET_FILE}" ]; then
        cat ${TARGET_FILE} | ${CLIPBOARD_CMD}
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
       text=""
       if [ -n "$(which zbarimg)" ]; then
         text=$(${BARCODE_SCAN_CMD}  ${TARGET_FILE})
       fi
       if [ -z "$text" ]; then
	 cd /tmp      
         #text=$(${OCR_CMD} ${TARGET_FILE} stdout 2>/dev/null)
         text=$(${OCR_CMD} ./snappo.png stdout 2>/dev/null)
       fi
       echo -n "$text" |  ${CLIPBOARD_TXT_CMD}
     else
       exit 1
     fi
     ;;
   default)
     ;;
esac
