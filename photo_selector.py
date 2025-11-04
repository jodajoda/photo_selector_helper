#!/usr/bin/env python3
"""
Photo Selector - Automatic photo selection and conversion tool
For ARW raw photos - selects sharp images with focused faces and converts to JPEG
"""

import os
import sys
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

# XMP sidecar template (converted from preset to sidecar format)
XMP_PRESET = """<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 7.0-c000 1.000000, 0000/00/00-00:00:00        ">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
    xmlns:xmp="http://ns.adobe.com/xap/1.0/"
    xmlns:photoshop="http://ns.adobe.com/photoshop/1.0/"
    xmlns:crd="http://ns.adobe.com/camera-raw-defaults/1.0/"
    xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/"
   photoshop:SidecarForExtension="ARW"
   crd:CameraProfile="Adobe Standard"
   crs:Version="18.0"
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
   crs:Sharpness="40"
   crs:SharpenRadius="+1.0"
   crs:SharpenDetail="25"
   crs:SharpenEdgeMasking="0"
   crs:LuminanceSmoothing="0"
   crs:ColorNoiseReduction="25"
   crs:ColorNoiseReductionDetail="50"
   crs:ColorNoiseReductionSmoothness="50"
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
   crs:GrainAmount="0"
   crs:PostCropVignetteAmount="0"
   crs:ShadowTint="0"
   crs:RedHue="0"
   crs:RedSaturation="-14"
   crs:GreenHue="0"
   crs:GreenSaturation="0"
   crs:BlueHue="0"
   crs:BlueSaturation="0"
   crs:HDREditMode="0"
   crs:CurveRefineSaturation="100"
   crs:OverrideLookVignette="False"
   crs:ToneCurveName2012="Custom"
   crs:CameraProfile="Adobe Standard"
   crs:CameraProfileDigest="8231747EC38F3123A793D07144E134B4"
   crs:HasSettings="True"
   crs:HasCrop="False"
   crs:AlreadyApplied="False">
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
    crs:FocalRange="-80 0 100 180"
    crs:FocalRangeSource="3"
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


def generate_xmp_with_rotation(tilt_angle=0.0, base_xmp=None):
    """Generate XMP preset with rotation and auto-crop if tilt angle is detected

    Args:
        tilt_angle: Rotation angle in degrees
        base_xmp: Optional custom XMP content to use instead of built-in preset
    """
    # Use custom XMP or built-in preset
    xmp = base_xmp if base_xmp else XMP_PRESET

    if abs(tilt_angle) > 0.1:  # Only add rotation if tilt is significant (> 0.1 degrees)
        # Add rotation parameters before the closing tag
        rotation_params = f'   crs:StraightenAngle="{tilt_angle:.2f}"'

        # Replace HasCrop flag when rotation is applied
        xmp = xmp.replace('crs:HasCrop="False"', 'crs:HasCrop="True"')

        # Try to find a good insertion point for the rotation parameter
        # Look for common closing patterns in XMP files
        if 'crs:AlreadyApplied="False">' in xmp:
            # Insert before the closing bracket after AlreadyApplied
            xmp = xmp.replace('crs:AlreadyApplied="False">',
                            f'crs:AlreadyApplied="False"\n{rotation_params}>')
        elif 'crs:HasCrop="True">' in xmp:
            # Insert after HasCrop if it was just changed
            xmp = xmp.replace('crs:HasCrop="True">',
                            f'crs:HasCrop="True"\n{rotation_params}>')
        else:
            # Fallback: insert before the first closing rdf:Description tag
            xmp = xmp.replace('  </rdf:Description>',
                            f'{rotation_params}\n  </rdf:Description>', 1)

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
        # Also check bundled location for PyInstaller apps
        bundled_cascade = None
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            bundle_dir = sys._MEIPASS
            bundled_cascade = os.path.join(bundle_dir, 'cv2', 'data', 'haarcascade_frontalface_default.xml')

        cascade_paths = [
            bundled_cascade,  # Try bundled location first
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml',
            '/usr/local/share/opencv4/haarcascades/haarcascade_frontalface_default.xml',
            '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml',
        ]

        face_cascade = None
        for cascade_path in cascade_paths:
            if cascade_path and os.path.exists(cascade_path):
                face_cascade = cv2.CascadeClassifier(cascade_path)
                if not face_cascade.empty():
                    break

        if face_cascade is None or face_cascade.empty():
            # Try to load from cv2.data (most reliable method)
            try:
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            except:
                print("WARNING: Could not load face detection cascade - no photos will be selected!")
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


def calculate_brightness(image_array):
    """Calculate the average brightness/luminance of an image

    Returns:
        float: Average brightness value (0-255 scale)
    """
    try:
        # Convert to grayscale if needed
        if len(image_array.shape) == 3:
            # Use perceptual luminance formula (Y = 0.299*R + 0.587*G + 0.114*B)
            gray = 0.299 * image_array[:,:,0] + 0.587 * image_array[:,:,1] + 0.114 * image_array[:,:,2]
        else:
            gray = image_array

        # Calculate mean brightness
        brightness = float(np.mean(gray))
        return brightness

    except Exception as e:
        print(f"Brightness calculation error: {e}")
        return 128.0  # Return neutral brightness on error


def analyze_photo(file_path, sharpness_threshold=100, detect_tilt=False, include_vertical=True, max_brightness=255, min_brightness=0):
    """Analyze a photo for sharpness, orientation, tilt angle, and brightness

    Uses face detection to focus sharpness analysis on faces when present.
    Rejects photos that are too bright (burned out/overexposed) or too dark (underexposed/faded).

    Args:
        file_path: Path to the photo file
        sharpness_threshold: Minimum sharpness score required
        detect_tilt: Whether to detect and measure horizon tilt
        include_vertical: Whether to include vertical/portrait photos
        max_brightness: Maximum brightness threshold (reject if exceeded)
        min_brightness: Minimum brightness threshold (reject if below)
    """
    try:
        tilt_angle = 0.0
        face_count = 0
        brightness = 128.0  # Default mid-brightness
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

                # Calculate brightness
                brightness = calculate_brightness(img_array_color)

                # Detect tilt angle if requested
                if detect_tilt and HAS_CV2:
                    tilt_angle = detect_horizon_angle(img_array_color)

        # Determine if photo should be selected based on filters
        # IMPORTANT: Only select photos with detected faces AND sharp AND not burned out AND not too dark
        has_faces = face_count > 0
        is_not_burned_out = brightness <= max_brightness
        is_not_too_dark = brightness >= min_brightness

        if include_vertical:
            # Select if sharp AND has faces AND not burned out AND not too dark, regardless of orientation
            selected = is_sharp and has_faces and is_not_burned_out and is_not_too_dark
        else:
            # Select only if sharp AND has faces AND horizontal AND not burned out AND not too dark
            selected = is_sharp and has_faces and is_horizontal and is_not_burned_out and is_not_too_dark

        return {
            'sharpness': sharpness_score,
            'is_sharp': is_sharp,
            'is_horizontal': is_horizontal,
            'width': width,
            'height': height,
            'tilt_angle': tilt_angle,
            'face_count': face_count,
            'brightness': brightness,
            'is_burned_out': brightness > max_brightness,
            'is_too_dark': brightness < min_brightness,
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
            'brightness': 128.0,
            'is_burned_out': False,
            'is_too_dark': False,
            'selected': False,
            'error': str(e)
        }


class PhotoSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Selector & Renamer")
        self.root.geometry("1000x900")

        # Modern light color scheme
        self.colors = {
            'bg': '#f5f7fa',           # Light gray background
            'card': '#ffffff',         # White card background
            'accent': '#7c3aed',       # Purple accent
            'accent_hover': '#6d28d9', # Darker purple hover
            'success': '#059669',      # Green
            'text': '#1f2937',         # Dark text
            'text_secondary': '#6b7280', # Secondary gray text
            'border': '#e5e7eb',       # Light border
            'input_bg': '#f9fafb',     # Light input background
            'input_border': '#d1d5db'  # Input border
        }

        # Configure root background
        self.root.configure(bg=self.colors['bg'])

        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.project_name = tk.StringVar(value="Project")
        self.sharpness_threshold = tk.IntVar(value=20)
        self.brightness_threshold = tk.IntVar(value=100)  # Brightness threshold (0-255) to separate dark/light
        self.min_brightness_threshold = tk.IntVar(value=30)  # Minimum brightness threshold (reject too dark/faded images)
        self.max_brightness_threshold = tk.IntVar(value=220)  # Maximum brightness threshold (reject burned out images)
        self.auto_straighten = tk.BooleanVar(value=True)
        self.preset_file = tk.StringVar(value="(Using built-in preset)")
        self.custom_xmp_content = None
        # Separate presets for dark and light photos
        self.preset_file_dark = tk.StringVar(value="(Using built-in preset)")
        self.custom_xmp_content_dark = None
        self.preset_file_light = tk.StringVar(value="(Using built-in preset)")
        self.custom_xmp_content_light = None
        self.watermark_file = tk.StringVar(value="(Using built-in camera icon)")
        self.watermark_path = None
        self.photos = []

        self.setup_styles()
        self.create_widgets()

        # Update header title when project name changes
        self.project_name.trace_add('write', self._update_title)

        # Auto-load watermark.png if it exists in the same directory
        self._load_default_watermark()

    def setup_styles(self):
        """Setup custom ttk styles for modern appearance"""
        style = ttk.Style()

        # Try to use a modern theme as base
        try:
            style.theme_use('clam')
        except:
            pass

        # Configure Frame styles
        style.configure('Card.TFrame',
                       background=self.colors['card'],
                       relief='solid',
                       borderwidth=1,
                       bordercolor=self.colors['border'])

        style.configure('TFrame',
                       background=self.colors['bg'])

        # Configure Label styles
        style.configure('Title.TLabel',
                       background=self.colors['card'],
                       foreground=self.colors['text'],
                       font=('SF Pro Display', 24, 'bold'))

        style.configure('Subtitle.TLabel',
                       background=self.colors['card'],
                       foreground=self.colors['text_secondary'],
                       font=('SF Pro Text', 11))

        style.configure('TLabel',
                       background=self.colors['card'],
                       foreground=self.colors['text'],
                       font=('SF Pro Text', 12))

        style.configure('Secondary.TLabel',
                       background=self.colors['card'],
                       foreground=self.colors['text_secondary'],
                       font=('SF Pro Text', 10))

        # Configure Entry styles
        style.configure('TEntry',
                       fieldbackground=self.colors['input_bg'],
                       background=self.colors['input_bg'],
                       foreground=self.colors['text'],
                       borderwidth=1,
                       relief='flat')

        # Configure Button styles
        style.configure('Primary.TButton',
                       background=self.colors['accent'],
                       foreground='white',
                       borderwidth=0,
                       relief='flat',
                       font=('SF Pro Text', 12, 'bold'),
                       padding=(20, 12))

        style.map('Primary.TButton',
                 background=[('active', self.colors['accent_hover']),
                           ('pressed', self.colors['accent_hover'])])

        style.configure('Secondary.TButton',
                       background=self.colors['card'],
                       foreground=self.colors['text'],
                       borderwidth=1,
                       relief='flat',
                       font=('SF Pro Text', 11),
                       padding=(15, 8))

        style.map('Secondary.TButton',
                 background=[('active', self.colors['border']),
                           ('pressed', self.colors['border'])])

        # Configure Checkbutton styles
        style.configure('TCheckbutton',
                       background=self.colors['card'],
                       foreground=self.colors['text'],
                       font=('SF Pro Text', 11))

        # Configure Progressbar
        style.configure('TProgressbar',
                       background=self.colors['accent'],
                       troughcolor=self.colors['border'],
                       borderwidth=0,
                       relief='flat')

    def create_widgets(self):
        # Main container with padding
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # ===== HEADER SECTION =====
        header_card = ttk.Frame(main_frame, style='Card.TFrame')
        header_card.pack(fill=tk.X, pady=(0, 20))

        header_content = tk.Frame(header_card, bg=self.colors['card'])
        header_content.pack(fill=tk.X, padx=25, pady=20)

        # Title shows project name dynamically
        self.title_var = tk.StringVar(value="Photo Selector")
        title_label = ttk.Label(header_content, textvariable=self.title_var, style='Title.TLabel')
        title_label.pack(anchor=tk.W)

        subtitle_label = ttk.Label(header_content,
                                   text="Automatic photo selection with face detection and preset application",
                                   style='Subtitle.TLabel')
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))

        # ===== SETTINGS CARD =====
        settings_card = ttk.Frame(main_frame, style='Card.TFrame')
        settings_card.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Create a canvas with scrollbar for settings
        settings_canvas = tk.Canvas(settings_card, bg=self.colors['card'], highlightthickness=0, height=350)
        settings_scrollbar = tk.Scrollbar(settings_card, orient="vertical", command=settings_canvas.yview)
        settings_scrollable_frame = tk.Frame(settings_canvas, bg=self.colors['card'])

        settings_scrollable_frame.bind(
            "<Configure>",
            lambda e: settings_canvas.configure(scrollregion=settings_canvas.bbox("all"))
        )

        settings_canvas.create_window((0, 0), window=settings_scrollable_frame, anchor="nw")
        settings_canvas.configure(yscrollcommand=settings_scrollbar.set)

        settings_canvas.pack(side="left", fill="both", expand=True, padx=(25, 0), pady=20)
        settings_scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=20)

        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            settings_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        settings_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        settings_content = settings_scrollable_frame

        # Input folder
        self._create_folder_field(settings_content, "Input Folder",
                                 self.input_folder, self.select_input_folder, 0)

        # Output folder
        self._create_folder_field(settings_content, "Output Folder",
                                 self.output_folder, self.select_output_folder, 1)

        # Separator
        separator1 = tk.Frame(settings_content, height=1, bg=self.colors['border'])
        separator1.pack(fill=tk.X, pady=15)

        # Project name
        project_label = ttk.Label(settings_content, text="Project Name", style='TLabel')
        project_label.pack(anchor=tk.W, pady=(0, 8))

        project_entry = tk.Entry(settings_content,
                                textvariable=self.project_name,
                                font=('SF Pro Text', 12),
                                bg=self.colors['input_bg'],
                                fg=self.colors['text'],
                                insertbackground=self.colors['text'],
                                relief='flat',
                                bd=0)
        project_entry.pack(fill=tk.X, ipady=6, ipadx=12)

        # Separator
        separator2 = tk.Frame(settings_content, height=1, bg=self.colors['border'])
        separator2.pack(fill=tk.X, pady=15)

        # Sharpness threshold
        threshold_label = ttk.Label(settings_content,
                                    text=f"Sharpness Threshold",
                                    style='TLabel')
        threshold_label.pack(anchor=tk.W, pady=(0, 8))

        threshold_container = tk.Frame(settings_content, bg=self.colors['card'])
        threshold_container.pack(fill=tk.X)

        self.threshold_scale = tk.Scale(
            threshold_container,
            from_=2,
            to=50,
            resolution=2,
            variable=self.sharpness_threshold,
            orient=tk.HORIZONTAL,
            bg=self.colors['card'],
            fg=self.colors['text'],
            troughcolor=self.colors['input_bg'],
            highlightthickness=0,
            sliderrelief='raised',
            sliderlength=20,
            width=12,
            activebackground=self.colors['accent'],
            font=('SF Pro Text', 10),
            length=400
        )
        self.threshold_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        threshold_value_label = tk.Label(threshold_container,
                                        textvariable=self.sharpness_threshold,
                                        font=('SF Pro Text', 14, 'bold'),
                                        bg=self.colors['card'],
                                        fg=self.colors['accent'],
                                        width=4)
        threshold_value_label.pack(side=tk.LEFT, padx=15)

        # Separator
        separator3 = tk.Frame(settings_content, height=1, bg=self.colors['border'])
        separator3.pack(fill=tk.X, pady=15)

        # Brightness threshold
        brightness_label = ttk.Label(settings_content,
                                    text=f"Brightness Threshold (separate dark/light photos)",
                                    style='TLabel')
        brightness_label.pack(anchor=tk.W, pady=(0, 8))

        brightness_container = tk.Frame(settings_content, bg=self.colors['card'])
        brightness_container.pack(fill=tk.X)

        self.brightness_scale = tk.Scale(
            brightness_container,
            from_=50,
            to=200,
            resolution=5,
            variable=self.brightness_threshold,
            orient=tk.HORIZONTAL,
            bg=self.colors['card'],
            fg=self.colors['text'],
            troughcolor=self.colors['input_bg'],
            highlightthickness=0,
            sliderrelief='raised',
            sliderlength=20,
            width=12,
            activebackground=self.colors['accent'],
            font=('SF Pro Text', 10),
            length=400
        )
        self.brightness_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        brightness_value_label = tk.Label(brightness_container,
                                        textvariable=self.brightness_threshold,
                                        font=('SF Pro Text', 14, 'bold'),
                                        bg=self.colors['card'],
                                        fg=self.colors['accent'],
                                        width=4)
        brightness_value_label.pack(side=tk.LEFT, padx=15)

        # Help text for brightness threshold
        brightness_help = ttk.Label(settings_content,
                                   text="Photos below this value will use dark preset, above will use light preset",
                                   style='Secondary.TLabel')
        brightness_help.pack(anchor=tk.W, pady=(5, 0))

        # Separator
        separator3b = tk.Frame(settings_content, height=1, bg=self.colors['border'])
        separator3b.pack(fill=tk.X, pady=15)

        # Minimum brightness threshold (reject too dark images)
        min_brightness_label = ttk.Label(settings_content,
                                        text=f"Minimum Brightness (reject too dark/faded images)",
                                        style='TLabel')
        min_brightness_label.pack(anchor=tk.W, pady=(0, 8))

        min_brightness_container = tk.Frame(settings_content, bg=self.colors['card'])
        min_brightness_container.pack(fill=tk.X)

        self.min_brightness_scale = tk.Scale(
            min_brightness_container,
            from_=0,
            to=80,
            resolution=5,
            variable=self.min_brightness_threshold,
            orient=tk.HORIZONTAL,
            bg=self.colors['card'],
            fg=self.colors['text'],
            troughcolor=self.colors['input_bg'],
            highlightthickness=0,
            sliderrelief='raised',
            sliderlength=20,
            width=12,
            activebackground=self.colors['accent'],
            font=('SF Pro Text', 10),
            length=400
        )
        self.min_brightness_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        min_brightness_value_label = tk.Label(min_brightness_container,
                                             textvariable=self.min_brightness_threshold,
                                             font=('SF Pro Text', 14, 'bold'),
                                             bg=self.colors['card'],
                                             fg=self.colors['accent'],
                                             width=4)
        min_brightness_value_label.pack(side=tk.LEFT, padx=15)

        # Help text for min brightness
        min_brightness_help = ttk.Label(settings_content,
                                       text="Photos below this value will be rejected (underexposed/faded)",
                                       style='Secondary.TLabel')
        min_brightness_help.pack(anchor=tk.W, pady=(5, 0))

        # Separator
        separator3c = tk.Frame(settings_content, height=1, bg=self.colors['border'])
        separator3c.pack(fill=tk.X, pady=15)

        # Maximum brightness threshold (reject burned out images)
        max_brightness_label = ttk.Label(settings_content,
                                        text=f"Maximum Brightness (reject burned out images)",
                                        style='TLabel')
        max_brightness_label.pack(anchor=tk.W, pady=(0, 8))

        max_brightness_container = tk.Frame(settings_content, bg=self.colors['card'])
        max_brightness_container.pack(fill=tk.X)

        self.max_brightness_scale = tk.Scale(
            max_brightness_container,
            from_=180,
            to=255,
            resolution=5,
            variable=self.max_brightness_threshold,
            orient=tk.HORIZONTAL,
            bg=self.colors['card'],
            fg=self.colors['text'],
            troughcolor=self.colors['input_bg'],
            highlightthickness=0,
            sliderrelief='raised',
            sliderlength=20,
            width=12,
            activebackground=self.colors['accent'],
            font=('SF Pro Text', 10),
            length=400
        )
        self.max_brightness_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        max_brightness_value_label = tk.Label(max_brightness_container,
                                             textvariable=self.max_brightness_threshold,
                                             font=('SF Pro Text', 14, 'bold'),
                                             bg=self.colors['card'],
                                             fg=self.colors['accent'],
                                             width=4)
        max_brightness_value_label.pack(side=tk.LEFT, padx=15)

        # Help text for max brightness
        max_brightness_help = ttk.Label(settings_content,
                                       text="Photos above this value will be rejected (overexposed/burned out)",
                                       style='Secondary.TLabel')
        max_brightness_help.pack(anchor=tk.W, pady=(5, 0))

        # Separator
        separator3d = tk.Frame(settings_content, height=1, bg=self.colors['border'])
        separator3d.pack(fill=tk.X, pady=15)

        # Checkboxes
        check_auto = ttk.Checkbutton(settings_content,
                                    text="Auto-straighten tilted photos",
                                    variable=self.auto_straighten,
                                    style='TCheckbutton')
        check_auto.pack(anchor=tk.W, pady=5)

        # Separator
        separator4 = tk.Frame(settings_content, height=1, bg=self.colors['border'])
        separator4.pack(fill=tk.X, pady=15)

        # XMP Presets for Dark and Light Photos
        presets_container = tk.Frame(settings_content, bg=self.colors['card'])
        presets_container.pack(fill=tk.X)

        # Dark Photos Preset (left side)
        preset_dark_frame = tk.Frame(presets_container, bg=self.colors['card'])
        preset_dark_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))

        preset_dark_label = ttk.Label(preset_dark_frame, text="XMP Preset (Dark Photos)", style='TLabel')
        preset_dark_label.pack(anchor=tk.W, pady=(0, 8))

        preset_dark_info = ttk.Label(preset_dark_frame,
                               textvariable=self.preset_file_dark,
                               style='Secondary.TLabel')
        preset_dark_info.pack(anchor=tk.W, pady=(0, 10))

        preset_dark_btn_container = tk.Frame(preset_dark_frame, bg=self.colors['card'])
        preset_dark_btn_container.pack(fill=tk.X)

        preset_dark_custom_btn = ttk.Button(preset_dark_btn_container,
                                      text="Select Preset",
                                      command=self.select_preset_file_dark,
                                      style='Secondary.TButton')
        preset_dark_custom_btn.pack(side=tk.LEFT, padx=(0, 10))

        preset_dark_builtin_btn = ttk.Button(preset_dark_btn_container,
                                       text="Use Built-in",
                                       command=self.use_builtin_preset_dark,
                                       style='Secondary.TButton')
        preset_dark_builtin_btn.pack(side=tk.LEFT)

        # Light Photos Preset (right side)
        preset_light_frame = tk.Frame(presets_container, bg=self.colors['card'])
        preset_light_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        preset_light_label = ttk.Label(preset_light_frame, text="XMP Preset (Light Photos)", style='TLabel')
        preset_light_label.pack(anchor=tk.W, pady=(0, 8))

        preset_light_info = ttk.Label(preset_light_frame,
                               textvariable=self.preset_file_light,
                               style='Secondary.TLabel')
        preset_light_info.pack(anchor=tk.W, pady=(0, 10))

        preset_light_btn_container = tk.Frame(preset_light_frame, bg=self.colors['card'])
        preset_light_btn_container.pack(fill=tk.X)

        preset_light_custom_btn = ttk.Button(preset_light_btn_container,
                                      text="Select Preset",
                                      command=self.select_preset_file_light,
                                      style='Secondary.TButton')
        preset_light_custom_btn.pack(side=tk.LEFT, padx=(0, 10))

        preset_light_builtin_btn = ttk.Button(preset_light_btn_container,
                                       text="Use Built-in",
                                       command=self.use_builtin_preset_light,
                                       style='Secondary.TButton')
        preset_light_builtin_btn.pack(side=tk.LEFT)

        # Separator
        separator5 = tk.Frame(settings_content, height=1, bg=self.colors['border'])
        separator5.pack(fill=tk.X, pady=15)

        # PDF Watermark
        watermark_frame = tk.Frame(settings_content, bg=self.colors['card'])
        watermark_frame.pack(fill=tk.X)

        watermark_label = ttk.Label(watermark_frame, text="PDF Watermark", style='TLabel')
        watermark_label.pack(anchor=tk.W, pady=(0, 8))

        watermark_info = ttk.Label(watermark_frame,
                                   textvariable=self.watermark_file,
                                   style='Secondary.TLabel')
        watermark_info.pack(anchor=tk.W, pady=(0, 10))

        watermark_btn_container = tk.Frame(watermark_frame, bg=self.colors['card'])
        watermark_btn_container.pack(fill=tk.X)

        watermark_select_btn = ttk.Button(watermark_btn_container,
                                         text="Select Image",
                                         command=self.select_watermark_file,
                                         style='Secondary.TButton')
        watermark_select_btn.pack(side=tk.LEFT, padx=(0, 10))

        watermark_clear_btn = ttk.Button(watermark_btn_container,
                                        text="Use Default",
                                        command=self.clear_watermark,
                                        style='Secondary.TButton')
        watermark_clear_btn.pack(side=tk.LEFT)

        # ===== ACTION BUTTONS =====
        action_container = tk.Frame(main_frame, bg=self.colors['bg'])
        action_container.pack(fill=tk.X, pady=(0, 15))

        analyze_btn = ttk.Button(action_container,
                                text="Analyze Photos",
                                command=self.analyze_photos,
                                style='Primary.TButton')
        analyze_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

        self.process_btn = ttk.Button(action_container,
                                     text="Process Selected Photos",
                                     command=self.process_photos,
                                     state='disabled',
                                     style='Primary.TButton')
        self.process_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # ===== PROGRESS BAR & STATUS =====
        progress_container = tk.Frame(main_frame, bg=self.colors['bg'])
        progress_container.pack(fill=tk.X, pady=(0, 15))

        # Status label above progress bar
        self.status_label = tk.Label(progress_container,
                                     text="Ready",
                                     font=('SF Pro Text', 11),
                                     bg=self.colors['bg'],
                                     fg=self.colors['text_secondary'])
        self.status_label.pack(anchor=tk.W, pady=(0, 5))

        self.progress = ttk.Progressbar(progress_container,
                                       mode='determinate',
                                       style='TProgressbar')
        self.progress.pack(fill=tk.X, ipady=3)

        # ===== RESULTS SECTION =====
        results_card = ttk.Frame(main_frame, style='Card.TFrame')
        results_card.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        results_header = tk.Frame(results_card, bg=self.colors['card'])
        results_header.pack(fill=tk.X, padx=25, pady=(20, 10))

        results_title = ttk.Label(results_header, text="Results", style='TLabel')
        results_title.pack(anchor=tk.W)

        results_text_container = tk.Frame(results_card, bg=self.colors['card'])
        results_text_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 20))

        self.results_text = scrolledtext.ScrolledText(
            results_text_container,
            font=('SF Mono', 11),
            bg='#ffffff',
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            relief='solid',
            borderwidth=1,
            highlightthickness=0,
            padx=15,
            pady=15,
            wrap=tk.WORD,
            height=10
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for colored output
        self.results_text.tag_config('success', foreground=self.colors['success'], font=('SF Mono', 11, 'bold'))
        self.results_text.tag_config('accent', foreground=self.colors['accent'], font=('SF Mono', 11, 'bold'))
        self.results_text.tag_config('secondary', foreground=self.colors['text_secondary'])
        self.results_text.tag_config('error', foreground='#dc2626', font=('SF Mono', 11, 'bold'))
        self.results_text.tag_config('info', foreground='#0284c7', font=('SF Mono', 11))
        self.results_text.tag_config('warning', foreground='#ea580c')

        # ===== LOG SECTION =====
        log_card = ttk.Frame(main_frame, style='Card.TFrame')
        log_card.pack(fill=tk.BOTH, expand=True)

        log_header = tk.Frame(log_card, bg=self.colors['card'])
        log_header.pack(fill=tk.X, padx=25, pady=(20, 10))

        log_title = ttk.Label(log_header, text="Activity Log", style='TLabel')
        log_title.pack(anchor=tk.W)

        log_text_container = tk.Frame(log_card, bg=self.colors['card'])
        log_text_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 20))

        self.log_text = scrolledtext.ScrolledText(
            log_text_container,
            font=('SF Mono', 10),
            bg='#ffffff',
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            relief='solid',
            borderwidth=1,
            highlightthickness=0,
            padx=15,
            pady=15,
            wrap=tk.WORD,
            height=8
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for log
        self.log_text.tag_config('success', foreground=self.colors['success'], font=('SF Mono', 10, 'bold'))
        self.log_text.tag_config('accent', foreground=self.colors['accent'], font=('SF Mono', 10, 'bold'))
        self.log_text.tag_config('secondary', foreground=self.colors['text_secondary'])
        self.log_text.tag_config('error', foreground='#dc2626', font=('SF Mono', 10, 'bold'))
        self.log_text.tag_config('info', foreground='#0284c7', font=('SF Mono', 10))
        self.log_text.tag_config('warning', foreground='#ea580c')

    def _update_title(self, *args):
        """Update header title based on project name"""
        project = self.project_name.get().strip()
        if project and project != "Project":
            self.title_var.set(f"{project}")
        else:
            self.title_var.set("Photo Selector")

    def _load_default_watermark(self):
        """Auto-load watermark.png if it exists in the script directory"""
        # Check if running as bundled app (PyInstaller)
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            bundle_dir = sys._MEIPASS
            default_watermark = Path(bundle_dir) / "watermark.png"
        else:
            # Running in normal Python
            script_dir = Path(__file__).parent
            default_watermark = script_dir / "watermark.png"

        if default_watermark.exists():
            try:
                # Validate that it's a valid image file
                img = Image.open(default_watermark)
                img.close()

                self.watermark_path = str(default_watermark)
                self.watermark_file.set("watermark.png")
                print(f"Auto-loaded default watermark: {default_watermark}")
            except Exception as e:
                print(f"Could not load default watermark: {e}")
                self.watermark_path = None

    def _create_folder_field(self, parent, label_text, variable, command, row):
        """Helper to create a folder selection field"""
        label = ttk.Label(parent, text=label_text, style='TLabel')
        label.pack(anchor=tk.W, pady=(0, 8) if row == 0 else (15, 8))

        folder_container = tk.Frame(parent, bg=self.colors['card'])
        folder_container.pack(fill=tk.X)

        entry = tk.Entry(folder_container,
                        textvariable=variable,
                        font=('SF Pro Text', 11),
                        bg=self.colors['input_bg'],
                        fg=self.colors['text'],
                        insertbackground=self.colors['text'],
                        relief='flat',
                        bd=0)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, ipadx=12)

        browse_btn = ttk.Button(folder_container,
                               text="Browse",
                               command=command,
                               style='Secondary.TButton')
        browse_btn.pack(side=tk.LEFT, padx=(10, 0))

    def select_input_folder(self):
        folder = filedialog.askdirectory(title="Select Input Folder with ARW Photos")
        if folder:
            self.input_folder.set(folder)

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)

    def select_preset_file(self):
        file = filedialog.askopenfilename(
            title="Select XMP Preset File",
            filetypes=[("XMP Files", "*.xmp"), ("All Files", "*.*")]
        )
        if file:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    self.custom_xmp_content = f.read()

                # Validate that it's a proper XMP file
                if '<x:xmpmeta' not in self.custom_xmp_content or 'crs:' not in self.custom_xmp_content:
                    messagebox.showerror("Invalid XMP",
                                       "The selected file does not appear to be a valid Camera Raw XMP preset.")
                    self.custom_xmp_content = None
                    return

                filename = Path(file).name
                self.preset_file.set(filename)
                self.log_message(f"Loaded custom preset: {filename}")

            except Exception as e:
                messagebox.showerror("Error Loading Preset", f"Could not load preset file:\n{e}")
                self.custom_xmp_content = None

    def use_builtin_preset(self):
        self.custom_xmp_content = None
        self.preset_file.set("(Using built-in preset)")
        self.log_message("Using built-in XMP preset")

    def select_preset_file_dark(self):
        file = filedialog.askopenfilename(
            title="Select XMP Preset File for Dark Photos",
            filetypes=[("XMP Files", "*.xmp"), ("All Files", "*.*")]
        )
        if file:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    self.custom_xmp_content_dark = f.read()

                # Validate that it's a proper XMP file
                if '<x:xmpmeta' not in self.custom_xmp_content_dark or 'crs:' not in self.custom_xmp_content_dark:
                    messagebox.showerror("Invalid XMP",
                                       "The selected file does not appear to be a valid Camera Raw XMP preset.")
                    self.custom_xmp_content_dark = None
                    return

                filename = Path(file).name
                self.preset_file_dark.set(filename)
                self.log_message(f"Loaded custom preset for dark photos: {filename}")

            except Exception as e:
                messagebox.showerror("Error Loading Preset", f"Could not load preset file:\n{e}")
                self.custom_xmp_content_dark = None

    def use_builtin_preset_dark(self):
        self.custom_xmp_content_dark = None
        self.preset_file_dark.set("(Using built-in preset)")
        self.log_message("Using built-in XMP preset for dark photos")

    def select_preset_file_light(self):
        file = filedialog.askopenfilename(
            title="Select XMP Preset File for Light Photos",
            filetypes=[("XMP Files", "*.xmp"), ("All Files", "*.*")]
        )
        if file:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    self.custom_xmp_content_light = f.read()

                # Validate that it's a proper XMP file
                if '<x:xmpmeta' not in self.custom_xmp_content_light or 'crs:' not in self.custom_xmp_content_light:
                    messagebox.showerror("Invalid XMP",
                                       "The selected file does not appear to be a valid Camera Raw XMP preset.")
                    self.custom_xmp_content_light = None
                    return

                filename = Path(file).name
                self.preset_file_light.set(filename)
                self.log_message(f"Loaded custom preset for light photos: {filename}")

            except Exception as e:
                messagebox.showerror("Error Loading Preset", f"Could not load preset file:\n{e}")
                self.custom_xmp_content_light = None

    def use_builtin_preset_light(self):
        self.custom_xmp_content_light = None
        self.preset_file_light.set("(Using built-in preset)")
        self.log_message("Using built-in XMP preset for light photos")

    def select_watermark_file(self):
        file = filedialog.askopenfilename(
            title="Select Watermark/Logo Image",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("PNG Files", "*.png"),
                ("JPEG Files", "*.jpg *.jpeg"),
                ("All Files", "*.*")
            ]
        )
        if file:
            try:
                # Validate that it's a valid image file
                img = Image.open(file)
                img.close()

                self.watermark_path = file
                filename = Path(file).name
                self.watermark_file.set(filename)
                self.log_message(f"Loaded watermark: {filename}")
            except Exception as e:
                messagebox.showerror("Error Loading Image", f"Could not load image file:\n{e}")
                self.watermark_path = None

    def clear_watermark(self):
        """Reset to default watermark (watermark.png if exists, otherwise camera icon)"""
        self._load_default_watermark()
        if not self.watermark_path:
            # If watermark.png doesn't exist, use camera icon
            self.watermark_file.set("(Using built-in camera icon)")
            self.log_message("Using built-in camera icon")
        else:
            self.log_message("Reset to default watermark: watermark.png")

    def log_message(self, message, tag=None):
        """Log a message to the results text area with optional color tag"""
        if tag:
            self.results_text.insert(tk.END, message + "\n", tag)
        else:
            self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.root.update()

    def log_to_activity(self, message, tag=None):
        """Log a message to the activity log with optional color tag"""
        if tag:
            self.log_text.insert(tk.END, message + "\n", tag)
        else:
            self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def update_status(self, message):
        """Update the status label above the progress bar"""
        self.status_label.config(text=message)
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

        # Clear previous results and logs
        self.results_text.delete(1.0, tk.END)
        self.log_text.delete(1.0, tk.END)
        self.photos = []

        # Find all ARW files
        arw_files = list(Path(input_dir).glob("*.ARW")) + list(Path(input_dir).glob("*.arw"))

        if not arw_files:
            messagebox.showwarning("Warning", "No ARW files found in the selected folder")
            return

        self.log_to_activity(f"Found {len(arw_files)} ARW files in {input_dir}", 'info')
        self.update_status(f"Preparing to analyze {len(arw_files)} photos...")
        self.progress['maximum'] = len(arw_files)
        self.progress['value'] = 0

        # Analyze in a separate thread
        thread = threading.Thread(target=self._analyze_thread, args=(arw_files,))
        thread.start()
    
    def _analyze_thread(self, arw_files):
        threshold = self.sharpness_threshold.get()
        detect_tilt = self.auto_straighten.get()
        include_vertical = True  # Always include vertical photos
        max_brightness = self.max_brightness_threshold.get()
        min_brightness = self.min_brightness_threshold.get()

        # Log start of analysis with settings to activity log
        self.root.after(0, self.log_to_activity,
                       f"Starting photo analysis...", 'info')
        self.root.after(0, self.log_to_activity,
                       f"Settings: Sharpness={threshold}, Brightness range={min_brightness}-{max_brightness}, Auto-straighten={'ON' if detect_tilt else 'OFF'}", 'secondary')

        for i, file_path in enumerate(arw_files, 1):
            # Update status and progress
            self.root.after(0, self.update_status, f"Analyzing {i}/{len(arw_files)}: {file_path.name}")
            self.root.after(0, lambda val=i: self.progress.config(value=val))

            result = analyze_photo(str(file_path), threshold, detect_tilt, include_vertical, max_brightness, min_brightness)
            result['path'] = str(file_path)
            result['filename'] = file_path.name
            self.photos.append(result)

            # Log all photos with status to results - use color tags
            status_icon = "✓" if result['selected'] else "✗"
            status_parts = [f"{status_icon} {file_path.name}"]

            # Add sharpness value
            status_parts.append(f"Sharp: {result['sharpness']:.1f}")

            # Add brightness value
            brightness = result.get('brightness', 128.0)
            brightness_threshold = self.brightness_threshold.get()
            brightness_category = "dark" if brightness < brightness_threshold else "light"
            status_parts.append(f"Bright: {brightness:.1f} ({brightness_category})")

            # Add face count if faces detected
            if result.get('face_count', 0) > 0:
                status_parts.append(f"Faces: {result['face_count']}")

            # Add tilt if detected
            if detect_tilt and abs(result.get('tilt_angle', 0)) > 0.1:
                status_parts.append(f"Tilt: {result['tilt_angle']:.2f}°")

            # Add rejection reason if not selected
            if not result['selected']:
                reasons = []
                if result.get('face_count', 0) == 0:
                    reasons.append("no faces")
                if not result['is_sharp']:
                    reasons.append(f"low sharpness (<{threshold})")
                if result.get('is_too_dark', False):
                    reasons.append(f"too dark (<{min_brightness})")
                if result.get('is_burned_out', False):
                    reasons.append(f"burned out (>{max_brightness})")
                if not include_vertical and not result['is_horizontal']:
                    reasons.append("vertical")
                if reasons:
                    status_parts.append(f"({', '.join(reasons)})")

            # Use colored output in results area
            tag = 'success' if result['selected'] else 'secondary'
            self.root.after(0, self.log_message, " | ".join(status_parts), tag)
        
        selected_count = sum(1 for p in self.photos if p['selected'])

        # Calculate dark vs light photo statistics
        brightness_threshold = self.brightness_threshold.get()
        selected_photos = [p for p in self.photos if p['selected']]
        dark_count = sum(1 for p in selected_photos if p.get('brightness', 128.0) < brightness_threshold)
        light_count = len(selected_photos) - dark_count

        # Completion summary - add to results
        self.root.after(0, self.log_message,
                       f"\n{'='*60}", 'accent')
        self.root.after(0, self.log_message,
                       f"ANALYSIS COMPLETE", 'success')
        self.root.after(0, self.log_message,
                       f"{'='*60}", 'accent')
        self.root.after(0, self.log_message,
                       f"Photos analyzed: {len(self.photos)}", 'info')
        self.root.after(0, self.log_message,
                       f"Photos selected: {selected_count}", 'success')
        self.root.after(0, self.log_message,
                       f"  - Dark photos (< {brightness_threshold}): {dark_count}", 'info')
        self.root.after(0, self.log_message,
                       f"  - Light photos (>= {brightness_threshold}): {light_count}", 'info')
        self.root.after(0, self.log_message,
                       f"Photos rejected: {len(self.photos) - selected_count}", 'secondary')
        self.root.after(0, self.log_message,
                       f"{'='*60}\n", 'accent')

        # Log to activity log
        self.root.after(0, self.log_to_activity,
                       f"Analysis complete: {selected_count}/{len(self.photos)} photos selected", 'success')

        # Update status
        self.root.after(0, self.update_status,
                       f"Analysis complete: {selected_count} of {len(self.photos)} photos selected")

        self.root.after(0, lambda: self.progress.config(value=0))
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

        selected_count = sum(1 for p in self.photos if p['selected'])

        self.log_to_activity(f"\nStarting to process {selected_count} selected photos...", 'info')
        self.log_to_activity(f"Output directory: {output_dir}", 'secondary')
        self.update_status(f"Processing {selected_count} photos...")

        self.progress['maximum'] = selected_count
        self.progress['value'] = 0
        self.process_btn.config(state='disabled')

        # Process in a separate thread
        thread = threading.Thread(target=self._process_thread, args=(output_dir, project))
        thread.start()
    
    def _process_thread(self, output_dir, project):
        selected_photos = [p for p in self.photos if p['selected']]

        for i, photo in enumerate(selected_photos, 1):
            try:
                # Update progress
                self.root.after(0, self.update_status, f"Processing {i}/{len(selected_photos)}: {photo['filename']}")
                self.root.after(0, lambda val=i: self.progress.config(value=val))

                # Extract original number from filename (e.g., DSC00595 -> 00595)
                import re
                original_filename = Path(photo['filename']).stem  # Remove extension

                # Try to extract number from various Sony camera filename formats
                # DSC00595, _DSC0001, etc.
                number_match = re.search(r'(\d{4,5})$', original_filename)

                if number_match:
                    # Use original number from filename
                    photo_number = number_match.group(1)
                    new_base_name = f"{project}_{photo_number}"
                else:
                    # Fallback to sequential numbering if no number found
                    new_base_name = f"{project}_{i:04d}"

                # Get original extension (ARW, CR2, NEF, etc.)
                original_ext = Path(photo['path']).suffix.upper()
                new_raw_name = f"{new_base_name}{original_ext}"
                new_raw_path = os.path.join(output_dir, new_raw_name)

                # Copy RAW file (don't convert to JPEG - Photoshop will do that)
                shutil.copy2(photo['path'], new_raw_path)

                # Log to activity log
                self.root.after(0, self.log_to_activity,
                              f"Copied {new_raw_name}", 'info')

                # Generate and save XMP sidecar file with preset (including rotation if detected)
                tilt_angle = photo.get('tilt_angle', 0.0)
                brightness = photo.get('brightness', 128.0)
                brightness_threshold = self.brightness_threshold.get()
                xmp_path = new_raw_path.replace(original_ext, '.xmp')

                # Determine if photo is dark or light based on brightness threshold
                is_dark = brightness < brightness_threshold

                # Choose appropriate XMP preset based on brightness
                if is_dark:
                    # Use dark preset
                    if self.custom_xmp_content_dark:
                        xmp_content = generate_xmp_with_rotation(tilt_angle, base_xmp=self.custom_xmp_content_dark)
                        preset_type = "dark (custom)"
                    else:
                        xmp_content = generate_xmp_with_rotation(tilt_angle)
                        preset_type = "dark (built-in)"
                else:
                    # Use light preset
                    if self.custom_xmp_content_light:
                        xmp_content = generate_xmp_with_rotation(tilt_angle, base_xmp=self.custom_xmp_content_light)
                        preset_type = "light (custom)"
                    else:
                        xmp_content = generate_xmp_with_rotation(tilt_angle)
                        preset_type = "light (built-in)"

                with open(xmp_path, 'w', encoding='utf-8') as xmp_file:
                    xmp_file.write(xmp_content)

                # Log XMP creation with brightness and tilt info
                if abs(tilt_angle) > 0.1:
                    self.root.after(0, self.log_to_activity,
                                  f"  → XMP {preset_type} applied, brightness={brightness:.1f}, rotation={abs(tilt_angle):.2f}°", 'success')
                else:
                    self.root.after(0, self.log_to_activity,
                                  f"  → XMP {preset_type} applied, brightness={brightness:.1f}", 'secondary')

            except Exception as e:
                self.root.after(0, self.log_to_activity,
                              f"Error processing {photo['filename']}: {e}", 'error')

        # Log completion to activity log
        self.root.after(0, self.log_to_activity,
                       f"✓ Processing complete! {len(selected_photos)} files copied to {output_dir}", 'success')
        self.root.after(0, self.update_status,
                       f"Processing complete: {len(selected_photos)} files copied")

        # Check if any version of Photoshop is installed
        photoshop_installed = False
        photoshop_version = None
        for year in [2026, 2025, 2024, 2023, 2022, 2021, 2020]:
            ps_path = f"/Applications/Adobe Photoshop {year}"
            if os.path.exists(ps_path):
                photoshop_installed = True
                photoshop_version = f"Adobe Photoshop {year}"
                break

        if not photoshop_installed:
            self.root.after(0, self.log_to_activity,
                           f"Photoshop not found - import to Lightroom manually", 'warning')
        else:
            # Launch Photoshop automation
            self.root.after(0, self.log_to_activity,
                           f"\nStarting Photoshop automation with {photoshop_version}...", 'info')
            self.root.after(0, self.update_status, "Running Photoshop automation...")

            try:
                import subprocess
                # Find script directory (works for both dev and bundled app)
                if getattr(sys, 'frozen', False):
                    # Running in PyInstaller bundle
                    script_dir = Path(sys._MEIPASS)
                else:
                    # Running in normal Python
                    script_dir = Path(__file__).parent
                photoshop_script = script_dir / "apply_preset_photoshop.sh"

                if photoshop_script.exists():
                    # Run Photoshop automation script with output folder as argument
                    self.root.after(0, self.log_to_activity, "[1/2] Converting RAW to JPEG with Photoshop...", 'info')

                    result = subprocess.run(
                        [str(photoshop_script), output_dir],
                        capture_output=True,
                        text=True
                    )

                    if result.returncode == 0:
                        self.root.after(0, self.log_to_activity, "  ✓ Photoshop conversion complete", 'success')
                        self.root.after(0, self.log_to_activity, "[2/2] Creating PDF grid from JPEGs...", 'info')
                        self.root.after(0, self.update_status, "Creating PDF grid...")

                        # Run Python PDF generator
                        pdf_script = script_dir / "create_pdf_grid.py"
                        if pdf_script.exists():
                            # Use the same Python that's running this script
                            # Try homebrew python first, fall back to sys.executable
                            python_exec = sys.executable
                            if os.path.exists("/opt/homebrew/bin/python3.11"):
                                python_exec = "/opt/homebrew/bin/python3.11"

                            # Build command arguments
                            pdf_cmd = [python_exec, str(pdf_script), output_dir, project]
                            if self.watermark_path:
                                pdf_cmd.append(self.watermark_path)

                            pdf_result = subprocess.run(
                                pdf_cmd,
                                capture_output=True,
                                text=True
                            )

                            if pdf_result.returncode == 0:
                                # Determine PDF filename based on project name
                                safe_name = project.replace(' ', '_').replace('/', '_').replace('\\', '_')
                                pdf_filename = f"{safe_name}.pdf" if project and project != "Photo Selection" else "photo_grid.pdf"

                                self.root.after(0, self.log_to_activity,
                                               f"  ✓ PDF created: {pdf_filename}", 'success')
                            else:
                                self.root.after(0, self.log_to_activity,
                                               f"  ✗ Error creating PDF (exit code {pdf_result.returncode})", 'error')
                        else:
                            self.root.after(0, self.log_to_activity,
                                           "  ✗ PDF generator script not found", 'error')
                    else:
                        self.root.after(0, self.log_to_activity,
                                       f"  ✗ Photoshop script failed (exit code {result.returncode})", 'error')
                else:
                    self.root.after(0, self.log_to_activity,
                                   f"  ✗ Script not found: {photoshop_script}", 'error')
            except Exception as e:
                self.root.after(0, self.log_to_activity,
                               f"  ✗ Error launching Photoshop: {e}", 'error')

        self.root.after(0, lambda: self.progress.config(value=0))
        self.root.after(0, self.update_status, "Ready")

        # Calculate summary statistics
        total_photos = len(self.photos)
        selected_count = len(selected_photos)
        rejected_count = total_photos - selected_count

        if photoshop_installed:
            safe_name = project.replace(' ', '_').replace('/', '_').replace('\\', '_')
            pdf_filename = f"{safe_name}.pdf" if project and project != "Photo Selection" else "photo_grid.pdf"

            self.root.after(0, lambda: messagebox.showinfo("Success",
                           f"PHOTO ANALYSIS SUMMARY\n"
                           f"{'='*40}\n"
                           f"Total photos analyzed: {total_photos}\n"
                           f"Photos selected: {selected_count}\n"
                           f"Photos rejected: {rejected_count}\n\n"
                           f"PROCESSING COMPLETE\n"
                           f"{'='*40}\n"
                           f"Copied {selected_count} RAW files + XMP sidecars\n\n"
                           f"RAW files saved to:\n{output_dir}\n\n"
                           f"Photoshop is now processing...\n"
                           f"PDF will be saved to:\n{output_dir}/{pdf_filename}"))
        else:
            self.root.after(0, lambda: messagebox.showinfo("Success",
                           f"PHOTO ANALYSIS SUMMARY\n"
                           f"{'='*40}\n"
                           f"Total photos analyzed: {total_photos}\n"
                           f"Photos selected: {selected_count}\n"
                           f"Photos rejected: {rejected_count}\n\n"
                           f"PROCESSING COMPLETE\n"
                           f"{'='*40}\n"
                           f"Copied {selected_count} RAW files + XMP sidecars\n\n"
                           f"RAW files saved to:\n{output_dir}\n\n"
                           f"NEXT STEP:\n"
                           f"1. Open Adobe Lightroom CC\n"
                           f"2. Import the output folder\n"
                           f"3. Preset will be auto-applied\n"
                           f"4. Export as JPEG"))


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
