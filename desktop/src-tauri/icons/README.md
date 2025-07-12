# Voice Separator Icon Placeholder

This directory should contain the application icons in the following formats:

- `32x32.png` - Small icon (32x32 pixels)
- `128x128.png` - Medium icon (128x128 pixels)  
- `128x128@2x.png` - Retina medium icon (256x256 pixels)
- `icon.icns` - macOS icon format
- `icon.ico` - Windows icon format
- `icon.png` - Generic PNG icon

## Quick Icon Generation

You can use online tools to generate icons from a single image:
- https://icon.kitchen/ 
- https://icongen.com/
- https://www.favicon-generator.org/

Or use command line tools like ImageMagick:

```bash
# From a source image (e.g., logo.png)
convert logo.png -resize 32x32 32x32.png
convert logo.png -resize 128x128 128x128.png
convert logo.png -resize 256x256 128x128@2x.png
```

For now, Tauri will use default icons if these are not present.
