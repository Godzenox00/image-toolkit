import os
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
from PIL.ImageDraw import Draw
from PIL.ImageFont import load_default, truetype
from PIL.ExifTags import TAGS, GPSTAGS

def print_zenox_banner():
    banner = """
███████╗███████╗███╗   ██╗ ██████╗ ██╗  ██╗     ██████╗  ██████╗ ██████╗ 
╚══███╔╝██╔════╝████╗  ██║██╔═══██╗╚██╗██╔╝    ██╔════╝ ██╔═══██╗██╔══██╗
  ███╔╝ █████╗  ██╔██╗ ██║██║   ██║ ╚███╔╝     ██║  ███╗██║   ██║██║  ██║
 ███╔╝  ██╔══╝  ██║╚██╗██║██║   ██║ ██╔██╗     ██║   ██║██║   ██║██║  ██║
███████╗███████║██║ ╚████║╚██████╔╝██╔╝ ██╗    ╚██████╔╝╚██████╔╝██████╔╝
╚══════╝╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝     ╚═════╝  ╚═════╝ ╚═════╝ 
"""
    print(banner)

def get_decimal_from_dms(dms, ref):
    try:
        degrees = float(dms[0])
        minutes = float(dms[1]) / 60.0
        seconds = float(dms[2]) / 3600.0
        decimal = degrees + minutes + seconds
        if ref in ['S', 'W']:
            decimal = -decimal
        return decimal
    except Exception:
        return None

# ==========================================
# TOOL 1: EXIF & LOCATION VIEWER
# ==========================================
def tool_1_exif():
    print("\n" + "="*50 + "\n      [1] EXIF & LOCATION VIEWER\n" + "="*50)
    path = input("Enter image path: ").strip()
    if not os.path.exists(path): print("❌ File not found."); return
    try:
        img = Image.open(path)
        exif = img.getexif()
        if not exif: print("⚠️ No EXIF data found."); return
        lat, lon, lat_ref, lon_ref, gps_found = None, None, None, None, False
        for tag_id, val in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag != 'GPSInfo':
                print(f"{str(tag):<25}: {val}")
            else:
                gps_found = True
                for t in val:
                    sub = GPSTAGS.get(t, t)
                    if sub == 'GPSLatitude': lat = val[t]
                    elif sub == 'GPSLatitudeRef': lat_ref = val[t]
                    elif sub == 'GPSLongitude': lon = val[t]
                    elif sub == 'GPSLongitudeRef': lon_ref = val[t]
        if gps_found and lat and lon and lat_ref and lon_ref:
            lat_dec = get_decimal_from_dms(lat, lat_ref)
            lon_dec = get_decimal_from_dms(lon, lon_ref)
            print("\n📍 GPS Coordinates:")
            print(f"  Latitude : {lat_dec}\n  Longitude: {lon_dec}")
            print(f"  Map Link : https://www.google.com/maps?q={lat_dec},{lon_dec}")
    except Exception as e: print(f"❌ Error: {e}")

# ==========================================
# TOOL 2: IMAGE STATS & COLORS
# ==========================================
def tool_2_stats():
    print("\n" + "="*50 + "\n      [2] IMAGE STATS & COLOR PALETTE\n" + "="*50)
    path = input("Enter image path: ").strip()
    if not os.path.exists(path): print("❌ File not found."); return
    try:
        size_kb = os.path.getsize(path) / 1024
        img = Image.open(path)
        print(f"  Size   : {size_kb:.2f} KB\n  Pixels : {img.size[0]} x {img.size[1]}\n  Format : {img.format}\n  Mode   : {img.mode}")
        small = img.resize((50, 50))
        colors = small.getcolors(2500)
        sorted_cols = sorted(colors, key=lambda x: x[0], reverse=True)
        print("\n🎨 Top 3 Dominant Colors (RGB):")
        for i in range(min(3, len(sorted_cols))):
            print(f"  Color {i+1}: {sorted_cols[i][1]}")
    except Exception as e: print(f"❌ Error: {e}")

