#!/usr/bin/env python3
"""
PDF Grid Generator
Creates a professional PDF grid from JPEG images with filenames
Includes client selection template with checkboxes
"""

import sys
import os
import re
from pathlib import Path
from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor, black, white
from reportlab.graphics.shapes import Drawing, Circle, Rect, Polygon
from reportlab.graphics import renderPDF
from datetime import datetime

# Configuration
IMAGES_PER_ROW = 2
PAGE_SIZE = landscape(A4)  # A4 landscape (297mm x 210mm)
PAGE_WIDTH, PAGE_HEIGHT = PAGE_SIZE
MARGIN = 0.5 * inch  # Larger margin for professional look
HEADER_HEIGHT = 0.4 * inch  # Space for header (reduced to fit more photos)
FOOTER_HEIGHT = 0.4 * inch  # Space for footer
SPACING = 20  # Spacing between images in points
MAX_IMAGE_DPI = 150  # Max DPI for images in PDF (150 is good for screen/email)
FILENAME_FONT_SIZE = 8  # Font for filenames
FILENAME_HEIGHT = 30  # Space for filename + checkbox

# Template styling
PRIMARY_COLOR = HexColor('#2C3E50')  # Dark blue-gray
ACCENT_COLOR = HexColor('#3498DB')  # Bright blue
LIGHT_GRAY = HexColor('#ECF0F1')
CHECKBOX_SIZE = 12  # Size of selection checkbox


def draw_builtin_watermark(c, x, y, width, height):
    """Draw a simple camera icon as built-in watermark"""
    # Save graphics state
    c.saveState()

    # Draw a simple camera icon in white
    c.setFillColor(white)
    c.setStrokeColor(white)
    c.setLineWidth(1.5)

    # Camera body (rounded rectangle)
    body_width = width * 0.7
    body_height = height * 0.5
    body_x = x + (width - body_width) / 2
    body_y = y + height * 0.2

    c.roundRect(body_x, body_y, body_width, body_height, 3, fill=False, stroke=True)

    # Lens (circle)
    lens_radius = min(body_width, body_height) * 0.25
    lens_x = body_x + body_width / 2
    lens_y = body_y + body_height / 2

    c.circle(lens_x, lens_y, lens_radius, fill=False, stroke=True)
    c.circle(lens_x, lens_y, lens_radius * 0.5, fill=False, stroke=True)

    # Viewfinder bump on top
    bump_width = body_width * 0.3
    bump_height = height * 0.15
    bump_x = body_x + (body_width - bump_width) / 2
    bump_y = body_y + body_height

    c.roundRect(bump_x, bump_y, bump_width, bump_height, 2, fill=False, stroke=True)

    # Flash dot
    flash_radius = 2
    flash_x = body_x + body_width * 0.8
    flash_y = body_y + body_height * 0.75

    c.circle(flash_x, flash_y, flash_radius, fill=True, stroke=False)

    # Restore graphics state
    c.restoreState()


def draw_header(c, page_num, total_pages, project_name="Photo Selection", watermark_path=None):
    """Draw professional header on page with optional watermark/logo"""
    # Header background
    c.setFillColor(PRIMARY_COLOR)
    c.rect(0, PAGE_HEIGHT - HEADER_HEIGHT, PAGE_WIDTH, HEADER_HEIGHT, fill=True, stroke=False)

    # Watermark/Logo (custom or built-in)
    logo_width = 0
    max_logo_height = HEADER_HEIGHT * 0.7  # 70% of header height
    logo_x = MARGIN
    logo_y = PAGE_HEIGHT - HEADER_HEIGHT/2 - max_logo_height/2

    # If no watermark provided, try to load default watermark.png
    if not watermark_path:
        default_watermark = Path(__file__).parent / "watermark.png"
        if default_watermark.exists():
            watermark_path = str(default_watermark)

    if watermark_path and os.path.exists(watermark_path):
        # Use custom watermark
        try:
            logo_img = Image.open(watermark_path)
            # Calculate logo dimensions to fit in header (leave some padding)
            logo_aspect = logo_img.width / logo_img.height
            logo_height = max_logo_height
            logo_width = logo_height * logo_aspect

            # Draw logo
            c.drawImage(ImageReader(logo_img), logo_x, logo_y,
                       width=logo_width, height=logo_height,
                       preserveAspectRatio=True, mask='auto')

            logo_img.close()
            logo_width += 15  # Add spacing after logo
        except Exception as e:
            print(f"Warning: Could not load watermark: {e}")
            # Fall back to built-in watermark
            logo_width = max_logo_height  # Make it square
            draw_builtin_watermark(c, logo_x, logo_y, logo_width, max_logo_height)
            logo_width += 15
    else:
        # Use built-in camera icon watermark
        logo_width = max_logo_height  # Make it square
        draw_builtin_watermark(c, logo_x, logo_y, logo_width, max_logo_height)
        logo_width += 15  # Add spacing after logo

    # Title (position after logo if present)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(MARGIN + logo_width, PAGE_HEIGHT - HEADER_HEIGHT/2 - 4, project_name)

    # Page number
    c.setFont("Helvetica", 10)
    page_text = f"Oldal {page_num} / {total_pages}"
    text_width = c.stringWidth(page_text, "Helvetica", 10)
    c.drawString(PAGE_WIDTH - MARGIN - text_width, PAGE_HEIGHT - HEADER_HEIGHT/2 - 4, page_text)


