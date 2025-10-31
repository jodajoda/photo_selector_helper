#!/usr/bin/env python3
"""
Photo Selector - Automatic photo selection and renaming tool
For ARW raw photos - selects sharp, horizontal images and applies XMP presets
"""

import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
from datetime import datetime

try:
    import rawpy
    import numpy as np
    HAS_RAWPY = True
except ImportError:
    HAS_RAWPY = False

# XMP preset template (loaded from your preset)
XMP_PRESET = """<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 7.0-c000 1.000000, 0000/00/00-00:00:00        ">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
    xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/"
   crs:PresetType="Normal"
   crs:Cluster=""
   crs:UUID="A04D27A42934411880733CD438F9EEC5"
   crs:SupportsAmount2="True"
   crs:SupportsAmount="True"
   crs:SupportsColor="True"
   crs:SupportsMonochrome="True"
   crs:SupportsHighDynamicRange="True"
   crs:SupportsNormalDynamicRange="True"
   crs:SupportsSceneReferred="True"
   crs:SupportsOutputReferred="True"
   crs:RequiresRGBTables="False"
   crs:ShowInPresets="True"
   crs:ShowInQuickActions="False"
   crs:CameraModelRestriction=""
   crs:Copyright=""
   crs:ContactInfo=""
   crs:Version="17.5"
   crs:CompatibleVersion="268435456"
   crs:ProcessVersion="15.4"
   crs:WhiteBalance="Custom"
   crs:Temperature="7415"
   crs:Tint="+27"
   crs:Exposure2012="-0.40"
   crs:Contrast2012="+1"
   crs:Highlights2012="-100"
   crs:Shadows2012="+47"
   crs:Whites2012="-12"
   crs:Blacks2012="-60"
   crs:Texture="+2"
   crs:Clarity2012="-11"
   crs:Dehaze="0"
   crs:Vibrance="+37"
   crs:Saturation="-9"
   crs:ParametricShadows="0"
   crs:ParametricDarks="0"
   crs:ParametricLights="0"
   crs:ParametricHighlights="0"
   crs:ParametricShadowSplit="25"
   crs:ParametricMidtoneSplit="50"
   crs:ParametricHighlightSplit="75"
   crs:HueAdjustmentRed="+6"
   crs:HueAdjustmentOrange="-5"
   crs:HueAdjustmentYellow="-6"
   crs:HueAdjustmentGreen="+12"
   crs:HueAdjustmentAqua="0"
   crs:HueAdjustmentBlue="-24"
   crs:HueAdjustmentPurple="+3"
   crs:HueAdjustmentMagenta="+20"
   crs:SaturationAdjustmentRed="-21"
   crs:SaturationAdjustmentOrange="-30"
   crs:SaturationAdjustmentYellow="-32"
   crs:SaturationAdjustmentGreen="-34"
   crs:SaturationAdjustmentAqua="-28"
   crs:SaturationAdjustmentBlue="-13"
   crs:SaturationAdjustmentPurple="-17"
   crs:SaturationAdjustmentMagenta="-39"
   crs:LuminanceAdjustmentRed="-19"
   crs:LuminanceAdjustmentOrange="-10"
   crs:LuminanceAdjustmentYellow="0"
   crs:LuminanceAdjustmentGreen="0"
   crs:LuminanceAdjustmentAqua="0"
   crs:LuminanceAdjustmentBlue="-10"
   crs:LuminanceAdjustmentPurple="0"
   crs:LuminanceAdjustmentMagenta="0"
   crs:SplitToningShadowHue="286"
   crs:SplitToningShadowSaturation="1"
   crs:SplitToningHighlightHue="238"
   crs:SplitToningHighlightSaturation="0"
   crs:SplitToningBalance="0"
   crs:ColorGradeMidtoneHue="222"
   crs:ColorGradeMidtoneSat="4"
   crs:ColorGradeShadowLum="+100"
   crs:ColorGradeMidtoneLum="+52"
   crs:ColorGradeHighlightLum="+100"
   crs:ColorGradeBlending="100"
   crs:ColorGradeGlobalHue="0"
   crs:ColorGradeGlobalSat="0"
   crs:ColorGradeGlobalLum="0"
   crs:AutoLateralCA="0"
   crs:LensProfileEnable="0"
   crs:LensManualDistortionAmount="0"
   crs:VignetteAmount="0"
   crs:DefringePurpleAmount="0"
   crs:DefringePurpleHueLo="30"
   crs:DefringePurpleHueHi="70"
   crs:DefringeGreenAmount="0"
   crs:DefringeGreenHueLo="40"
   crs:DefringeGreenHueHi="60"
   crs:PerspectiveUpright="0"
   crs:PerspectiveVertical="0"
   crs:PerspectiveHorizontal="0"
   crs:PerspectiveRotate="0.0"
   crs:PerspectiveAspect="0"
   crs:PerspectiveScale="100"
   crs:PerspectiveX="0.00"
   crs:PerspectiveY="0.00"
   crs:ShadowTint="0"
   crs:RedHue="0"
   crs:RedSaturation="-14"
   crs:GreenHue="0"
   crs:GreenSaturation="0"
   crs:BlueHue="0"
   crs:BlueSaturation="0"
   crs:HDREditMode="0"
   crs:CurveRefineSaturation="100"
   crs:ToneCurveName2012="Custom"
   crs:HasSettings="True"
   crs:CropConstrainToWarp="0"
   crs:AsShotTemperature="6350"
   crs:AsShotTint="4">
   <crs:Name>
    <rdf:Alt>
     <rdf:li xml:lang="x-default">Emiék</rdf:li>
    </rdf:Alt>
   </crs:Name>
   <crs:ShortName>
    <rdf:Alt>
     <rdf:li xml:lang="x-default"/>
    </rdf:Alt>
   </crs:ShortName>
   <crs:SortName>
    <rdf:Alt>
     <rdf:li xml:lang="x-default"/>
    </rdf:Alt>
   </crs:SortName>
   <crs:Group>
    <rdf:Alt>
     <rdf:li xml:lang="x-default">Családfotózás</rdf:li>
    </rdf:Alt>
   </crs:Group>
   <crs:Description>
    <rdf:Alt>
     <rdf:li xml:lang="x-default"/>
    </rdf:Alt>
   </crs:Description>
   <crs:ToneCurvePV2012>
    <rdf:Seq>
     <rdf:li>0, 0</rdf:li>
     <rdf:li>27, 34</rdf:li>
     <rdf:li>104, 117</rdf:li>
     <rdf:li>174, 175</rdf:li>
     <rdf:li>218, 210</rdf:li>
     <rdf:li>255, 239</rdf:li>
    </rdf:Seq>
   </crs:ToneCurvePV2012>
   <crs:ToneCurvePV2012Red>
    <rdf:Seq>
     <rdf:li>0, 0</rdf:li>
     <rdf:li>255, 255</rdf:li>
    </rdf:Seq>
   </crs:ToneCurvePV2012Red>
   <crs:ToneCurvePV2012Green>
    <rdf:Seq>
     <rdf:li>0, 0</rdf:li>
     <rdf:li>255, 255</rdf:li>
    </rdf:Seq>
   </crs:ToneCurvePV2012Green>
   <crs:ToneCurvePV2012Blue>
    <rdf:Seq>
     <rdf:li>0, 0</rdf:li>
     <rdf:li>255, 255</rdf:li>
    </rdf:Seq>
   </crs:ToneCurvePV2012Blue>
   <crs:PointColors>
    <rdf:Seq>
     <rdf:li>1.522230, 0.818425, 0.090266, -0.380000, -0.170000, 0.000000, 0.500000, 0.000000, 0.330000, 0.670000, 1.000000, 0.090000, 0.640000, 1.000000, 1.000000, 0.000000, 0.150000, 0.510000, 1.000000</rdf:li>
     <rdf:li>0.234680, 0.497424, 0.215041, 0.180000, 0.080000, 0.260000, 0.500000, 0.000000, 0.330000, 0.670000, 1.000000, 0.000000, 0.320000, 0.680000, 1.000000, 0.000000, 0.320000, 0.680000, 1.000000</rdf:li>
     <rdf:li>4.648630, 0.272624, 0.154884, 0.000000, -0.080000, 0.000000, 0.500000, 0.000000, 0.330000, 0.670000, 1.000000, 0.000000, 0.090000, 0.450000, 1.000000, 0.000000, 0.250000, 0.610000, 1.000000</rdf:li>
    </rdf:Seq>
   </crs:PointColors>
   <crs:ColorVariance>
    <rdf:Seq>
     <rdf:li>0.000000</rdf:li>
     <rdf:li>0.000000</rdf:li>
     <rdf:li>0.000000</rdf:li>
    </rdf:Seq>
   </crs:ColorVariance>
   <crs:LensBlur
    crs:Version="1"
    crs:Active="false"
    crs:ImageOrientation="0"
    crs:FocalRange="0 0 100 100"
    crs:BlurAmount="50"
    crs:BokehShape="0"
    crs:BokehShapeDetail="0"
    crs:HighlightsThreshold="50"
    crs:HighlightsBoost="50"
    crs:CatEyeAmount="0"
    crs:CatEyeScale="100"
    crs:BokehAspect="0"
    crs:BokehRotation="0"
    crs:SphericalAberration="0"/>
   <crs:Look>
    <rdf:Description
     crs:Name="Adobe Color"
     crs:Amount="1"
     crs:UUID="B952C231111CD8E0ECCF14B86BAA7077"
     crs:SupportsAmount="false"
     crs:SupportsMonochrome="false"
     crs:SupportsOutputReferred="false"
     crs:Copyright="© 2018 Adobe Systems, Inc."
     crs:Stubbed="true">
    <crs:Group>
     <rdf:Alt>
      <rdf:li xml:lang="x-default">Profiles</rdf:li>
     </rdf:Alt>
    </crs:Group>
    </rdf:Description>
   </crs:Look>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>"""