# ==========================================
# TOOL 3: ASCII ART CONVERTER
# ==========================================
def tool_3_ascii():
    print("\n" + "="*50 + "\n      [3] ASCII ART IMAGE CONVERTER\n" + "="*50)
    path = input("Enter image path: ").strip()
    if not os.path.exists(path): print("❌ File not found."); return
    try:
        img = Image.open(path)
        w = 80
        h = int(w * (img.height / img.width) * 0.55)
        img = img.resize((w, h)).convert("L")
        chars = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]
        pixels = img.getdata()
        txt = "".join(chars[p * len(chars) // 256] for p in pixels)
        print("\n".join(txt[i:i+w] for i in range(0, len(txt), w)))
    except Exception as e: print(f"❌ Error: {e}")

# ==========================================
# TOOL 4: TEXT WATERMARK
# ==========================================
def tool_4_watermark():
    print("\n" + "="*50 + "\n      [4] TEXT WATERMARK GENERATOR\n" + "="*50)
    path = input("Enter image path: ").strip()
    if not os.path.exists(path): print("❌ File not found."); return
    text = input("Watermark text (default 'ZENOX GOD'): ").strip() or "ZENOX GOD"
    out = input("Output filename (default 'watermarked.jpg'): ").strip() or "watermarked.jpg"
    try:
        base = Image.open(path).convert("RGBA")
        layer = Image.new("RGBA", base.size, (255, 255, 255, 0))
        try: font = truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 100)
        except: font = load_default()
        draw = Draw(layer)
        bbox = draw.textbbox((0, 0), text, font=font)
        pos = ((base.width - (bbox[2] - bbox[0])) / 2, (base.height - (bbox[3] - bbox[1])) / 2)
        draw.text(pos, text, fill=(255, 255, 255, 128), font=font)
        Image.alpha_composite(base, layer).convert("RGB").save(out, "JPEG")
        print(f"✅ Saved as '{out}'")
    except Exception as e: print(f"❌ Error: {e}")

# ==========================================
# TOOL 5: RESIZE IMAGE
# ==========================================
def tool_5_resize():
    print("\n" + "="*50 + "\n      [5] RESIZE IMAGE\n" + "="*50)
    path = input("Enter image path: ").strip()
    if not os.path.exists(path): print("❌ File not found."); return
    try:
        img = Image.open(path)
        print(f"Current dimensions: {img.size}")
        nw = int(input("Enter new width: "))
        nh = int(input("Enter new height: "))
        out = input("Output filename (default 'resized.jpg'): ").strip() or "resized.jpg"
        img.resize((nw, nh)).save(out)
        print(f"✅ Saved as '{out}'")
    except Exception as e: print(f"❌ Error: {e}")

# ==========================================
# TOOL 6: FORMAT CONVERTER
# ==========================================
def tool_6_convert():
    print("\n" + "="*50 + "\n      [6] CONVERT IMAGE FORMAT\n" + "="*50)
    path = input("Enter image path: ").strip()
    if not os.path.exists(path): print("❌ File not found."); return
    fmt = input("Target format (PNG, WEBP, JPEG, BMP): ").strip().upper()
    out = f"converted.{fmt.lower()}"
    try:
        img = Image.open(path)
        if fmt == "JPEG" and img.mode in ("RGBA", "P"): img = img.convert("RGB")
        img.save(out, fmt)
        print(f"✅ Saved as '{out}'")
    except Exception as e: print(f"❌ Error: {e}")

# ==========================================
# TOOL 7: GRAYSCALE FILTER
# ==========================================
def tool_7_grayscale():
    print("\n" + "="*50 + "\n      [7] GRAYSCALE FILTER\n" + "="*50)
    path = input("Enter image path: ").strip()
    if not os.path.exists(path): print("❌ File not found."); return
    out = input("Output filename (default 'grayscale.jpg'): ").strip() or "grayscale.jpg"
    try:
        Image.open(path).convert("L").save(out)
        print(f"✅ Saved as '{out}'")
    except Exception as e: print(f"❌ Error: {e}")

# ==========================================
# TOOL 8: ROTATE & FLIP
# ==========================================
def tool_8_transform():
    print("\n" + "="*50 + "\n      [8] ROTATE & FLIP IMAGE\n" + "="*50)
    path = input("Enter image path: ").strip()
    if not os.path.exists(path): print("❌ File not found."); return
    print("1. Rotate 90°\n2. Rotate 180°\n3. Rotate 270°\n4. Flip Horizontal\n5. Flip Vertical")
    sub = input("Choose (1-5): ").strip()
    out = input("Output filename (default 'transformed.jpg'): ").strip() or "transformed.jpg"
    try:
        img = Image.open(path)
        if sub == '1': img = img.rotate(270, expand=True)
        elif sub == '2': img = img.rotate(180, expand=True)
        elif sub == '3': img = img.rotate(90, expand=True)
        elif sub == '4': img = ImageOps.mirror(img)
        elif sub == '5': img = ImageOps.flip(img)
        img.save(out)
        print(f"✅ Saved as '{out}'")
    except Exception as e: print(f"❌ Error: {e}")

# ==========================================
# TOOL 9: CROP IMAGE
# ==========================================
def tool_9_crop():
    print("\n" + "="*50 + "\n      [9] CROP IMAGE\n" + "="*50)
    path = input("Enter image path: ").strip()
    if not os.path.exists(path): print("❌ File not found."); return
    try:
        img = Image.open(path)
        w, h = img.size
        print(f"Size: {w}x{h}")
        l = int(input("Left: ")); t = int(input("Top: ")); r = int(input("Right: ")); b = int(input("Bottom: "))
        out = input("Output filename (default 'cropped.jpg'): ").strip() or "cropped.jpg"
        img.crop((l, t, r, b)).save(out)
        print(f"✅ Saved as '{out}'")
    except Exception as e: print(f"❌ Error: {e}")

# ==========================================
# TOOL 10: THUMBNAIL GENERATOR
# ==========================================
def tool_10_thumbnail():
    print("\n" + "="*50 + "\n      [10] GENERATE THUMBNAIL\n" + "="*50)
    path = input("Enter image path: ").strip()
    if not os.path.exists(path): print("❌ File not found."); return
    out = input("Output filename (default 'thumbnail.jpg'): ").strip() or "thumbnail.jpg"
    try:
        img = Image.open(path)
        img.thumbnail((150, 150))
        img.save(out)
        print(f"✅ Saved as '{out}'")
    except Exception as e: print(f"❌ Error: {e}")

# ==========================================
# TOOL 11: ADJUST BRIGHTNESS & CONTRAST
# ==========================================
def tool_11_adjust():
    print("\n" + "="*50 + "\n      [11] BRIGHTNESS & CONTRAST\n" + "="*50)
    path = input("Enter image path: ").strip()
    if not os.path.exists(path): print("❌ File not found."); return
    b_factor = float(input("Brightness factor (e.g. 1.0 = normal, 1.5 = brighter): ") or 1.0)
    c_factor = float(input("Contrast factor (e.g. 1.0 = normal, 1.5 = higher contrast): ") or 1.0)
    out = input("Output filename (default 'adjusted.jpg'): ").strip() or "adjusted.jpg"
    try:
        img = Image.open(path)
        img = ImageEnhance.Brightness(img).enhance(b_factor)
        img = ImageEnhance.Contrast(img).enhance(c_factor)
        img.save(out)
        print(f"✅ Saved as '{out}'")
    except Exception as e: print(f"❌ Error: {e}")

# ==========================================
# TOOL 12: GAUSSIAN BLUR
# ==========================================
def tool_12_blur():
    print("\n" + "="*50 + "\n      [12] GAUSSIAN BLUR\n" + "="*50)
    path = input("Enter image path: ").strip()
    if not os.path.exists(path): print("❌ File not found."); return
    radius = float(input("Blur radius (e.g. 2.0): ") or 2.0)
    out = input("Output filename (default 'blurred.jpg'): ").strip() or "blurred.jpg"
    try:
        Image.open(path).filter(ImageFilter.GaussianBlur(radius)).save(out)
        print(f"✅ Saved as '{out}'")
    except Exception as e: print(f"❌ Error: {e}")

# ==========================================
# TOOL 13: SHARPEN FILTER
# ==========================================
def tool_13_sharpen():
    print("\n" + "="*50 + "\n      [13] SHARPEN IMAGE\n" + "="*50)
    path = input("Enter image path: ").strip()
    if not os.path.exists(path): print("❌ File not found."); return
    out = input("Output filename (default 'sharpened.jpg'): ").strip() or "sharpened.jpg"
    try:
        Image.open(path).filter(ImageFilter.SHARPEN).save(out)
        print(f"✅ Saved as '{out}'")
    except Exception as e: print(f"❌ Error: {e}")

# ==========================================
# TOOL 14: INVERT COLORS (NEGATIVE)
# ==========================================
def tool_14_invert():
    print("\n" + "="*50 + "\n      [14] INVERT COLORS (NEGATIVE)\n" + "="*50)
    path = input("Enter image path: ").strip()
    if not os.path.exists(path): print("❌ File not found."); return
    out = input("Output filename (default 'inverted.jpg'): ").strip() or "inverted.jpg"
    try:
        img = Image.open(path)
        if img.mode == 'RGBA':
            r, g, b, a = img.split()
            rgb = Image.merge('RGB', (r, g, b))
            inv = ImageOps.invert(rgb).convert('RGBA')
            inv.putalpha(a)
            inv.save(out)
        else:
            ImageOps.invert(img.convert('RGB')).save(out)
        print(f"✅ Saved as '{out}'")
    except Exception as e: print(f"❌ Error: {e}")

# ==========================================
# TOOL 15: ADD BORDER / FRAME
# ==========================================
def tool_15_border():
    print("\n" + "="*50 + "\n      [15] ADD IMAGE BORDER\n" + "="*50)
    path = input("Enter image path: ").strip()
    if not os.path.exists(path): print("❌ File not found."); return
    border_size = int(input("Border thickness in pixels (e.g. 20): ") or 20)
    out = input("Output filename (default 'bordered.jpg'): ").strip() or "bordered.jpg"
    try:
        ImageOps.expand(Image.open(path), border=border_size, fill='black').save(out)
        print(f"✅ Saved as '{out}'")
    except Exception as e: print(f"❌ Error: {e}")

# ==========================================
# TOOL 16: SEPIA TONE FILTER
# ==========================================
def tool_16_sepia():
    print("\n" + "="*50 + "\n      [16] SEPIA TONE FILTER\n" + "="*50)
    path = input("Enter image path: ").strip()
    if not os.path.exists(path): print("❌ File not found."); return
    out = input("Output filename (default 'sepia.jpg'): ").strip() or "sepia.jpg"
    try:
        img = Image.open(path).convert("RGB")
        width, height = img.size
        pixels = img.load()
        for py in range(height):
            for px in range(width):
                r, g, b = pixels[px, py]
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                pixels[px, py] = (min(tr, 255), min(tg, 255), min(tb, 255))
        img.save(out)
        print(f"✅ Saved as '{out}'")
    except Exception as e: print(f"❌ Error: {e}")

# ==========================================
# TOOL 17: MIRROR IMAGE
# ==========================================
def tool_17_mirror():
    print("\n" + "="*50 + "\n      [17] MIRROR IMAGE (HORIZONTAL)\n" + "="*50)
    path = input("Enter image path: ").strip()
    if not os.path.exists(path): print("❌ File not found."); return
    out = input("Output filename (default 'mirrored.jpg'): ").strip() or "mirrored.jpg"
    try:
        ImageOps.mirror(Image.open(path)).save(out)
        print(f"✅ Saved as '{out}'")
    except Exception as e: print(f"❌ Error: {e}")

# ==========================================
# TOOL 18: COMPRESS / REDUCE QUALITY
# ==========================================
def tool_18_compress():
    print("\n" + "="*50 + "\n      [18] COMPRESS IMAGE QUALITY\n" + "="*50)
    path = input("Enter image path: ").strip()
    if not os.path.exists(path): print("❌ File not found."); return
    quality = int(input("Enter quality (1-100, default 50): ") or 50)
    out = input("Output filename (default 'compressed.jpg'): ").strip() or "compressed.jpg"
    try:
        img = Image.open(path)
        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
        img.save(out, "JPEG", quality=quality)
        print(f"✅ Saved as '{out}' (Quality: {quality})")
    except Exception as e: print(f"❌ Error: {e}")

# ==========================================
# TOOL 19: EDGE DETECTION FILTER
# ==========================================
def tool_19_edges():
    print("\n" + "="*50 + "\n      [19] EDGE DETECTION FILTER\n" + "="*50)
    path = input("Enter image path: ").strip()
    if not os.path.exists(path): print("❌ File not found."); return
    out = input("Output filename (default 'edges.jpg'): ").strip() or "edges.jpg"
    try:
        Image.open(path).filter(ImageFilter.FIND_EDGES).save(out)
        print(f"✅ Saved as '{out}'")
    except Exception as e: print(f"❌ Error: {e}")

# ==========================================
# TOOL 20: EXTRACT RED CHANNEL
# ==========================================
def tool_20_channel():
    print("\n" + "="*50 + "\n      [20] EXTRACT RED COLOR CHANNEL\n" + "="*50)
    path = input("Enter image path: ").strip()
    if not os.path.exists(path): print("❌ File not found."); return
    out = input("Output filename (default 'red_channel.jpg'): ").strip() or "red_channel.jpg"
    try:
        img = Image.open(path).convert("RGB")
        r, g, b = img.split()
        zero = Image.new("L", img.size, 0)
        Image.merge("RGB", (r, zero, zero)).save(out)
        print(f"✅ Saved as '{out}'")
    except Exception as e: print(f"❌ Error: {e}")


# ==========================================
# MAIN INTERFACE
# ==========================================
def main_menu():
    while True:
        print_zenox_banner()
        print("\n" + "="*60)
        print("          IMAGE TOOLKIT             ")
        print("="*60)
        print(" 1. EXIF & Location Viewer         11. Adjust Brightness/Contrast")
        print(" 2. Image Stats & Color Palette    12. Gaussian Blur Filter")
        print(" 3. ASCII Art Image Converter      13. Sharpen Image")
        print(" 4. Text Watermark Generator       14. Invert Colors (Negative)")
        print(" 5. Resize Image                   15. Add Image Border")
        print(" 6. Convert Image Format           16. Sepia Tone Filter")
        print(" 7. Grayscale Filter               17. Mirror Image (Horizontal)")
        print(" 8. Rotate & Flip Image            18. Compress Image Quality")
        print(" 9. Crop Image                     19. Edge Detection Filter")
        print("10. Generate Thumbnail (150x150)   20. Extract Red Channel")
        print("------------------------------------------------------------")
        print("21. Exit")

    
        

        choice = input("Select an option (1-21): ").strip()

        if choice == '1': tool_1_exif()
        elif choice == '2': tool_2_stats()
        elif choice == '3': tool_3_ascii()
        elif choice == '4': tool_4_watermark()
        elif choice == '5': tool_5_resize()
        elif choice == '6': tool_6_convert()
        elif choice == '7': tool_7_grayscale()
        elif choice == '8': tool_8_transform()
        elif choice == '9': tool_9_crop()
        elif choice == '10': tool_10_thumbnail()
        elif choice == '11': tool_11_adjust()
        elif choice == '12': tool_12_blur()
        elif choice == '13': tool_13_sharpen()
        elif choice == '14': tool_14_invert()
        elif choice == '15': tool_15_border()
        elif choice == '16': tool_16_sepia()
        elif choice == '17': tool_17_mirror()
        elif choice == '18': tool_18_compress()
        elif choice == '19': tool_19_edges()
        elif choice == '20': tool_20_channel()
        elif choice == '21':
            print("Exiting...")
            break
        else:
            print("❌ Invalid option. Please choose between 1 and 21.")

        input("\nPress Enter to return to the menu...")

if __name__ == "__main__":
    main_menu()
