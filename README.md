# snappo
### A Screen Snapshot tool with OCR capabilities
Snappo stand for **SN**apshot **APP**licati**O**n. It is a useful tool to take snapshots of windows,
areas of the screen, or the entire desktop in the system clipboard, for quick copy & paste exchanges
with other applications. What makes Snappo different is the possibility to apply bar code recognition
or OCR on the clipboard snapshot content: if the decoding or OCR will be successful, the clipboard
will be set with the decoded or recognized text, leaving you with the possibility to easily paste it 
elsewhere.  

Snappo is written in python using the pygtk library, and relies on gnome to function. The GUI is 
designed as a frontend to a shell script that leverages a few commands to work its magic.

### Dependencies
**Linux**  
*Binaries*:  
`tesseract` (optical character recognition)  
`zbarimg` (bar codes decoding)   
`xclip`  (X Window clipboard for images)  
`xsel` (Insert text into X Window Clipboard)   
`xdotool`  (Select a window and give it focus)  
`eog`  (Visualize grabbed imaged)  
`gnome-screenshot` (grab the graphic data from the screen)  
*Python*  
`PyGObject` (Python Gtk Object bindings library)

### Installation

##### Fedora
`$ sudo dnf install python3-gobject gtk3`  
`$ sudo dnf install tesseract zbar xclip xsel xdotool eog gnome-screenshot`  

##### Ubuntu
`$ sudo apt update`  
`$ sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0`  
`$ sudo apt install tesseract-ocr zbar-tools xclip xsel xdotool eog gnome-screenshot`  

In case of problems, more information about the installation of the python Gtk Object binding can be found [here](https://pygobject.readthedocs.io/en/latest/getting_started.html)

**MacOS**  
(Coming soon)