def draw_footer(c):
    """Draw professional footer on page"""
    # Footer line
    c.setStrokeColor(LIGHT_GRAY)
    c.setLineWidth(1)
    c.line(MARGIN, FOOTER_HEIGHT, PAGE_WIDTH - MARGIN, FOOTER_HEIGHT)

    # Footer text
    c.setFillColor(PRIMARY_COLOR)
    c.setFont("Helvetica", 8)
    date_str = datetime.now().strftime("%Y. %B %d.")
    c.drawString(MARGIN, FOOTER_HEIGHT/2 - 4, f"Készült: {date_str}")

    # Right side text
    footer_right = "Válaszd ki a fotókat és az azonosító számokat küldd vissza nekem emailben: peleiniki@gmail.com"
    text_width = c.stringWidth(footer_right, "Helvetica", 8)
    c.drawString(PAGE_WIDTH - MARGIN - text_width, FOOTER_HEIGHT/2 - 4, footer_right)


def draw_checkbox_with_label(c, x, y, label):
    """Draw a checkbox with label for photo selection"""
    # Checkbox border
    c.setStrokeColor(PRIMARY_COLOR)
    c.setFillColor(white)
    c.setLineWidth(1)
    c.rect(x, y, CHECKBOX_SIZE, CHECKBOX_SIZE, fill=True, stroke=True)

    # Checkmark instruction (light gray)
    c.setFillColor(LIGHT_GRAY)
    check_x = x + CHECKBOX_SIZE/4
    check_y = y + CHECKBOX_SIZE/4
    c.setFont("Helvetica-Bold", 8)
    c.drawString(check_x, check_y, "✓")

    # Label (filename)
    c.setFillColor(PRIMARY_COLOR)
    c.setFont("Helvetica", FILENAME_FONT_SIZE)
    c.drawString(x + CHECKBOX_SIZE + 5, y + 2, label)


def calculate_total_pages(jpeg_files, cell_width, available_height, top_margin):
    """Calculate how many pages are needed for all images"""
    page_count = 1
    current_y = top_margin
    image_index = 0

    while image_index < len(jpeg_files):
        # Look ahead to see how many images are in this row
        row_start = image_index
        row_end = min(row_start + IMAGES_PER_ROW, len(jpeg_files))
        row_images = row_end - row_start

        # Calculate the height needed for this row
        max_row_height = 0
        for i in range(row_images):
            img_file = jpeg_files[row_start + i]
            try:
                img = Image.open(img_file)
                img_width, img_height = img.size
                aspect_ratio = img_width / img_height
                scaled_height = cell_width / aspect_ratio

                # Limit portrait height to ensure it fits on page with filename
                # Available height minus filename space and some margin
                max_safe_height = available_height - FILENAME_HEIGHT - SPACING - 20
                max_portrait_height = min(cell_width * 1.5, max_safe_height)
                if scaled_height > max_portrait_height:
                    scaled_height = max_portrait_height

                img.close()
                max_row_height = max(max_row_height, scaled_height)
            except:
                max_row_height = max(max_row_height, cell_width * (2/3))

        row_total_height = max_row_height + FILENAME_HEIGHT

        # Check if this row fits on the page
        if current_y + row_total_height + SPACING > available_height and current_y > top_margin:
            # Start new page (but only if we already have content on current page)
            page_count += 1
            current_y = top_margin

        # Add row to current page
        current_y += row_total_height + SPACING
        image_index += row_images

    return page_count


