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

## Building and Running

### Requirements

- Python 3.9+
- PyQt6
- PyInstaller for packaging

### Run from source

```bash
pip install -r requirements.txt
python GUI.py
```

### Build a standalone app

FreshNamer includes a PyInstaller spec file for generating a standalone executable.

```bash
pyinstaller FreshNamer.spec
```

After building, the bundled executable appears under `dist/FreshNamer/`.

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