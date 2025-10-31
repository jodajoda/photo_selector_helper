# Photo Selector - Automatic Photo Selection & Renaming Tool

A desktop application for photographers to automatically select sharp, horizontal photos and apply XMP presets.

## Features

✅ **Automatic Selection**
- Detects sharp photos using advanced sharpness analysis
- Filters for horizontal orientation
- Adjustable sharpness threshold

✅ **Batch Renaming**
- Rename all selected photos with custom project name
- Sequential numbering (e.g., Wedding_0001.ARW, Wedding_0002.ARW)

✅ **XMP Preset Application**
- Automatically applies your "Emiék" Lightroom/Photoshop preset
- Creates XMP sidecar files for each selected photo

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

5. **Analyze Photos**
   - Click "Analyze Photos" button
   - Wait for analysis to complete
   - Review the results in the log

6. **Process Selected Photos**
   - Click "Process Selected Photos"
   - The app will:
     - Copy selected photos to output folder
     - Rename them with project name + sequence number
     - Create XMP sidecar files with your preset

### Example Output

If you process 3 photos with project name "Wedding":
```
Output Folder:
  Wedding_0001.ARW
  Wedding_0001.xmp
  Wedding_0002.ARW
  Wedding_0002.xmp
  Wedding_0003.ARW
  Wedding_0003.xmp
```

### Opening in Photoshop/Lightroom

After processing:
1. Open Photoshop or Lightroom
2. Import/open the photos from the output folder
3. The XMP preset will automatically apply your "Emiék" settings!

## How It Works

### Sharpness Detection
The app uses **Laplacian variance** to measure image sharpness:
- Reads a thumbnail/preview of each RAW file
- Applies edge detection algorithm
- Calculates variance (higher = sharper)
- Compares against threshold

### Orientation Detection
- Reads image dimensions from RAW metadata
- Width > Height = Horizontal ✓
- Width < Height = Vertical ✗

### XMP Preset
Your "Emiék" preset includes:
- White balance adjustment (7415K, +27 tint)
- Exposure compensation (-0.40)
- Tone curve adjustments
- HSL color adjustments
- Split toning
- And more!

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
