# snappo
### A Screen Snapshot tool with OCR capabilities
Snappo stand for SNapshot APPlicatiOn. It is a useful tool
that can be useful to grab windows, areas of the screen, or
the entire desktop in the system clipboard for quick copy & paste exchanges with other applications.  
What makes Snappo useful is the possibility to apply bar code recognition, and OCR, on the clipboard
content, leaving you the possibility to easily paste the text extracted from codes and images. 
 
Snappo is written in python using the pygtk library, and relies on gnome to function. The GUI is 
designed as a frontend to a shell script that leverages a few commands to work its magic.

#### Dependencies
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
`pygtk`  
`appindicator`  
`notify`  

**MacOS**  
(Coming soon)