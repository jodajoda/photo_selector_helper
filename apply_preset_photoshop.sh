#!/bin/bash

# Automated Photoshop Batch Processing Script
# This script opens Photoshop and runs the JSX script to apply XMP presets
# Usage: ./apply_preset_photoshop.sh [input_folder]

# Path to the JSX script (same directory as this script)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
JSX_SCRIPT="$SCRIPT_DIR/batch_convert_photoshop_v2.jsx"
WATERMARK_PATH="$SCRIPT_DIR/watermark.png"

# Get input folder from argument or let JSX prompt for it
INPUT_FOLDER="${1:-}"

if [ -n "$INPUT_FOLDER" ]; then
    echo "Starting Photoshop batch processing..."
    echo "Input folder: $INPUT_FOLDER"
    echo "Script: $JSX_SCRIPT"
    echo "Output: $INPUT_FOLDER/final_jpegs/"

    # Create a temporary JSX file with the folder path embedded directly
    TEMP_JSX=$(mktemp /tmp/photoshop_batch_XXXXXX.jsx)

    # Read the main script and inject the folder path
    cat > "$TEMP_JSX" <<JSXEOF
// Auto-generated wrapper script with embedded folder path
#target photoshop

// Embedded configuration
var EMBEDDED_INPUT_FOLDER = "$INPUT_FOLDER";
var WATERMARK_FILE = "$WATERMARK_PATH";

// Configuration
var JPEG_QUALITY = 10; // 1-12 scale (10 = high quality, ~90%)
var OUTPUT_SUBFOLDER = "final_jpegs";
var RAW_EXTENSIONS = [".ARW", ".arw", ".CR2", ".cr2", ".NEF", ".nef"];
var WATERMARK_OPACITY = 30; // 0-100 (30 = 30% opacity)
var WATERMARK_POSITION = "center"; // bottom-right, bottom-left, top-right, top-left, center
var WATERMARK_SIZE = 0.75; // Watermark will be 75% of image width (with margin)

// PDF Grid Configuration
var PDF_IMAGES_PER_ROW = 2; // Number of images per row in grid (2 = bigger images)
var PDF_PAGE_WIDTH = 11.69 * 72; // A4 width in points (297mm = 11.69 inches)
var PDF_PAGE_HEIGHT = 8.27 * 72; // A4 height in points landscape (210mm = 8.27 inches)
var PDF_MARGIN = 0.2 * 72; // 0.2 inch margin (smaller margin = more space for images)
var PDF_RESOLUTION = 400; // DPI for PDF (400 for extremely high quality print)
var FILENAME_HEIGHT = 18; // Height reserved for filename text in points

// Main function
function main() {
    var sourceFolder = new Folder(EMBEDDED_INPUT_FOLDER);

    if (!sourceFolder || !sourceFolder.exists) {
        alert("Error: Folder does not exist:\\n" + EMBEDDED_INPUT_FOLDER);
        return;
    }

    // Create output folder
    var outputFolder = new Folder(sourceFolder + "/" + OUTPUT_SUBFOLDER);
    if (!outputFolder.exists) {
        outputFolder.create();
    }

    // Get all RAW files
    var rawFiles = getRawFiles(sourceFolder);

    if (rawFiles.length === 0) {
        alert("No RAW files found in the selected folder.");
        return;
    }

    // Process each file
    var successCount = 0;
    var errorCount = 0;

    for (var i = 0; i < rawFiles.length; i++) {
        try {
            var rawFile = rawFiles[i];

            // Open RAW file with XMP settings
            var doc = openRawWithXMP(rawFile);

            if (doc) {
                // Flatten the RAW document first (important for RAW files)
                if (doc.layers.length > 1 || doc.backgroundLayer == null) {
                    doc.flatten();
                }

                // Apply watermark if watermark file exists
                var watermarkFile = new File(WATERMARK_FILE);
                if (watermarkFile.exists) {
                    var watermarkApplied = applyWatermark(doc, watermarkFile, WATERMARK_OPACITY, WATERMARK_POSITION, WATERMARK_SIZE);
                }

                // Save as high-quality JPEG
                var baseName = rawFile.name.replace(/\\.[^\\.]+\\$/, "");
                var jpegFile = new File(outputFolder + "/" + baseName + ".jpg");
                saveAsJPEG(doc, jpegFile, JPEG_QUALITY);

                // Close document
                doc.close(SaveOptions.DONOTSAVECHANGES);

                successCount++;
            } else {
                errorCount++;
            }
        } catch (e) {
            errorCount++;
        }
    }

    // Show completion message
    alert("JPEG conversion complete!\\n\\n" +
          "Processed: " + rawFiles.length + " files\\n" +
          "Success: " + successCount + "\\n" +
          "Errors: " + errorCount + "\\n\\n" +
          "JPEGs saved to:\\n" + outputFolder.fsName);
}

