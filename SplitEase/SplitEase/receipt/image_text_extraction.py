import json

from PIL import Image
import io
import requests


def read_test(img):
    payload = {
        'apikey': "K88395828588957",
        'language': 'fre',
    }
    # L'image téléchargée est déjà fournie comme un fichier ouvert
    # Utilisez le nom de champ correct pour le fichier
    image = Image.open(img)
    compressed_image = compress_image(image)
    files = {'file': ('compressed_image.jpg', compressed_image, 'image/jpeg')}
    r = requests.post('https://api.ocr.space/parse/image', files=files, data=payload)
    return json.loads(r.content.decode())['ParsedResults'][0]['ParsedText']


def compress_image(image, max_size_kb=1024, step=5, min_quality=10):
    """
    Compresse une image pour qu'elle soit inférieure à max_size_kb sans changer le format.

    :param image: Image ouverte avec Pillow.
    :param max_size_kb: Taille maximale en kilo-octets.
    :param step: Pas de réduction de qualité.
    :param min_quality: Qualité minimale pour la compression.
    :return: Image compressée sous forme de bytes.
    """
    img_format = image.format  # Conserver le format original
    img_bytes = io.BytesIO()
    quality = 95

    # Enregistre l'image avec une qualité initiale
    image.save(img_bytes, format=img_format, quality=quality)

    # Réduire la qualité progressivement jusqu'à atteindre la taille désirée
    while img_bytes.tell() > max_size_kb * 1024 and quality > min_quality:
        quality -= step
        img_bytes = io.BytesIO()
        image.save(img_bytes, format=img_format, quality=quality)

    # Si la qualité atteint min_quality, et que la taille est toujours trop grande, on retourne l'image avec min_quality
    if quality <= min_quality and img_bytes.tell() > max_size_kb * 1024:
        img_bytes = io.BytesIO()
        image.save(img_bytes, format=img_format, quality=min_quality)

    img_bytes.seek(0)
    return img_bytes