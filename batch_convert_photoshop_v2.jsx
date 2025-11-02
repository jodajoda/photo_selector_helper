/*
 * Batch Convert RAW to JPEG with XMP Preset - Photoshop Script
 *
 * This script:
 * 1. Opens all ARW (RAW) files from a specified folder
 * 2. Applies XMP sidecar settings automatically
 * 3. Converts to JPEG with specified quality
 * 4. Saves to a "final_jpegs" subfolder
 *
 * Usage: Run from Photoshop or via command line
 */

#target photoshop

// Configuration
var JPEG_QUALITY = 10; // 1-12 scale (10 = high quality, ~90%)
var OUTPUT_SUBFOLDER = "final_jpegs";
var RAW_EXTENSIONS = [".ARW", ".arw", ".CR2", ".cr2", ".NEF", ".nef"];

// Main function
function main() {
    // Get the folder passed as argument (from shell script)
    var sourceFolder;

    if (app.playbackParameters.count > 0) {
        // Called from shell script with parameter
        var folderPath = app.playbackParameters.getString(0);
        sourceFolder = new Folder(folderPath);
    } else {
        // No folder provided - error
        alert("Error: This script must be called with a folder path parameter.\nRun it via the shell script or Python app.");
        return;
    }

    if (!sourceFolder || !sourceFolder.exists) {
        alert("Error: Folder does not exist:\n" + (sourceFolder ? sourceFolder.fsName : "undefined"));
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

            // Progress message
            app.doProgress(i, rawFiles.length);

            // Open RAW file with XMP settings
            var doc = openRawWithXMP(rawFile);

            if (doc) {
                // Save as JPEG
                var baseName = rawFile.name.replace(/\.[^\.]+$/, "");
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
            // Continue with next file
        }
    }

    // Show completion message
    alert("Conversion complete!\n\n" +
          "Processed: " + rawFiles.length + " files\n" +
          "Success: " + successCount + "\n" +
          "Errors: " + errorCount + "\n\n" +
          "JPEGs saved to:\n" + outputFolder.fsName);
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
        // Check if XMP sidecar exists
        var xmpFile = new File(rawFile.path + "/" + rawFile.name.replace(/\.[^\.]+$/, ".xmp"));

        // Open the RAW file - Camera Raw will automatically load the XMP sidecar if it exists
        var doc = app.open(rawFile);

        return doc;
    } catch (e) {
        return null;
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

// Run the script
try {
    // Set preferences for better automation
    var originalDisplayDialogs = app.displayDialogs;
    app.displayDialogs = DialogModes.NO; // Suppress dialogs

    main();

    // Restore original settings
    app.displayDialogs = originalDisplayDialogs;
} catch (e) {
    alert("Error: " + e.message + "\n\nLine: " + e.line);
}
