import mss
from PIL import Image
import pytesseract
import re
from pynput import mouse, keyboard
import pyautogui
import time
from PIL import Image, ImageFilter, ImageEnhance
import pytesseract
import numpy as np


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
def prendre_screenshot():
    with mss.MSS() as sct:
        region = {
    "left": -133,
    "top": 1044,
    "width": 77,   # -56 - (-133)
    "height": 37   # 1081 - 1044
    }

        screenshot = sct.grab(region)

        img = Image.frombytes(
        "RGB",
        screenshot.size,
        screenshot.rgb
    )
    return img

def prendre_screenshot_vers():
    with mss.MSS() as sct:

        x1, y1 = -1607, 595   # haut-gauche
        x2, y2 = -1457, 616   # bas-droite

        region = {
            "left": x1,
            "top": y1,
            "width": x2 - x1,
            "height": y2 - y1
        }

        screenshot = sct.grab(region)

        img = Image.frombytes(
            "RGB",
            screenshot.size,
            screenshot.rgb
        )

        return img
def prendre_screenshot_lait():
    with mss.MSS() as sct:

        region = {
    "left": -1142,
    "top": 393,
    "width": 150,   # -998 - (-1142)
    "height": 38    # 421 - 383
    }

        screenshot = sct.grab(region)

        img = Image.frombytes(
            "RGB",
            screenshot.size,
            screenshot.rgb
        )

        return img
def index_to_pos(index):
    index = index % 30
    origin_x = -1172
    origin_y = 1017

    cell_w = 105   # approx (ton spacing X)
    cell_h = 110   # approx (ton spacing Y)
    x = index % 10
    y = index // 10

    screen_x = origin_x + x * cell_w
    screen_y = origin_y + y * cell_h

    return screen_x, screen_y
    
def changer_page(index):
    return index % 30 == 0

def preparer_image(img):
    img = img.resize((img.width * 3, img.height * 3), Image.LANCZOS)
    img = img.convert("RGB")
    
    # Garde les pixels quasi-blanc (255±10), tout le reste → blanc
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y]
            if r >= 235 and g >= 235 and b >= 235:
                pixels[x, y] = (0, 0, 0)       # blanc pur → noir (chiffres)
            else:
                pixels[x, y] = (255, 255, 255)  # tout le reste → blanc
    
    img = img.convert("L")
    return img

def extraire_nombre(img):
    img = preparer_image(img)
    texte = pytesseract.image_to_string(img, config="--psm 7")
    texte = texte.strip()
    
    # Cherche un nombre avec suffixe B, M, K (ex: 4.49B, 505M, 2.3K)
    match = re.search(r'([\d,\.]+)\s*([BMKbmk]?)', texte)
    
    if not match:
        return None, texte
    
    nombre_str, suffixe = match.groups()
    
    # Enlève les virgules (760,400 → 760400)
    nombre_str = nombre_str.replace(',', '')
    
    try:
        nombre = float(nombre_str)
    except ValueError:
        return None, texte
    
    # Applique le multiplicateur
    multiplicateurs = {
        'b': 1_000_000_000,
        'm': 1_000_000,
        'k': 1_000,
    }
    
    if suffixe:
        nombre *= multiplicateurs.get(suffixe.lower(), 1)
    
    return nombre, texte


while True:
    img = prendre_screenshot_lait()
    img_prep = preparer_image(img)
    
    # Sauvegarde les deux pour comparer
    img.save("debug_original.png")
    img_prep.save("debug_preparee.png")
    
    valeur, texte_brut = extraire_nombre(img)
    print(f"Texte brut : '{texte_brut}'")
    
    if valeur is None:
        print("Valeur     : (rien détecté)")
    else:
        print(f"Valeur     : {valeur:,.0f}")
    
    time.sleep(2)
# while True:
#     img = prendre_screenshot()
#     texte = pytesseract.image_to_string(img, config="--psm 7")

#     match = re.search(r"(\d+)/(\d+)", texte)

#     if match:
#         print(match.group(1), match.group(2))
#         for i in range(int(match.group(1))):
#             if(changer_page(i)):
#                 pyautogui.scroll(-1)  # Scroll down pour changer de page
#             pos = index_to_pos(i)
#             pyautogui.click(pos[0], pos[1])
#             time.sleep(0.1)
#         time.sleep(5)
#     else:        
#         print("Aucun match trouvé")
    
    