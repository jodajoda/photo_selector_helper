#!/usr/bin/env python3
"""
Verify XMP Fix - Check that generated XMP files have all required attributes
Usage: python3 verify_xmp_fix.py [folder_with_xmp_files]
"""

import sys
import os
from pathlib import Path

def check_xmp_file(xmp_path):
    """Check if an XMP file has all required attributes"""
    with open(xmp_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Critical attributes that MUST be present for Camera Raw to apply preset
    required_attributes = {
        'xmlns:crs': 'xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/"',
        'photoshop:SidecarForExtension': 'photoshop:SidecarForExtension="ARW"',
        'crs:CameraProfile': 'crs:CameraProfile="Adobe Standard"',
        'crs:HasSettings': 'crs:HasSettings="True"',
        'crs:HasCrop': 'crs:HasCrop="False"',  # or "True" if straightened
        'crs:AlreadyApplied': 'crs:AlreadyApplied="False"',
    }

    # Optional but recommended attributes
    optional_attributes = {
        'xmlns:xmp': 'xmlns:xmp="http://ns.adobe.com/xap/1.0/"',
        'xmlns:photoshop': 'xmlns:photoshop="http://ns.adobe.com/photoshop/1.0/"',
        'xmlns:crd': 'xmlns:crd="http://ns.adobe.com/camera-raw-defaults/1.0/"',
        'crd:CameraProfile': 'crd:CameraProfile=',  # Can be "Adobe Standard" or "Camera Standard"
    }

    results = {}
    for name, pattern in required_attributes.items():
        # For HasCrop, accept either True or False
        if name == 'crs:HasCrop':
            results[name] = 'crs:HasCrop="True"' in content or 'crs:HasCrop="False"' in content
        else:
            results[name] = pattern in content

    return results, content

def main():
    if len(sys.argv) > 1:
        folder = Path(sys.argv[1])
    else:
        folder = Path.cwd()

    if not folder.exists():
        print(f"Error: Folder does not exist: {folder}")
        sys.exit(1)

    # Find all XMP files
    xmp_files = list(folder.glob("*.xmp")) + list(folder.glob("*.XMP"))

    if not xmp_files:
        print(f"No XMP files found in {folder}")
        sys.exit(1)

    print(f"\n{'='*70}")
    print(f"XMP VERIFICATION REPORT")
    print(f"{'='*70}")
    print(f"Folder: {folder}")
    print(f"XMP files found: {len(xmp_files)}")
    print(f"{'='*70}\n")

    all_passed = True

    for xmp_file in xmp_files:
        print(f"\nChecking: {xmp_file.name}")
        print("-" * 70)

        results, content = check_xmp_file(xmp_file)

        passed = all(results.values())
        all_passed = all_passed and passed

        if passed:
            print("✅ PASSED - All required attributes present!")
        else:
            print("❌ FAILED - Missing required attributes:")
            for attr, present in results.items():
                if not present:
                    print(f"  ❌ {attr}")

        # Show some key settings to verify preset is there
        if 'crs:Temperature="7415"' in content:
            print("  ✓ Temperature: 7415K (preset applied)")
        else:
            print("  ⚠ Temperature not found (preset may not be applied)")

        if 'crs:Exposure2012="-0.40"' in content:
            print("  ✓ Exposure: -0.40 (preset applied)")
        else:
            print("  ⚠ Exposure not found (preset may not be applied)")

        if 'crs:Highlights2012="-100"' in content:
            print("  ✓ Highlights: -100 (preset applied)")
        else:
            print("  ⚠ Highlights not found (preset may not be applied)")

        # Check if straightening is applied
        if 'crs:StraightenAngle=' in content:
            import re
            angle_match = re.search(r'crs:StraightenAngle="([^"]+)"', content)
            if angle_match:
                print(f"  ✓ Straightening angle: {angle_match.group(1)}°")

    print(f"\n{'='*70}")
    if all_passed:
        print("✅ ALL XMP FILES PASSED VERIFICATION!")
        print("All files have the required attributes for Camera Raw to apply presets.")
    else:
        print("❌ SOME XMP FILES FAILED VERIFICATION")
        print("These files may not work correctly with Camera Raw.")
        print("\nTo fix: Re-run photo_selector.py to regenerate XMP files with the fix.")
    print(f"{'='*70}\n")

    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
