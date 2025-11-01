# Photo Selector - Automatic Photo Selection & Renaming Tool

A desktop application for photographers to automatically select sharp, horizontal photos and apply XMP presets.

## Features

✅ **Automatic Selection**
- Detects sharp photos using advanced sharpness analysis
- Optional filter for horizontal/vertical orientation
- Adjustable sharpness threshold
- Choose to include or exclude portrait photos

✅ **Auto-Straightening (NEW!)**
- Automatically detects tilted horizons using edge detection
- Corrects rotation angle up to ±10 degrees
- Auto-crops image to remove black edges after rotation
- Applied via XMP preset for non-destructive editing

✅ **Batch Renaming**
- Rename all selected photos with custom project name
- Sequential numbering (e.g., Wedding_0001.ARW, Wedding_0002.ARW)

✅ **XMP Sidecar Creation**
- Creates XMP sidecar files with your "Emlék" preset
- Import to Lightroom/Photoshop and preset is automatically applied
- Perfect color accuracy using Adobe's processing engine

✅ **User-Friendly GUI**
- Simple folder selection
- Real-time analysis progress
- Detailed results log

## Installation

### Step 1: Install Python

**macOS Users:**
The system Python doesn't support Tkinter properly. Install Python via Homebrew:
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python with Tkinter support
brew install python-tk@3.11
```

**Other Systems:**
Make sure you have Python 3.8 or newer installed. Check with:
```bash
python3 --version
```

### Step 2: Install Dependencies
Open Terminal and navigate to the folder with the files:
```bash
cd ~/Downloads

# macOS (using Homebrew Python):
/opt/homebrew/bin/python3.11 -m pip install -r requirements.txt

# Other systems:
pip3 install -r requirements.txt
```

**Note:** The required libraries are:
- `rawpy` - For reading Sony ARW raw files
- `numpy` - For image processing
- `scipy` - For sharpness calculations
- `Pillow` - For image manipulation
- `opencv-python` - For horizon detection and tilt correction

## Usage

### Running the App

1. Open Terminal
2. Navigate to the folder:
   ```bash
   cd ~/Downloads
   ```
3. Run the app:
   ```bash
   # macOS (using Homebrew Python):
   /opt/homebrew/bin/python3.11 photo_selector.py

   # Other systems:
   python3 photo_selector.py
   ```

### Using the App

1. **Select Input Folder**
   - Click "Browse" next to "Input Folder"
   - Choose the folder containing your ARW photos

2. **Select Output Folder** (optional)
   - If not selected, a subfolder "selected_photos" will be created automatically
   - Or choose a custom location for processed photos

3. **Enter Project Name**
   - Type your project name (e.g., "Wedding", "Portrait_Session", "Family_Photos")
   - This will be used as the prefix for renamed files

4. **Adjust Sharpness Threshold** (optional)
   - Default is 100
   - Lower = more photos selected (less strict)
   - Higher = fewer photos selected (more strict)
   - Experiment to find what works for your camera/lens

5. **Enable Auto-Straightening** (optional)
   - Check the box to automatically detect and correct tilted horizons
   - The app will analyze each photo for tilt (typically ±10 degrees or less)
   - Rotation is applied via XMP preset (non-destructive)
   - Images are auto-cropped to remove black edges

6. **Include Vertical/Portrait Photos** (optional)
   - **Checked (default):** Selects all sharp photos, both horizontal and vertical
   - **Unchecked:** Only selects sharp horizontal (landscape) photos
   - Useful if you only want landscape orientation for your project

7. **Analyze Photos**
   - Click "Analyze Photos" button
   - Wait for analysis to complete
   - Review the results in the log

8. **Process Selected Photos**
   - Click "Process Selected Photos"
   - The app will:
     - Convert RAW files to JPEG (basic processing)
     - Auto-straighten if tilt detected
     - Rename with project name + sequence number
     - Create XMP sidecar files with your preset

### Example Output

If you process 3 photos with project name "Wedding":
```
Output Folder:
  Wedding_00595.jpg   (Basic JPEG)
  Wedding_00595.xmp   (Preset sidecar for Lightroom)
  Wedding_00596.jpg
  Wedding_00596.xmp
  Wedding_00597.jpg
  Wedding_00597.xmp
```

### Next Step: Apply Preset in Lightroom

For perfect color matching your Photoshop preset:

1. **Open Adobe Lightroom**
2. **Import** the output folder
3. Preset is **automatically applied** from XMP sidecars
4. **Export as JPEG** (File → Export)
   - Format: JPEG
   - Quality: 95+
   - Done!

This gives you **perfect color accuracy** using Adobe's processing engine.

## How It Works

### Sharpness Detection
The app uses **Laplacian variance** to measure image sharpness:
- Reads a thumbnail/preview of each RAW file
- Applies edge detection algorithm
- Calculates variance (higher = sharper)
- Compares against threshold

### Orientation Detection
- Reads image dimensions from RAW metadata
- Width > Height = Horizontal (landscape)
- Width < Height = Vertical (portrait)
- Optional filtering: Include both or horizontal only

### Auto-Straightening (Horizon Correction)
The app uses **Hough Line Transform** to detect and correct tilted horizons:
- Applies Canny edge detection to find prominent lines
- Uses Hough transform to detect line angles
- Calculates median tilt angle (robust against outliers)
- Only corrects small tilts (±10 degrees)
- Adds rotation and auto-crop parameters to XMP preset
- Non-destructive - original RAW file is unchanged

### XMP Preset Workflow
Your "Emlék" preset is stored in XMP sidecar files:
- XMP files are created alongside each JPEG
- Lightroom/Photoshop automatically reads XMP sidecars
- Preset contains: Temperature 7415K, Exposure -0.40, Highlights -100, Shadows +47, Blacks -60, Vibrance +37, custom tone curve, HSL adjustments
- When imported to Lightroom, preset is automatically applied
- Export from Lightroom gives perfect color matching your Photoshop preset

## Troubleshooting

### "rawpy library not found"
Install with: `pip3 install rawpy`

If that fails on Mac, try:
```bash
brew install libraw
pip3 install rawpy
```

### "No ARW files found"
- Make sure files have .ARW or .arw extension
- Check that you selected the correct folder

### Photos not being selected
- Lower the sharpness threshold slider
- Check if photos are actually sharp (view them manually)
- Try adjusting threshold between 50-200 for different results

### App is slow
- Processing RAW files takes time (especially with many photos)
- The app analyzes thumbnails for speed, but 100+ photos may take a few minutes
- Be patient during analysis!

## Tips for Best Results

1. **Start with a small batch** (10-20 photos) to calibrate the sharpness threshold
2. **Use consistent lighting** for best sharpness detection
3. **Name your projects clearly** (include date, client name, etc.)
4. **Keep originals** - the app copies files, never deletes originals
5. **Back up your NAS** before processing large batches

## Support

For issues or questions, check the results log in the app for detailed error messages.

---

**Made for photographers who value their time! 📸**