def calculate_sharpness(image_array):
    """Calculate sharpness using Laplacian variance method"""
    try:
        # Convert to grayscale if needed
        if len(image_array.shape) == 3:
            gray = np.mean(image_array, axis=2)
        else:
            gray = image_array
        
        # Apply Laplacian operator
        laplacian = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
        
        # Convolve
        from scipy import signal
        filtered = signal.convolve2d(gray, laplacian, mode='valid')
        
        # Return variance as sharpness metric
        return float(np.var(filtered))
    except Exception as e:
        print(f"Sharpness calculation error: {e}")
        return 0


def analyze_photo(file_path, sharpness_threshold=100):
    """Analyze a photo for sharpness and orientation"""
    try:
        if not HAS_RAWPY:
            # Fallback: just check file size as proxy
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            is_sharp = file_size > 20  # Assume larger files are better quality
            is_horizontal = True  # Default assumption
            sharpness_score = file_size * 10
            width, height = 6000, 4000  # Default Sony ARW dimensions
        else:
            with rawpy.imread(file_path) as raw:
                # Get thumbnail for faster processing
                thumb = raw.extract_thumb()
                if thumb.format == rawpy.ThumbFormat.JPEG:
                    import io
                    from PIL import Image
                    img = Image.open(io.BytesIO(thumb.data))
                    width, height = img.size
                    img_array = np.array(img.convert('L'))  # Convert to grayscale
                else:
                    # Use postprocess for raw data
                    img_array = raw.postprocess(use_camera_wb=True, half_size=True)
                    height, width = img_array.shape[:2]
                
                # Calculate sharpness
                sharpness_score = calculate_sharpness(img_array)
                is_sharp = sharpness_score > sharpness_threshold
                is_horizontal = width > height
        
        return {
            'sharpness': sharpness_score,
            'is_sharp': is_sharp,
            'is_horizontal': is_horizontal,
            'width': width,
            'height': height,
            'selected': is_sharp and is_horizontal
        }
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return {
            'sharpness': 0,
            'is_sharp': False,
            'is_horizontal': True,
            'width': 0,
            'height': 0,
            'selected': False,
            'error': str(e)
        }


class PhotoSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Selector & Renamer")
        self.root.geometry("900x700")
        
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.project_name = tk.StringVar(value="Project")
        self.sharpness_threshold = tk.IntVar(value=100)
        self.photos = []
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input folder selection
        ttk.Label(main_frame, text="Input Folder:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_folder, width=50).grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.select_input_folder).grid(row=0, column=2, pady=5)
        
        # Output folder selection
        ttk.Label(main_frame, text="Output Folder:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_folder, width=50).grid(row=1, column=1, pady=5, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.select_output_folder).grid(row=1, column=2, pady=5)
        
        # Project name
        ttk.Label(main_frame, text="Project Name:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.project_name, width=50).grid(row=2, column=1, pady=5, padx=5)
        
        # Sharpness threshold
        ttk.Label(main_frame, text="Sharpness Threshold:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Scale(main_frame, from_=50, to=500, variable=self.sharpness_threshold, 
                  orient=tk.HORIZONTAL, length=300).grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(main_frame, textvariable=self.sharpness_threshold).grid(row=3, column=2, pady=5)
        
        # Analyze button
        ttk.Button(main_frame, text="Analyze Photos", command=self.analyze_photos, 
                   style='Accent.TButton').grid(row=4, column=1, pady=15)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, length=400, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, pady=10)
        
        # Results text area
        ttk.Label(main_frame, text="Results:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.results_text = scrolledtext.ScrolledText(main_frame, width=100, height=20)
        self.results_text.grid(row=7, column=0, columnspan=3, pady=5)
        
        # Process button
        self.process_btn = ttk.Button(main_frame, text="Process Selected Photos", 
                                       command=self.process_photos, state='disabled')
        self.process_btn.grid(row=8, column=1, pady=15)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
    
    def select_input_folder(self):
        folder = filedialog.askdirectory(title="Select Input Folder with ARW Photos")
        if folder:
            self.input_folder.set(folder)
    
    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
    
    def log_message(self, message):
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.root.update()
    
    def analyze_photos(self):
        input_dir = self.input_folder.get()
        if not input_dir or not os.path.exists(input_dir):
            messagebox.showerror("Error", "Please select a valid input folder")
            return
        
        if not self.output_folder.get():
            # Auto-set output folder
            output_dir = os.path.join(input_dir, "selected_photos")
            self.output_folder.set(output_dir)
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        self.photos = []
        
        # Find all ARW files
        arw_files = list(Path(input_dir).glob("*.ARW")) + list(Path(input_dir).glob("*.arw"))
        
        if not arw_files:
            messagebox.showwarning("Warning", "No ARW files found in the selected folder")
            return
        
        self.log_message(f"Found {len(arw_files)} ARW files. Analyzing...\n")
        self.progress.start()
        
        # Analyze in a separate thread
        thread = threading.Thread(target=self._analyze_thread, args=(arw_files,))
        thread.start()
    
    def _analyze_thread(self, arw_files):
        threshold = self.sharpness_threshold.get()
        
        for i, file_path in enumerate(arw_files):
            result = analyze_photo(str(file_path), threshold)
            result['path'] = str(file_path)
            result['filename'] = file_path.name
            self.photos.append(result)
            
            status = "✓ SELECTED" if result['selected'] else "✗ REJECTED"
            reason = []
            if not result['is_sharp']:
                reason.append("not sharp enough")
            if not result['is_horizontal']:
                reason.append("vertical orientation")
            
            reason_str = f" ({', '.join(reason)})" if reason else ""
            
            self.root.after(0, self.log_message, 
                          f"{file_path.name}: {status} "
                          f"[Sharpness: {result['sharpness']:.1f}, "
                          f"{result['width']}x{result['height']}]{reason_str}")
        
        selected_count = sum(1 for p in self.photos if p['selected'])
        self.root.after(0, self.log_message, 
                       f"\n{'='*60}\n"
                       f"Analysis complete!\n"
                       f"Total photos: {len(self.photos)}\n"
                       f"Selected: {selected_count}\n"
                       f"Rejected: {len(self.photos) - selected_count}\n"
                       f"{'='*60}\n")
        
        self.root.after(0, self.progress.stop)
        self.root.after(0, lambda: self.process_btn.config(state='normal'))
    
    def process_photos(self):
        output_dir = self.output_folder.get()
        if not output_dir:
            messagebox.showerror("Error", "Please select an output folder")
            return
        
        project = self.project_name.get().strip()
        if not project:
            messagebox.showerror("Error", "Please enter a project name")
            return
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        self.log_message("\nProcessing selected photos...\n")
        self.progress.start()
        self.process_btn.config(state='disabled')
        
        # Process in a separate thread
        thread = threading.Thread(target=self._process_thread, args=(output_dir, project))
        thread.start()
    
    def _process_thread(self, output_dir, project):
        selected_photos = [p for p in self.photos if p['selected']]
        
        for i, photo in enumerate(selected_photos, 1):
            try:
                # Create new filename
                new_name = f"{project}_{i:04d}.ARW"
                new_path = os.path.join(output_dir, new_name)
                
                # Copy the photo
                shutil.copy2(photo['path'], new_path)
                
                # Create XMP sidecar file
                xmp_path = os.path.join(output_dir, f"{project}_{i:04d}.xmp")
                with open(xmp_path, 'w', encoding='utf-8') as f:
                    f.write(XMP_PRESET)
                
                self.root.after(0, self.log_message, 
                              f"Processed: {photo['filename']} → {new_name}")
            except Exception as e:
                self.root.after(0, self.log_message, 
                              f"Error processing {photo['filename']}: {e}")
        
        self.root.after(0, self.log_message, 
                       f"\n{'='*60}\n"
                       f"Processing complete!\n"
                       f"Processed {len(selected_photos)} photos\n"
                       f"Output folder: {output_dir}\n"
                       f"{'='*60}\n")
        
        self.root.after(0, self.progress.stop)
        self.root.after(0, lambda: messagebox.showinfo("Success", 
                       f"Processed {len(selected_photos)} photos!\n\n"
                       f"Files saved to:\n{output_dir}"))


def main():
    if not HAS_RAWPY:
        print("\nWARNING: rawpy library not found!")
        print("Install it with: pip install rawpy numpy scipy Pillow")
        print("The app will run with limited functionality.\n")
    
    root = tk.Tk()
    app = PhotoSelectorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
