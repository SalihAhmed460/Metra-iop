from PIL import Image, ImageDraw
import os

# Ensure directory exists
os.makedirs('media/profile_pics', exist_ok=True)

# Create a default profile picture
size = (400, 400)
bg_color = (13, 110, 253)  # Bootstrap primary color
image = Image.new('RGB', size, bg_color)

# Create circular mask
mask = Image.new('L', size, 0)
draw = ImageDraw.Draw(mask)
draw.ellipse((0, 0) + size, fill=255)

# Apply mask to the image
output = Image.new('RGB', size, (0, 0, 0))
output.paste(image, mask=mask)

# Add a light circle in the top portion for the "head"
draw = ImageDraw.Draw(output)
draw.ellipse((150, 80, 250, 180), fill=(255, 255, 255))

# Add a larger light rounded rectangle in the bottom portion for the "body"
draw.rounded_rectangle((100, 200, 300, 400), radius=50, fill=(255, 255, 255))

# Save the default profile picture
output.save('media/profile_pics/default.png')
print("Default profile picture created successfully.")