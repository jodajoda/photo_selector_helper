#!/bin/bash

# Alternative Photoshop Batch Processing via Adobe Bridge
# Bridge ALWAYS respects XMP sidecars, unlike direct Photoshop opening
# Usage: ./apply_preset_via_bridge.sh [input_folder]

INPUT_FOLDER="${1:-}"

if [ -z "$INPUT_FOLDER" ]; then
    echo "Error: Please provide input folder"
    echo "Usage: ./apply_preset_via_bridge.sh /path/to/folder"
    exit 1
fi

if [ ! -d "$INPUT_FOLDER" ]; then
    echo "Error: Folder does not exist: $INPUT_FOLDER"
    exit 1
fi

OUTPUT_FOLDER="$INPUT_FOLDER/final_jpegs"
mkdir -p "$OUTPUT_FOLDER"

echo "========================================="
echo "Batch Processing via Adobe Bridge"
echo "========================================="
echo "Input folder: $INPUT_FOLDER"
echo "Output folder: $OUTPUT_FOLDER"
echo ""
echo "This method uses Adobe Bridge which ALWAYS"
echo "respects XMP sidecars (unlike direct Photoshop)"
echo ""

# Count RAW files
RAW_COUNT=$(find "$INPUT_FOLDER" -maxdepth 1 -iname "*.arw" -o -iname "*.cr2" -o -iname "*.nef" | wc -l | tr -d ' ')
echo "Found $RAW_COUNT RAW files"
echo ""

# Use Bridge's Image Processor
echo "Opening Adobe Bridge Image Processor..."
echo "(You may need to click 'Run' in the Image Processor dialog)"
echo ""

osascript <<EOF
tell application "Adobe Bridge 2024"
    activate

    -- Open the input folder in Bridge
    reveal (POSIX file "$INPUT_FOLDER")

    delay 2

    -- Select all RAW files in the folder
    tell application "System Events"
        keystroke "a" using command down
    end tell

    delay 1

    -- Open Image Processor
    -- Tools → Photoshop → Image Processor
    tell application "System Events"
        tell process "Adobe Bridge 2024"
            click menu item "Image Processor..." of menu "Photoshop" of menu item "Photoshop" of menu "Tools" of menu bar 1
        end tell
    end tell

end tell

-- Wait for Image Processor window
delay 3

tell application "System Events"
    tell process "Image Processor"
        -- Select output folder
        -- (User will need to manually set this)

        -- Enable JPEG output
        -- (User will need to manually set this)

        display dialog "Image Processor is now open.

Please configure:
1. Section 2: Save as JPEG (Quality: 12)
2. Section 3: Destination - Choose folder: $OUTPUT_FOLDER
3. Click 'Run'

Bridge will apply XMP presets to ALL files!" buttons {"OK"} default button 1
    end tell
end tell
EOF

echo ""
echo "========================================="
echo "Next steps:"
echo "1. In the Image Processor window that just opened:"
echo "   - Section 2: Check 'Save as JPEG', Quality: 12"
echo "   - Section 3: Choose destination folder:"
echo "     $OUTPUT_FOLDER"
echo "   - Click 'Run'"
echo "2. Bridge will process all files with XMP presets"
echo "========================================="
