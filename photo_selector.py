#!/usr/bin/env python3
"""
Photo Selector - Automatic photo selection and conversion tool
For ARW raw photos - selects sharp images with focused faces and converts to JPEG
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
    from scipy import ndimage
    from PIL import Image
    import cv2
    HAS_RAWPY = True
    HAS_CV2 = True
except ImportError as e:
    HAS_RAWPY = False
    HAS_CV2 = False
    print(f"Import warning: {e}")

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


def generate_xmp_with_rotation(tilt_angle=0.0):
    """Generate XMP preset with rotation and auto-crop if tilt angle is detected"""
    # Parse the base XMP and add rotation parameters
    xmp = XMP_PRESET

    if abs(tilt_angle) > 0.1:  # Only add rotation if tilt is significant (> 0.1 degrees)
        # Add rotation parameters before the closing tags
        rotation_params = f"""   crs:StraightenAngle="{tilt_angle:.2f}"
   crs:CropConstrainToWarp="1"
   crs:HasCrop="True"
"""
        # Insert before the last crs attributes
        xmp = xmp.replace('   crs:AsShotTint="4">',
                         f'   crs:AsShotTint="4"\n{rotation_params}>')

    return xmp


def calculate_sharpness(image_array, face_regions=None):
    """Calculate sharpness using enhanced Laplacian variance method

    Args:
        image_array: The image to analyze
        face_regions: Optional list of face bounding boxes [(x, y, w, h), ...]
                     If provided, only analyzes sharpness on faces
    """
    try:
        # Convert to grayscale if needed
        if len(image_array.shape) == 3:
            gray = np.mean(image_array, axis=2)
        else:
            gray = image_array

        # Ensure proper data type
        gray = gray.astype(np.float64)

        # If face regions provided, only analyze those areas
        if face_regions and len(face_regions) > 0:
            face_sharpness_scores = []
            for (x, y, w, h) in face_regions:
                # Extract face region - focus on center (eyes/nose area) for better sharpness detection
                # Eyes are typically the sharpest point and most important for portraits
                center_factor = 0.6  # Focus on center 60% of face
                padding_x = int(w * (1 - center_factor) / 2)
                padding_y = int(h * (1 - center_factor) / 2)

                y1 = max(0, y + padding_y)
                y2 = min(gray.shape[0], y + h - padding_y)
                x1 = max(0, x + padding_x)
                x2 = min(gray.shape[1], x + w - padding_x)

                face_region = gray[y1:y2, x1:x2]

                if face_region.size == 0:
                    continue

                # Use OpenCV's Laplacian if available (faster and more accurate)
                if HAS_CV2:
                    # Convert to uint8 for OpenCV
                    face_uint8 = face_region.astype(np.uint8)

                    # Use Sobel gradient magnitude for more robust sharpness detection
                    # This is less sensitive to lighting and orientation
                    sobelx = cv2.Sobel(face_uint8, cv2.CV_64F, 1, 0, ksize=3)
                    sobely = cv2.Sobel(face_uint8, cv2.CV_64F, 0, 1, ksize=3)
                    gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)

                    # Calculate mean of gradient magnitude (normalized by region size)
                    score = float(np.mean(gradient_magnitude))
                else:
                    # Fallback: scipy implementation
                    laplacian = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
                    from scipy import signal
                    filtered = signal.convolve2d(face_region, laplacian, mode='valid')
                    score = float(np.var(filtered))

                face_sharpness_scores.append(score)

            # Return average sharpness across all faces
            return np.mean(face_sharpness_scores) if face_sharpness_scores else 0
        else:
            # No faces detected - analyze entire image
            if HAS_CV2:
                gray_uint8 = gray.astype(np.uint8)

                # Use Sobel gradient magnitude for more robust sharpness detection
                sobelx = cv2.Sobel(gray_uint8, cv2.CV_64F, 1, 0, ksize=3)
                sobely = cv2.Sobel(gray_uint8, cv2.CV_64F, 0, 1, ksize=3)
                gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)

                return float(np.mean(gradient_magnitude))
            else:
                laplacian = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
                from scipy import signal
                filtered = signal.convolve2d(gray, laplacian, mode='valid')
                return float(np.var(filtered))

    except Exception as e:
        print(f"Sharpness calculation error: {e}")
        return 0


def detect_faces(image_array):
    """Detect faces in the image using OpenCV Haar Cascade

    Returns:
        List of face bounding boxes [(x, y, w, h), ...]
    """
    try:
        if not HAS_CV2:
            return []

        # Convert to grayscale if needed
        if len(image_array.shape) == 3:
            gray = cv2.cvtColor(image_array.astype(np.uint8), cv2.COLOR_RGB2GRAY)
        else:
            gray = image_array.astype(np.uint8)

        # Load Haar Cascade classifier for face detection
        # Try multiple cascade files (different OpenCV versions store them differently)
        cascade_paths = [
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml',
            '/usr/local/share/opencv4/haarcascades/haarcascade_frontalface_default.xml',
            '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml',
        ]

        face_cascade = None
        for cascade_path in cascade_paths:
            if os.path.exists(cascade_path):
                face_cascade = cv2.CascadeClassifier(cascade_path)
                break

        if face_cascade is None or face_cascade.empty():
            # Try to load from cv2.data (most reliable method)
            try:
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            except:
                return []

        # Detect faces
        # Parameters tuned for portrait photography with stricter settings to reduce false positives
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=8,  # Increased from 5 to reduce false positives
            minSize=(60, 60),  # Increased minimum size to avoid detecting small artifacts
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        return [(x, y, w, h) for (x, y, w, h) in faces]

    except Exception as e:
        print(f"Face detection error: {e}")
        return []


def detect_horizon_angle(image_array):
    """Detect the tilt angle of the horizon/image using edge detection"""
    try:
        if not HAS_CV2:
            return 0.0

        # Convert to grayscale if needed
        if len(image_array.shape) == 3:
            gray = cv2.cvtColor(image_array.astype(np.uint8), cv2.COLOR_RGB2GRAY)
        else:
            gray = image_array.astype(np.uint8)

        # Apply Canny edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Detect lines using Hough Transform
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)

        if lines is None or len(lines) == 0:
            return 0.0

        # Calculate angles of detected lines
        angles = []
        for rho, theta in lines[:, 0]:
            # Convert from Hough space to degrees
            angle = (theta * 180 / np.pi) - 90
            # Normalize to -45 to +45 degrees range
            if angle > 45:
                angle -= 90
            elif angle < -45:
                angle += 90
            # Only consider small tilts (less than 10 degrees)
            if abs(angle) < 10:
                angles.append(angle)

        if not angles:
            return 0.0

        # Return median angle (more robust than mean)
        return float(np.median(angles))

    except Exception as e:
        print(f"Horizon detection error: {e}")
        return 0.0


def analyze_photo(file_path, sharpness_threshold=100, detect_tilt=False, include_vertical=True):
    """Analyze a photo for sharpness, orientation, and tilt angle

    Uses face detection to focus sharpness analysis on faces when present.
    """
    try:
        tilt_angle = 0.0
        face_count = 0
        if not HAS_RAWPY:
            # Fallback: just check file size as proxy
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            is_sharp = file_size > 20  # Assume larger files are better quality
            is_horizontal = True  # Default assumption
            sharpness_score = file_size * 10
            width, height = 6000, 4000  # Default Sony ARW dimensions
        else:
            with rawpy.imread(file_path) as raw:
                # For face detection, use higher resolution for better accuracy
                # Process at quarter size (half_size=True gives 1/2 dimensions = 1/4 pixels)
                img_array_color = raw.postprocess(use_camera_wb=True, half_size=False, output_bps=8)
                height, width = img_array_color.shape[:2]
                img_array = np.mean(img_array_color, axis=2).astype(np.uint8)

                # Detect faces first
                face_regions = detect_faces(img_array_color) if HAS_CV2 else []
                face_count = len(face_regions)

                # Calculate sharpness (focused on faces if detected)
                sharpness_score = calculate_sharpness(img_array, face_regions)
                is_sharp = sharpness_score > sharpness_threshold
                is_horizontal = width > height

                # Detect tilt angle if requested
                if detect_tilt and HAS_CV2:
                    tilt_angle = detect_horizon_angle(img_array_color)

        # Determine if photo should be selected based on filters
        # IMPORTANT: Only select photos with detected faces AND sharp
        has_faces = face_count > 0

        if include_vertical:
            # Select if sharp AND has faces, regardless of orientation
            selected = is_sharp and has_faces
        else:
            # Select only if sharp AND has faces AND horizontal
            selected = is_sharp and has_faces and is_horizontal

        return {
            'sharpness': sharpness_score,
            'is_sharp': is_sharp,
            'is_horizontal': is_horizontal,
            'width': width,
            'height': height,
            'tilt_angle': tilt_angle,
            'face_count': face_count,
            'selected': selected
        }
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return {
            'sharpness': 0,
            'is_sharp': False,
            'is_horizontal': True,
            'width': 0,
            'height': 0,
            'tilt_angle': 0.0,
            'face_count': 0,
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
        self.sharpness_threshold = tk.IntVar(value=15)
        self.auto_straighten = tk.BooleanVar(value=True)
        self.include_vertical = tk.BooleanVar(value=True)
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
        ttk.Scale(main_frame, from_=1, to=100, variable=self.sharpness_threshold,
                  orient=tk.HORIZONTAL, length=300).grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(main_frame, textvariable=self.sharpness_threshold).grid(row=3, column=2, pady=5)

        # Auto-straighten checkbox
        ttk.Checkbutton(main_frame, text="Auto-straighten tilted photos (detect and fix horizon tilt)",
                       variable=self.auto_straighten).grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)

        # Include vertical photos checkbox
        ttk.Checkbutton(main_frame, text="Include vertical/portrait photos (not just horizontal)",
                       variable=self.include_vertical).grid(row=5, column=1, sticky=tk.W, pady=5, padx=5)

        # Analyze button
        ttk.Button(main_frame, text="Analyze Photos", command=self.analyze_photos,
                   style='Accent.TButton').grid(row=6, column=1, pady=15)

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, length=400, mode='indeterminate')
        self.progress.grid(row=7, column=0, columnspan=3, pady=10)

        # Results text area
        ttk.Label(main_frame, text="Results:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.results_text = scrolledtext.ScrolledText(main_frame, width=100, height=20)
        self.results_text.grid(row=9, column=0, columnspan=3, pady=5)

        # Process button
        self.process_btn = ttk.Button(main_frame, text="Process Selected Photos",
                                       command=self.process_photos, state='disabled')
        self.process_btn.grid(row=10, column=1, pady=15)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(9, weight=1)
    
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
        detect_tilt = self.auto_straighten.get()
        include_vertical = self.include_vertical.get()

        for i, file_path in enumerate(arw_files):
            result = analyze_photo(str(file_path), threshold, detect_tilt, include_vertical)
            result['path'] = str(file_path)
            result['filename'] = file_path.name
            self.photos.append(result)

            status = "✓ SELECTED" if result['selected'] else "✗ REJECTED"
            reason = []
            if result.get('face_count', 0) == 0:
                reason.append("no faces detected")
            if not result['is_sharp']:
                reason.append("not sharp enough")
            if not include_vertical and not result['is_horizontal']:
                reason.append("vertical orientation")

            reason_str = f" ({', '.join(reason)})" if reason else ""

            tilt_info = ""
            if detect_tilt and abs(result.get('tilt_angle', 0)) > 0.1:
                tilt_info = f" [Tilt: {result['tilt_angle']:.2f}°]"

            face_info = ""
            if result.get('face_count', 0) > 0:
                face_info = f" [Faces: {result['face_count']}]"

            self.root.after(0, self.log_message,
                          f"{file_path.name}: {status} "
                          f"[Sharpness: {result['sharpness']:.1f}, "
                          f"{result['width']}x{result['height']}]{face_info}{reason_str}{tilt_info}")
        
        selected_count = sum(1 for p in self.photos if p['selected'])

        # Calculate sharpness statistics separately for photos with/without faces
        photos_with_faces = [p for p in self.photos if p.get('face_count', 0) > 0 and p['sharpness'] > 0]
        photos_without_faces = [p for p in self.photos if p.get('face_count', 0) == 0 and p['sharpness'] > 0]

        sharpness_stats = "\nSharpness Statistics:\n"

        if photos_with_faces:
            face_sharpness = [p['sharpness'] for p in photos_with_faces]
            min_sharp = min(face_sharpness)
            max_sharp = max(face_sharpness)
            avg_sharp = np.mean(face_sharpness)
            median_sharp = np.median(face_sharpness)

            # Calculate percentiles for better threshold suggestion
            percentile_25 = np.percentile(face_sharpness, 25)
            percentile_50 = np.percentile(face_sharpness, 50)
            percentile_75 = np.percentile(face_sharpness, 75)

            sharpness_stats += (f"  Photos WITH faces ({len(photos_with_faces)} photos):\n"
                              f"    Min: {min_sharp:.1f}\n"
                              f"    25th percentile: {percentile_25:.1f}\n"
                              f"    Median (50th): {median_sharp:.1f}\n"
                              f"    75th percentile: {percentile_75:.1f}\n"
                              f"    Max: {max_sharp:.1f}\n"
                              f"    Average: {avg_sharp:.1f}\n"
                              f"    Suggested threshold (conservative): {percentile_25:.1f}\n"
                              f"    Suggested threshold (moderate): {median_sharp * 0.6:.1f}\n"
                              f"    Suggested threshold (strict): {median_sharp * 0.8:.1f}\n\n")

        if photos_without_faces:
            no_face_sharpness = [p['sharpness'] for p in photos_without_faces]
            min_sharp = min(no_face_sharpness)
            max_sharp = max(no_face_sharpness)
            avg_sharp = np.mean(no_face_sharpness)
            median_sharp = np.median(no_face_sharpness)

            sharpness_stats += (f"  Photos WITHOUT faces ({len(photos_without_faces)} photos):\n"
                              f"    Min: {min_sharp:.1f}\n"
                              f"    Max: {max_sharp:.1f}\n"
                              f"    Average: {avg_sharp:.1f}\n"
                              f"    Median: {median_sharp:.1f}\n"
                              f"    Suggested threshold: {median_sharp * 0.7:.1f} (70% of median)\n\n")

        sharpness_stats += f"  Current threshold: {threshold}\n"

        self.root.after(0, self.log_message,
                       f"\n{'='*60}\n"
                       f"Analysis complete!\n"
                       f"Total photos: {len(self.photos)}\n"
                       f"Selected: {selected_count}\n"
                       f"Rejected: {len(self.photos) - selected_count}\n"
                       f"{sharpness_stats}"
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
                # Extract original number from filename (e.g., DSC00595 -> 00595)
                import re
                original_filename = Path(photo['filename']).stem  # Remove extension

                # Try to extract number from various Sony camera filename formats
                # DSC00595, _DSC0001, etc.
                number_match = re.search(r'(\d{4,5})$', original_filename)

                if number_match:
                    # Use original number from filename
                    photo_number = number_match.group(1)
                    new_name = f"{project}_{photo_number}.jpg"
                else:
                    # Fallback to sequential numbering if no number found
                    new_name = f"{project}_{i:04d}.jpg"

                new_path = os.path.join(output_dir, new_name)

                if not HAS_RAWPY:
                    # Fallback: just copy the ARW file if rawpy not available
                    arw_name = f"{project}_{i:04d}.ARW"
                    arw_path = os.path.join(output_dir, arw_name)
                    shutil.copy2(photo['path'], arw_path)
                    self.root.after(0, self.log_message,
                                  f"Copied: {photo['filename']} → {arw_name} (rawpy not available)")
                else:
                    # Convert RAW to JPEG
                    with rawpy.imread(photo['path']) as raw:
                        # Process the RAW file with camera white balance
                        rgb = raw.postprocess(
                            use_camera_wb=True,
                            half_size=False,  # Full resolution
                            no_auto_bright=False,
                            output_bps=8
                        )

                        # Convert to PIL Image
                        img = Image.fromarray(rgb)
                        original_width, original_height = img.size

                        # Apply rotation if tilt was detected
                        tilt_angle = photo.get('tilt_angle', 0.0)
                        if abs(tilt_angle) > 0.1:
                            # Rotate to correct tilt (negative to correct, expand to avoid clipping)
                            rotated = img.rotate(-tilt_angle, expand=True, resample=Image.BICUBIC)

                            # Calculate the scale needed to fill the original frame after rotation
                            # When rotating, the image gets larger - we need to crop and zoom to fill
                            new_width, new_height = rotated.size

                            # Calculate how much we need to zoom to ensure NO black borders at all
                            # after cropping back to original aspect ratio
                            import math
                            angle_rad = abs(math.radians(tilt_angle))

                            # Calculate the scale factor needed to completely eliminate black corners
                            # This uses a more aggressive calculation to ensure full coverage
                            # For a rotated rectangle to fit inside the original, we need:
                            scale = 1.0 / (math.cos(angle_rad) - math.sin(angle_rad) *
                                          min(original_width / original_height, original_height / original_width))

                            # Add extra zoom buffer (5-10%) to ensure absolutely no black edges
                            scale *= 1.10  # 10% extra zoom to guarantee no black edges

                            # Resize (zoom) to fill the frame with buffer
                            zoom_width = int(new_width * scale)
                            zoom_height = int(new_height * scale)
                            rotated = rotated.resize((zoom_width, zoom_height), Image.BICUBIC)

                            # Crop from center to original dimensions
                            left = (zoom_width - original_width) // 2
                            top = (zoom_height - original_height) // 2
                            right = left + original_width
                            bottom = top + original_height

                            img = rotated.crop((left, top, right, bottom))

                        # Save as JPEG with high quality
                        img.save(new_path, 'JPEG', quality=95, optimize=True)

                    # Generate and save XMP sidecar file with preset
                    xmp_path = new_path.replace('.jpg', '.xmp')
                    xmp_content = generate_xmp_with_rotation(tilt_angle)
                    with open(xmp_path, 'w', encoding='utf-8') as xmp_file:
                        xmp_file.write(xmp_content)

                    tilt_msg = f" (straightened {abs(tilt_angle):.2f}°)" if abs(tilt_angle) > 0.1 else ""
                    self.root.after(0, self.log_message,
                                  f"Converted: {photo['filename']} → {new_name}{tilt_msg} + XMP")
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
