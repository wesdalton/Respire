# Favicon & App Icon Setup

The app is configured to use the following favicon and app icon files. You'll need to generate these from your logo.svg:

## Required Files

Place these files in `/apps/web/public/`:

### Favicon Files
- `favicon-16x16.png` - 16x16 pixels (browser tabs)
- `favicon-32x32.png` - 32x32 pixels (browser tabs)
- `favicon.ico` - Traditional ICO format (optional, for legacy support)

### Apple Touch Icon
- `apple-touch-icon.png` - 180x180 pixels (iOS home screen)

### PWA Icons
- `icon-192x192.png` - 192x192 pixels (Android home screen)
- `icon-512x512.png` - 512x512 pixels (Android splash screen)

### Social Media
- `og-image.png` - 1200x630 pixels (Open Graph/Twitter card)

## Quick Generation

You can use online tools to generate these from your logo.svg:

1. **Favicon.io** (https://favicon.io)
   - Upload logo.svg
   - Download the favicon package
   - Extract and place files in public directory

2. **RealFaviconGenerator** (https://realfavicongenerator.net)
   - More comprehensive generator
   - Generates all sizes plus manifest

3. **Manual with ImageMagick** (command line):
   ```bash
   # Install ImageMagick if needed: brew install imagemagick

   # Convert SVG to various sizes
   convert logo.svg -resize 16x16 favicon-16x16.png
   convert logo.svg -resize 32x32 favicon-32x32.png
   convert logo.svg -resize 180x180 apple-touch-icon.png
   convert logo.svg -resize 192x192 icon-192x192.png
   convert logo.svg -resize 512x512 icon-512x512.png

   # For OG image, you might want a banner version
   convert logo.svg -resize 1200x630 og-image.png
   ```

## Current Status

✅ logo.svg exists and is being used as fallback
❌ PNG versions need to be generated
❌ OG image needs to be created

Once you generate these files, the app will automatically use them for:
- Browser tabs (favicon)
- iOS home screen (apple-touch-icon)
- Android home screen (PWA icons)
- Social media sharing (og-image)
