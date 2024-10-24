import pytesseract
import numpy as np
from PIL import Image

def extract_text(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    
    # Remove symbols and split for better display
    chars_to_remove = "!()@-*?+/,'£$%^&*#"
    text = ''.join([char for char in text if char not in chars_to_remove])
    text_lines = text.split('\n')
    return text_lines

# Test the function
image_path = 'ImageToTextApp/app/static/uploads/215831_1296528.jpg'
extracted_text = extract_text(image_path)
print(extracted_text)