def create_pdf_grid(jpeg_folder, output_pdf, project_name=None, watermark_path=None):
    """Create a PDF grid from JPEG images with dynamic row heights and optional watermark"""

    # Get all JPEG files
    jpeg_folder_path = Path(jpeg_folder)
    jpeg_files = sorted(jpeg_folder_path.glob("*.jpg")) + sorted(jpeg_folder_path.glob("*.jpeg"))

    if not jpeg_files:
        print(f"No JPEG files found in {jpeg_folder}")
        return False

    print(f"Found {len(jpeg_files)} JPEG files")

    # Use provided project name, or extract from folder path
    if not project_name:
        # If we're in a final_jpegs subfolder, use the parent folder name
        # Otherwise use the folder name itself
        if jpeg_folder_path.name == 'final_jpegs':
            project_name = jpeg_folder_path.parent.name
        else:
            project_name = jpeg_folder_path.name

        # Fallback to default if empty
        if not project_name or project_name.lower() in ['', 'selected_photos']:
            project_name = "Photo Selection"

    # Calculate available space (accounting for header and footer)
    available_width = PAGE_WIDTH - (MARGIN * 2)
    # Reduced top margin for less padding between header and images
    TOP_MARGIN = 0.08 * inch  # Smaller top margin
    available_height = PAGE_HEIGHT - HEADER_HEIGHT - FOOTER_HEIGHT - TOP_MARGIN - MARGIN
    cell_width = (available_width - (SPACING * (IMAGES_PER_ROW - 1))) / IMAGES_PER_ROW

    print(f"Page: {PAGE_WIDTH:.1f} x {PAGE_HEIGHT:.1f} points")
    print(f"Cell width: {cell_width:.1f} points")
    print(f"Project: {project_name}")

    # First pass: count total pages needed
    print("Calculating page layout...")
    total_pages = calculate_total_pages(jpeg_files, cell_width, available_height, TOP_MARGIN)
    print(f"Total pages needed: {total_pages}")

    # Create PDF with compression
    c = canvas.Canvas(str(output_pdf), pagesize=PAGE_SIZE, pageCompression=1)
    c.setTitle(f"{project_name} - Photo Selection")
    c.setAuthor("Photo Selector Helper")
    c.setPageCompression(1)

    image_index = 0
    page_num = 1

    while image_index < len(jpeg_files):
        print(f"Creating page {page_num}...")

        # Draw header and footer
        draw_header(c, page_num, total_pages, project_name, watermark_path)
        draw_footer(c)

        # Dynamic layout - fit as many rows as possible on this page
        current_y = TOP_MARGIN  # Use reduced top margin for less padding
        images_on_page = 0

        while current_y < available_height and image_index + images_on_page < len(jpeg_files):
            # Look ahead to see how many images are in this row
            row_start = image_index + images_on_page
            row_end = min(row_start + IMAGES_PER_ROW, len(jpeg_files))
            row_images = row_end - row_start

            # Calculate the height needed for this row
            max_row_height = 0

            for i in range(row_images):
                img_file = jpeg_files[row_start + i]
                try:
                    img = Image.open(img_file)
                    img_width, img_height = img.size
                    aspect_ratio = img_width / img_height

                    # Calculate scaled height to fit cell width
                    scaled_height = cell_width / aspect_ratio

                    # Limit portrait height to ensure it fits on page with filename
                    # Available height minus filename space and some margin
                    max_safe_height = available_height - FILENAME_HEIGHT - SPACING - 20
                    max_portrait_height = min(cell_width * 1.5, max_safe_height)
                    if scaled_height > max_portrait_height:
                        scaled_height = max_portrait_height

                    img.close()
                    max_row_height = max(max_row_height, scaled_height)
                except Exception as e:
                    print(f"Error checking {img_file.name}: {e}")
                    max_row_height = max(max_row_height, cell_width * (2/3))

            # Add filename space
            row_total_height = max_row_height + FILENAME_HEIGHT

            # Check if this row fits on the page
            if current_y + row_total_height + SPACING > available_height:
                # Row doesn't fit, but if this is the first row on the page, we MUST include it
                # Otherwise we get an infinite loop
                if images_on_page == 0:
                    # Force this row to fit (better to overflow than infinite loop)
                    pass  # Continue to draw this row anyway
                else:
                    # Row doesn't fit and we already have content, start new page
                    break

            # Row fits! Draw the images
            for col in range(row_images):
                img_idx = row_start + col
                jpeg_file = jpeg_files[img_idx]

                # Calculate x position
                x_pos = MARGIN + (col * (cell_width + SPACING))
                # Calculate y position (flip for PDF coordinates, account for header)
                y_pos = PAGE_HEIGHT - HEADER_HEIGHT - MARGIN - current_y - row_total_height

                try:
                    # Open and prepare image
                    img = Image.open(jpeg_file)
                    img_width, img_height = img.size
                    aspect_ratio = img_width / img_height

                    # Calculate scaled dimensions
                    target_width = cell_width
                    target_height = cell_width / aspect_ratio

                    # Limit portrait images to ensure they fit on page
                    max_safe_height = available_height - FILENAME_HEIGHT - SPACING - 20
                    max_portrait_height = min(cell_width * 1.5, max_safe_height)
                    if target_height > max_portrait_height:
                        target_height = max_portrait_height
                        target_width = target_height * aspect_ratio

                    # Calculate pixel dimensions at target DPI
                    target_width_px = int((target_width / 72) * MAX_IMAGE_DPI)
                    target_height_px = int((target_height / 72) * MAX_IMAGE_DPI)

                    # Resize image to reduce file size
                    if img_width > target_width_px or img_height > target_height_px:
                        img = img.copy()
                        img.thumbnail((target_width_px, target_height_px), Image.Resampling.LANCZOS)

                    # Convert to RGB if necessary
                    if img.mode in ('RGBA', 'LA', 'P'):
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                        img = rgb_img

                    # Center image in cell horizontally
                    img_x = x_pos + (cell_width - target_width) / 2
                    img_y = y_pos + FILENAME_HEIGHT

                    # Draw image with border
                    c.drawImage(ImageReader(img), img_x, img_y,
                               width=target_width, height=target_height,
                               preserveAspectRatio=True)

                    # Draw border around image
                    c.setStrokeColor(LIGHT_GRAY)
                    c.setLineWidth(0.5)
                    c.rect(img_x, img_y, target_width, target_height, fill=False, stroke=True)

                    # Draw checkbox with filename below image
                    # Extract just the number from filename (e.g., "Project_00597.ARW" -> "00597")
                    filename = jpeg_file.stem
                    number_match = re.search(r'_(\d+)', filename)
                    display_name = number_match.group(1) if number_match else filename
                    checkbox_x = x_pos + (cell_width / 2) - (CHECKBOX_SIZE / 2) - 40
                    checkbox_y = y_pos + 5
                    draw_checkbox_with_label(c, checkbox_x, checkbox_y, display_name)

                    img.close()

                except Exception as e:
                    print(f"Error processing {jpeg_file.name}: {e}")

            # Move to next row
            current_y += row_total_height + SPACING
            images_on_page += row_images

        # Show page
        c.showPage()
        image_index += images_on_page
        page_num += 1

    # Save PDF
    c.save()
    print(f"\nPDF created successfully: {output_pdf}")
    print(f"Total pages: {page_num - 1}")
    print(f"Total images: {len(jpeg_files)}")

    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 create_pdf_grid.py <folder_with_jpegs> [project_name] [watermark_path]")
        sys.exit(1)

    input_folder = sys.argv[1]
    project_name = sys.argv[2] if len(sys.argv) > 2 else None
    watermark_path = sys.argv[3] if len(sys.argv) > 3 else None

    # Look for JPEGs in final_jpegs subfolder
    jpeg_folder = Path(input_folder) / "final_jpegs"

    if not jpeg_folder.exists():
        print(f"Warning: {jpeg_folder} not found, trying parent folder...")
        # Try the input folder itself
        jpeg_folder = Path(input_folder)

    # Create PDF filename based on project name
    if project_name and project_name != "Photo Selection":
        # Sanitize project name for filename (replace spaces and special chars)
        safe_name = project_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
        output_pdf = Path(input_folder) / f"{safe_name}.pdf"
    else:
        output_pdf = Path(input_folder) / "photo_grid.pdf"

    print("=" * 60)
    print("PDF Grid Generator")
    print("=" * 60)
    print(f"Input folder: {jpeg_folder}")
    print(f"Output PDF: {output_pdf}")
    if project_name:
        print(f"Project name: {project_name}")

    # Check if folder exists and is readable
    if not jpeg_folder.exists():
        print(f"\nERROR: Folder does not exist: {jpeg_folder}")
        sys.exit(1)

    if not jpeg_folder.is_dir():
        print(f"\nERROR: Not a directory: {jpeg_folder}")
        sys.exit(1)

    print()

    if watermark_path:
        print(f"Watermark: {watermark_path}")

    try:
        success = create_pdf_grid(jpeg_folder, output_pdf, project_name, watermark_path)

        if success:
            print("\n" + "=" * 60)
            print("SUCCESS!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("FAILED")
            print("=" * 60)
            sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
