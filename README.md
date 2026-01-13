# FreshNamer

FreshNamer is a clean, cross-platform batch renaming tool built with Python and PyQt6. It helps you rename large sets of files quickly using simple presets or advanced formatting patterns - all in a relatively simple offline GUI.


## Features:

- Rename images, videos, audio, GIFs, and documents
- Normal mode (prefix, suffix, padding, start number)
- Advanced mode using Python-style format strings
- Live preview of output names
- Multi-category configuration (image, video, audio, GIF, document)
- Fully offline - no data leaves your machine
- Cross-platform builds for Linux, macOS, and Windows


## Platforms:

FreshNamer is packaged with PyInstaller and runs without requiring Python or PyQt6 installed.

- Linux: AppImage (self-contained)
- Windows: standalone .exe
- macOS: .app bundle

Download links will appear in the Releases section as they are published.


## Installation:

Platform-specific installation instructions are as follows:


### Linux:

1. Download the AppImage
2. Right-click → Properties → Allow executing file as program
3. Double-click to launch
4. Optional: use a .desktop launcher for a native feel


### Windows:

Download FreshNamer.exe and run it.


### macOS:

Download the .app bundle, move it to Applications, and open it.


## Development:

FreshNamer is built with Python 3, PyQt6, and PyInstaller.


## To run from source:  

Run "python GUI.py" in a terminal inside the project directory.
Depending on platform and the python version installed, "python GUI.py" may also be valid.


## To build using PyInstaller:  

Run "pyinstaller FreshNamer.spec" in a terminal inside the project directory.


## Project Structure:

FreshNamer  
├── GUI.py  
├── engine.py  
├── core.py  
├── config.py  
├── logger.py  
├── paths.py  
├── assets  
│   ├── FreshNamerIcon.png  
│   ├── FreshNamerIcon.ico  
│   └── FreshNamerIcon.icns  
├── FreshNamer.spec  
└── README.md


## Contact:

If you have any questions regarding this project feel free to contact me at the following email address:
- kresh@kreshy.com


## License:

FreshNamer is licensed under the MIT License.
See the LICENSE file for full details.