// Get all RAW files from folder
function getRawFiles(folder) {
    var allFiles = folder.getFiles();
    var rawFiles = [];

    for (var i = 0; i < allFiles.length; i++) {
        var file = allFiles[i];

        if (file instanceof File) {
            var fileName = file.name;

            // Check if file has RAW extension
            for (var j = 0; j < RAW_EXTENSIONS.length; j++) {
                if (fileName.indexOf(RAW_EXTENSIONS[j]) === fileName.length - RAW_EXTENSIONS[j].length) {
                    rawFiles.push(file);
                    break;
                }
            }
        }
    }

    return rawFiles;
}

// Open RAW file with XMP settings
function openRawWithXMP(rawFile) {
    try {
        // Open the RAW file - Camera Raw will automatically load the XMP sidecar if it exists
        var doc = app.open(rawFile);
        return doc;
    } catch (e) {
        return null;
    }
}

// Apply watermark to document
function applyWatermark(doc, watermarkFile, opacity, position, watermarkSize) {
    try {
        // Open watermark as a separate document
        var watermarkDoc = app.open(watermarkFile);

        // Select all and copy watermark
        watermarkDoc.selection.selectAll();
        watermarkDoc.selection.copy();
        watermarkDoc.close(SaveOptions.DONOTSAVECHANGES);

        // Make sure the main document is active
        app.activeDocument = doc;

        // Paste watermark into main document
        var pastedLayer = doc.paste();

        // Set the active layer properties
        var watermarkLayer = doc.activeLayer;
        watermarkLayer.name = "Watermark";

        // Set opacity FIRST before any transformations
        watermarkLayer.opacity = opacity;

        // Get document dimensions
        var docWidth = doc.width.as("px");
        var docHeight = doc.height.as("px");

        // Calculate target width based on watermarkSize (0.5 = 50% of image width)
        var targetWidth = docWidth * watermarkSize;

        // Get original watermark dimensions BEFORE resize
        var origBounds = watermarkLayer.bounds;
        var origWidth = origBounds[2] - origBounds[0];
        var origHeight = origBounds[3] - origBounds[1];

        // Calculate scale percentage needed
        var scalePercent = (targetWidth / origWidth.as("px")) * 100;

        // Resize watermark proportionally using the center as anchor
        watermarkLayer.resize(scalePercent, scalePercent, AnchorPosition.MIDDLECENTER);

        // Get NEW bounds after resize
        var resizedBounds = watermarkLayer.bounds;
        var resizedLeft = resizedBounds[0].as("px");
        var resizedTop = resizedBounds[1].as("px");
        var resizedRight = resizedBounds[2].as("px");
        var resizedBottom = resizedBounds[3].as("px");
        var resizedWidth = resizedRight - resizedLeft;
        var resizedHeight = resizedBottom - resizedTop;

        // Calculate center position
        var centerX = (docWidth - resizedWidth) / 2;
        var centerY = (docHeight - resizedHeight) / 2;

        // Calculate how much to move from current position to center
        var moveX = centerX - resizedLeft;
        var moveY = centerY - resizedTop;

        // Move to center
        watermarkLayer.translate(moveX, moveY);

        // Flatten to merge watermark
        doc.flatten();

        return true;

    } catch (e) {
        // If watermark fails, continue without it
        return false;
    }
}

