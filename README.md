# FreshNamer

FreshNamer is a clean, cross-platform batch renaming tool built with Python and PyQt6. It helps you rename large sets of files quickly using simple presets or advanced formatting patterns—all in a relatively simple offline GUI.

**Disclaimer:** This project was built using AI but implemented by yours truly. Do with that as you will.

## Features

- Rename images, videos, audio, GIFs, and documents
- **Normal mode**: prefix, suffix, padding, start number
- **Advanced mode**: Python-style format strings with placeholders (`{original}`, `{num}`, `{num_padded}`, etc.)
- Live preview of output names
- Multi-category configuration (image, video, audio, GIF, document)
- Undo support (multi-level undo stack)
- Fully offline—no data leaves your machine

## Building from Source

### Prerequisites

- Python 3.9+
- PyQt6
- PyInstaller

### Install Dependencies

```bash
pip install -r requirements.txt
pip install pyinstaller
```

### Run from Source

```bash
python GUI.py
```

### Build Standalone Executable

#### macOS

```bash
pyinstaller FreshNamer.spec
```

Output: `dist/FreshNamer/FreshNamer` (ready to run, double-click or execute from terminal)

> For release packaging, zip the `dist/FreshNamer` folder and upload the archive to GitHub Releases.

#### Linux

On a Linux machine, run the same command:

```bash
pyinstaller FreshNamer.spec
```

Output: `dist/FreshNamer/FreshNamer` (standalone binary, no dependencies needed)

#### Windows

On Windows, use:

```bash
pyinstaller FreshNamer.spec
```

Output: `dist/FreshNamer/FreshNamer.exe`

### Cross-Platform Building with Docker

To build a Linux binary on macOS or Windows:

```bash
docker build -t freshnamer-builder .
docker run --rm -v $(pwd):/app freshnamer-builder
```

Output: `dist-linux/FreshNamer/FreshNamer`


## Project Architecture

- **GUI.py**: PyQt6 interface with live preview and settings management
- **engine.py**: Core rename planning and execution logic with undo support
- **core.py**: Rename mode implementations (normal and advanced formatting)
- **config.py**: Configuration builder from GUI inputs
- **logger.py**: Rotating file logger for debugging
- **paths.py**: PyInstaller resource path handling

## Recent Updates

- ✅ Fixed advanced mode format string validation
- ✅ Fixed undefined variable in debug logs
- ✅ Improved undo ordering for reliable reversibility
- ✅ Added optional Docker setup for cross-platform builds


## License

FreshNamer is licensed under the MIT License. See the LICENSE file for full details.