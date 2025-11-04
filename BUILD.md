# Build & Run Guide - Photo Selector App

This guide covers how to run the app in development mode and how to build a standalone macOS application.

## Prerequisites

### Install Python with Tkinter Support (macOS)

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python with Tkinter support
brew install python-tk@3.11
```

### Install Dependencies

```bash
# Navigate to project directory
cd /Users/bereczkiattila/Projects/Web/photo_selector_helper

# Install Python dependencies
/opt/homebrew/bin/python3.11 -m pip install -r requirements.txt

# Install PyInstaller for building standalone app
/opt/homebrew/bin/python3.11 -m pip install pyinstaller
```

## Running in Development Mode

### Option 1: Run Python Script Directly

```bash
# Navigate to project directory
cd /Users/bereczkiattila/Projects/Web/photo_selector_helper

# Run the app
/opt/homebrew/bin/python3.11 photo_selector.py
```

### Option 2: Make Script Executable

```bash
# Make the script executable
chmod +x photo_selector.py

# Run it directly
./photo_selector.py
```

## Building Standalone macOS Application

### Build the App Bundle

```bash
# Navigate to project directory
cd /Users/bereczkiattila/Projects/Web/photo_selector_helper

# Build using PyInstaller spec file
pyinstaller PhotoSelector.spec
```

### Build Output

After building, you'll find:
- **App Bundle**: `dist/PhotoSelector.app`
- **Build Files**: `build/` directory (can be deleted)

### Run the Standalone App

```bash
# Run from terminal
open dist/PhotoSelector.app

# Or double-click PhotoSelector.app in Finder
```

### Install the App

```bash
# Copy to Applications folder
cp -r dist/PhotoSelector.app /Applications/

# Run from Applications
open /Applications/PhotoSelector.app
```

## What Gets Bundled

The PyInstaller build includes:

### Python Scripts
- `photo_selector.py` - Main application
- `create_pdf_grid.py` - PDF grid generator
- `apply_preset_photoshop.sh` - Photoshop automation script
- `batch_convert_photoshop_v2.jsx` - Photoshop JSX script

### Data Files
- `watermark.png` - Default watermark/logo for PDF
- OpenCV Haar Cascade files (for face detection)

### Python Libraries
- `rawpy` - RAW file processing
- `numpy` - Array operations
- `scipy` - Scientific computing
- `Pillow` - Image manipulation
- `opencv-python` - Computer vision (face detection, horizon detection)
- `reportlab` - PDF generation
- `tkinter` - GUI framework

## Testing the Build

### Verify All Features Work

1. **Launch the app**
   ```bash
   open dist/PhotoSelector.app
   ```

2. **Test photo analysis**
   - Select input folder with ARW files
   - Click "Analyze Photos"
   - Verify face detection works
   - Verify sharpness calculation works

3. **Test photo processing**
   - Click "Process Selected Photos"
   - Verify RAW files are copied
   - Verify XMP files are created
   - Verify Photoshop automation launches
   - Verify JPEG conversion completes
   - Verify PDF grid is created

4. **Test watermark**
   - Check PDF grid includes watermark
   - Verify watermark.png is loaded automatically

## Troubleshooting Build Issues

### "Module not found" errors

```bash
# Rebuild with verbose output
pyinstaller --clean PhotoSelector.spec
```

### Watermark not found

Make sure `watermark.png` exists in the project directory before building:
```bash
ls -la watermark.png
```

### Face detection not working

The OpenCV Haar Cascade files should be bundled automatically. Verify they're included:
```bash
# Check bundled files
ls -la dist/PhotoSelector.app/Contents/MacOS/cv2/data/
```

### App crashes on launch

Run from terminal to see error messages:
```bash
dist/PhotoSelector.app/Contents/MacOS/PhotoSelector
```

## Clean Build

If you need to rebuild from scratch:

```bash
# Remove previous build artifacts
rm -rf build dist

# Remove PyInstaller cache
rm -rf __pycache__

# Rebuild
pyinstaller PhotoSelector.spec
```

## Distribution

### Share the App

To share with others:

1. **Create DMG (recommended)**
   ```bash
   # Install create-dmg
   brew install create-dmg

   # Create DMG
   create-dmg \
     --volname "Photo Selector" \
     --window-pos 200 120 \
     --window-size 600 400 \
     --icon-size 100 \
     --app-drop-link 425 120 \
     PhotoSelector.dmg \
     dist/PhotoSelector.app
   ```

2. **Zip the app**
   ```bash
   cd dist
   zip -r PhotoSelector.zip PhotoSelector.app
   ```

### System Requirements

The built app requires:
- **macOS**: 10.13 (High Sierra) or later
- **Photoshop**: Any version from 2020-2026 (optional, for automation)
- **Disk Space**: ~200MB for app + dependencies

## File Structure After Build

```
photo_selector_helper/
├── photo_selector.py           # Main script
├── create_pdf_grid.py          # PDF generator
├── apply_preset_photoshop.sh   # Shell script
├── batch_convert_photoshop_v2.jsx  # Photoshop script
├── watermark.png               # Watermark image
├── PhotoSelector.spec          # PyInstaller spec
├── requirements.txt            # Python dependencies
├── README.md                   # User guide
├── BUILD.md                    # This file
├── build/                      # Build artifacts (can delete)
└── dist/
    └── PhotoSelector.app       # Standalone macOS app
```

## Development Workflow

### Recommended Workflow

1. **Edit code**: Make changes to `photo_selector.py` or other scripts
2. **Test in dev mode**: Run with `python3.11 photo_selector.py`
3. **Rebuild app**: Run `pyinstaller PhotoSelector.spec`
4. **Test standalone**: Run `dist/PhotoSelector.app`
5. **Distribute**: Create DMG or ZIP

### Quick Rebuild

```bash
# Clean and rebuild
rm -rf build dist && pyinstaller PhotoSelector.spec
```

## Performance Notes

- **Build time**: ~30 seconds on M1 Mac
- **App size**: ~150MB (includes all Python libraries)
- **Startup time**: ~2 seconds (first launch may be slower)
- **Analysis speed**: ~1 photo/second for face detection + sharpness

---

**Built with**: PyInstaller, Python 3.11, Tkinter