// Save as JPEG
function saveAsJPEG(doc, file, quality) {
    var jpegOptions = new JPEGSaveOptions();
    jpegOptions.quality = quality;
    jpegOptions.embedColorProfile = true;
    jpegOptions.formatOptions = FormatOptions.STANDARDBASELINE;
    jpegOptions.scans = 3;
    jpegOptions.matte = MatteType.NONE;

    // Save
    doc.saveAs(file, jpegOptions, true, Extension.LOWERCASE);
}

// Create PDF with images arranged in a grid
function createPDFGrid(processedDocs, pdfFile) {
    try {
        // Calculate grid dimensions
        var imagesPerRow = PDF_IMAGES_PER_ROW;
        var availableWidth = PDF_PAGE_WIDTH - (PDF_MARGIN * 2);
        var availableHeight = PDF_PAGE_HEIGHT - (PDF_MARGIN * 2);

        var spacing = 20; // Spacing between images in points
        var cellWidth = (availableWidth - (spacing * (imagesPerRow - 1))) / imagesPerRow;

        // Assume landscape images (adjust cell height based on 3:2 aspect ratio + filename space)
        var imageHeight = cellWidth * (2/3);
        var cellHeight = imageHeight + FILENAME_HEIGHT + 10; // Add space for filename + extra padding

        var imagesPerColumn = Math.floor((availableHeight + spacing) / (cellHeight + spacing));
        var imagesPerPage = imagesPerRow * imagesPerColumn;

        // Create master PDF document (first page) with high resolution
        var pdfDoc = app.documents.add(PDF_PAGE_WIDTH, PDF_PAGE_HEIGHT, PDF_RESOLUTION, "Photo Grid", NewDocumentMode.RGB);

        var currentPage = 0;
        var imageIndex = 0;

        while (imageIndex < processedDocs.length) {
            // Create new page if not the first page
            if (currentPage > 0) {
                var newLayer = pdfDoc.artLayers.add();
                newLayer.name = "Page " + (currentPage + 1);
            }

            // Place images on current page
            var imagesOnThisPage = Math.min(imagesPerPage, processedDocs.length - imageIndex);

            for (var i = 0; i < imagesOnThisPage; i++) {
                var row = Math.floor(i / imagesPerRow);
                var col = i % imagesPerRow;

                // Calculate positions in points
                var xPosPoints = PDF_MARGIN + (col * (cellWidth + spacing));
                var yPosPoints = PDF_MARGIN + (row * (cellHeight + spacing));

                // Convert to pixels at PDF resolution
                var xPos = (xPosPoints / 72) * PDF_RESOLUTION;
                var yPos = (yPosPoints / 72) * PDF_RESOLUTION;

                var sourceDoc = processedDocs[imageIndex].doc;

                // Duplicate the source document to avoid modifying original
                var tempDoc = sourceDoc.duplicate();

                // Calculate target dimensions in pixels
                var targetWidthPx = (cellWidth / 72) * PDF_RESOLUTION;
                var targetHeightPx = (imageHeight / 72) * PDF_RESOLUTION;

                // Calculate scale to fit within cell while maintaining aspect ratio
                var docWidth = tempDoc.width.as("px");
                var docHeight = tempDoc.height.as("px");
                var aspectRatio = docWidth / docHeight;

                if (aspectRatio > (targetWidthPx / targetHeightPx)) {
                    // Width is limiting factor
                    targetHeightPx = targetWidthPx / aspectRatio;
                } else {
                    // Height is limiting factor
                    targetWidthPx = targetHeightPx * aspectRatio;
                }

                // Resize image with high quality resampling at PDF resolution
                tempDoc.resizeImage(UnitValue(targetWidthPx, "px"), UnitValue(targetHeightPx, "px"), PDF_RESOLUTION, ResampleMethod.BICUBIC);

                // Select all and copy
                tempDoc.selection.selectAll();
                tempDoc.selection.copy();
                tempDoc.close(SaveOptions.DONOTSAVECHANGES);

                // Paste into PDF document
                app.activeDocument = pdfDoc;
                var pastedLayer = pdfDoc.paste();

                // Position the pasted image (top of cell, centered horizontally)
                var bounds = pastedLayer.bounds;
                var layerWidth = bounds[2] - bounds[0];
                var layerHeight = bounds[3] - bounds[1];

                // Calculate cell width in pixels
                var cellWidthPx = (cellWidth / 72) * PDF_RESOLUTION;

                // Center horizontally in cell, align to top
                var centerX = xPos + (cellWidthPx / 2) - (layerWidth.as("px") / 2);
                var topY = yPos;

                var moveX = centerX - bounds[0].as("px");
                var moveY = topY - bounds[1].as("px");

                pastedLayer.translate(moveX, moveY);
                pastedLayer.name = processedDocs[imageIndex].name;

                // Add filename text below image
                try {
                    var textLayer = pdfDoc.artLayers.add();
                    textLayer.kind = LayerKind.TEXT;
                    textLayer.name = "Filename";

                    var textItem = textLayer.textItem;

                    // Position text first (required before setting content)
                    var imageHeightPx = (imageHeight / 72) * PDF_RESOLUTION;
                    var textXCenter = xPos + (cellWidthPx / 2);
                    var textY = yPos + imageHeightPx + ((12 / 72) * PDF_RESOLUTION);
                    textItem.position = [textXCenter, textY];

                    // Set text properties
                    textItem.contents = processedDocs[imageIndex].name;
                    textItem.size = 7; // Font size in points (smaller text)

                    // Set color
                    var textColor = new SolidColor();
                    textColor.rgb.red = 0;
                    textColor.rgb.green = 0;
                    textColor.rgb.blue = 0;
                    textItem.color = textColor;

                    textItem.justification = Justification.CENTER;
                } catch (textError) {
                    // If text fails, continue without it
                }

                imageIndex++;
            }

            currentPage++;
        }

        // Flatten the document
        pdfDoc.flatten();

        // Save as PDF with maximum quality
        var pdfSaveOptions = new PDFSaveOptions();
        pdfSaveOptions.embedColorProfile = true;
        pdfSaveOptions.pdfCompatibility = PDFCompatibility.PDF16;
        pdfSaveOptions.encoding = PDFEncoding.JPEG;
        pdfSaveOptions.jpegQuality = 12; // Maximum quality (1-12 scale)
        pdfSaveOptions.optimizeForWeb = false; // Don't optimize, keep full quality

        pdfDoc.saveAs(pdfFile, pdfSaveOptions, true, Extension.LOWERCASE);
        pdfDoc.close(SaveOptions.DONOTSAVECHANGES);

        return true;
    } catch (e) {
        alert("Error creating PDF: " + e.message);
        return false;
    }
}

