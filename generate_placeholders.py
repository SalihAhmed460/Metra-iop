from PIL import Image, ImageDraw, ImageFont
import os

# Ensure directories exist
os.makedirs('static/images', exist_ok=True)

# Create no-image placeholder
no_image = Image.new('RGB', (600, 400), color=(240, 240, 240))
d = ImageDraw.Draw(no_image)

# Add text
try:
    # Try to load a font (might not be available on all systems)
    font = ImageFont.truetype("arial.ttf", 40)
    d.text((300, 200), "No Image Available", fill=(150, 150, 150), font=font, anchor="mm")
except Exception:
    # Fallback if font not available
    d.text((200, 180), "No Image Available", fill=(150, 150, 150))

# Save the no-image placeholder
no_image.save('static/images/no-image.png')
print("Created no-image.png")

# Create hero image
hero_image = Image.new('RGB', (1200, 600), color=(13, 110, 253))  # Bootstrap primary color
d = ImageDraw.Draw(hero_image)

# Add some shapes to make it more interesting
for i in range(20):
    x1 = i * 60
    y1 = 0
    x2 = 1200
    y2 = i * 30
    d.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, 50), width=5)

# Add text
try:
    font = ImageFont.truetype("arial.ttf", 80)
    d.text((600, 300), "METRA TECH", fill=(255, 255, 255), font=font, anchor="mm")
except Exception:
    # Fallback
    d.text((400, 280), "METRA TECH", fill=(255, 255, 255))

# Save the hero image
hero_image.save('static/images/hero-image.png')
print("Created hero-image.png")

print("Placeholder images generated successfully.")