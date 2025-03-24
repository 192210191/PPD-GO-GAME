from PIL import Image
import os

# Load the logo image
logo_path = os.path.join('game', 'images', 'logo.jpg')
icon_path = os.path.join('game', 'images', 'logo.ico')

# Open and convert the image
img = Image.open(logo_path)
img.save(icon_path, format='ICO')