// Run the script
try {
    // Set preferences for better automation
    var originalDisplayDialogs = app.displayDialogs;
    app.displayDialogs = DialogModes.NO;

    main();

    // Restore original settings
    app.displayDialogs = originalDisplayDialogs;
} catch (e) {
    alert("Error: " + e.message + "\\n\\nLine: " + e.line);
}
JSXEOF

    # Auto-detect installed Photoshop version
    PHOTOSHOP_APP=""
    for year in 2026 2025 2024 2023 2022 2021 2020; do
        if [ -d "/Applications/Adobe Photoshop $year" ]; then
            PHOTOSHOP_APP="Adobe Photoshop $year"
            echo "Found Photoshop: $PHOTOSHOP_APP"
            break
        fi
    done

    if [ -z "$PHOTOSHOP_APP" ]; then
        echo "Error: Adobe Photoshop not found in /Applications/"
        echo "Please install Adobe Photoshop or specify the application name manually."
        rm -f "$TEMP_JSX"
        exit 1
    fi

    # Run Photoshop with the temporary JSX script
    osascript <<EOF
tell application "$PHOTOSHOP_APP"
    activate
    do javascript file "$TEMP_JSX"
end tell
EOF

    # Clean up temporary file
    rm -f "$TEMP_JSX"
else
    echo "Error: No input folder specified."
    echo "Usage: ./apply_preset_photoshop.sh [input_folder]"
    exit 1
fi

echo ""
echo "Batch processing complete!"
if [ -n "$INPUT_FOLDER" ]; then
    echo "JPEGs saved to: $INPUT_FOLDER/final_jpegs/"
fi
