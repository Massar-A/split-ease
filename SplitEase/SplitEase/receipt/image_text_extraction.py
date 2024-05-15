import pytesseract
from PIL import Image

def read_test(img):
    img = Image.open(img)
    text = pytesseract.image_to_string(img)
    return text