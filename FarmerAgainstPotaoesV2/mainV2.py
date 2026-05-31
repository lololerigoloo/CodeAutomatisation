import mss
from PIL import Image, ImageEnhance
import pytesseract
import re
from pynput import mouse, keyboard
import pyautogui
import time
import threading
import signal
import sys

# ─── CONFIG ───────────────────────────────────────────────────────────────────
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

TIMELAIT       = 900
TIMEVERS       = 300
TIMEINVENTAIRE = 300
TIMEWACK       = 300
TIMEFERME      = 3600



couleurWack    = (231, 231, 33)
couleurStuff   = (131, 57, 26)
couleurBonSuff = (0, 255, 0)
couleurMauvaisSuff = (255, 0, 0)

listeFerme           = [(-1251, 1348), (-346, 1224),(-1515, 1255),(-1653, 606),(-1447, 610),(-1218, 621),(-1254, 1354)]
positionAchatFerme   = (-293, 1103)
positionWack         = (-508, 405)
listWack             = [(-508, 405), (-930, 1343), (-1615, 1349)]
listeDeleteStuff     = [(-102, 1186), (-1107, 956), (-1837, 1351)]
cubeZoneStuff        = [(-722, 488), (-715, 498)]
positionStuff        = (-1616, 1336)
positionSpam         = (-1506, 870)
positionVers         = (-1154, 1346)
positionPlusVers     = [(-706, 519), (-708, 701), (-711, 885), (-710, 1067)]
positionPlusLarve    = [(-840, 587), (-834, 765), (-835, 942), (-835, 1137)]
positionChangerPageVers = [(-1153, 1241), (-1022, 1246), (-898, 1249)]
positionEcrireVers   = (-332, 1218)
postionLait          = (-765, 1358)
positionEcrireLait   = (-332, 1107)
positionPlusLait     = [(-1851, 564), (-1855, 708), (-1846, 867), (-1845, 1026)]
positionPageLait     = [(-1587, 1251), (-1461, 1249)]

# ─── ÉTAT GLOBAL ──────────────────────────────────────────────────────────────
listener           = None
keyboard_listener  = None
automation_running = False
automation_thread  = None
clic_humain        = True
timeInventaire     = time.time() - TIMEINVENTAIRE
timeWack           = time.time() - TIMEWACK
timeVers           = time.time() - TIMEVERS
timeLait           = time.time() - TIMELAIT
timeFerme          = time.time() - TIMEFERME
# ─── SCREENSHOTS ──────────────────────────────────────────────────────────────
def prendre_screenshot_inventaire():
   with mss.MSS() as sct:
        region = {"left": -133, "top": 1044, "width": 77, "height": 37}
        screenshot = sct.grab(region)
        return Image.frombytes("RGB", screenshot.size, screenshot.rgb)

def prendre_screenshot_vers():
    with mss.MSS() as sct:
        region = {"left": -1607, "top": 595, "width": 150, "height": 21}
        screenshot = sct.grab(region)
        return Image.frombytes("RGB", screenshot.size, screenshot.rgb)

def prendre_screenshot_larve():
    with mss.MSS() as sct:
        region = {"left": -1582, "top": 678, "width": 150, "height": 21}
        screenshot = sct.grab(region)
        return Image.frombytes("RGB", screenshot.size, screenshot.rgb)

def prendre_screenshot_lait():
    with mss.MSS() as sct:
        region = {"left": -1142, "top": 383, "width": 144, "height": 38}
        screenshot = sct.grab(region)
        return Image.frombytes("RGB", screenshot.size, screenshot.rgb)

# ─── IMAGE ────────────────────────────────────────────────────────────────────
def preparer_image_lait(img):
    img = img.resize((img.width * 3, img.height * 3), Image.LANCZOS)
    img = img.convert("RGB")
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y]
            if r >= 245 and g >= 245 and b >= 245:
                pixels[x, y] = (0, 0, 0)
            else:
                pixels[x, y] = (255, 255, 255)
    return img.convert("L")

def preparer_image_larve(img):
    img = img.resize((img.width * 3, img.height * 3), Image.LANCZOS)
    img = img.convert("RGB")
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y]
            if r <= 10 and g >= 245 and b <= 10:
                pixels[x, y] = (0, 0, 0)
            else:
                pixels[x, y] = (255, 255, 255)
    return img.convert("L")

# ─── OCR ──────────────────────────────────────────────────────────────────────
def extraire_nombre(img):
    texte = pytesseract.image_to_string(img, config="--psm 7").strip()
    match = re.search(r'([\d,\.]+)\s*([TBMKtbmk]?)', texte)
    if not match:
        return None, texte
    nombre_str, suffixe = match.groups()
    nombre_str = nombre_str.replace(',', '')
    try:
        nombre = float(nombre_str)
    except ValueError:
        return None, texte
    multiplicateurs = {'t': 1_000_000_000_000, 'b': 1_000_000_000, 'm': 1_000_000, 'k': 1_000}
    if suffixe:
        nombre *= multiplicateurs.get(suffixe.lower(), 1)
    return nombre, texte

def nb_stuff():
    img = prendre_screenshot_inventaire()
    texte = pytesseract.image_to_string(img, config="--psm 7")
    match = re.search(r"(\d+)/(\d+)", texte)
    if match:
        return int(match.group(1)), int(match.group(2))
    print("Aucun match trouvé")
    return None, None

# ─── UTILITAIRES ──────────────────────────────────────────────────────────────
def get_pixel_color(x, y):
    try:
        return pyautogui.pixel(x, y)
    except Exception:
        return (0, 0, 0)

def index_to_pos(index):
    index = index % 30
    x = index % 10
    y = index // 10
    return -1172 + x * 105, 1017 + y * 110

def changer_page(index):
    return index > 0 and index % 30 == 0

def afficher_temps_avant_action(lait, vers, wack, inventaire, ferme):
    print(f"⏳ Temps avant prochaine action:")
    print(f"   🥛 Lait:       {max(0, int(TIMELAIT       - (time.time() - lait)))}s")
    print(f"   🐛 Vers:       {max(0, int(TIMEVERS       - (time.time() - vers)))}s")
    print(f"   ⚔️  Wack:       {max(0, int(TIMEWACK       - (time.time() - wack)))}s")
    print(f"   📦 Inventaire: {max(0, int(TIMEINVENTAIRE - (time.time() - inventaire)))}s")
    print(f"   🏠 Ferme:       {max(0, int(TIMEFERME       - (time.time() - ferme)))}s")
# ─── ACTIONS ──────────────────────────────────────────────────────────────────
def cube_zone_check():
    x1, y1 = cubeZoneStuff[0]
    x2, y2 = cubeZoneStuff[1]
    for x in range(x1, x2):
        for y in range(y1, y2):
            color = get_pixel_color(x, y)
            if color == couleurBonSuff:
                print("Good")
                return True
            elif color == couleurMauvaisSuff:
                print("Bad")
                return False
    return False

def verifier_wack():
    color = get_pixel_color(positionWack[0], positionWack[1])
    if color == couleurWack:
        return True
    else:
        return False

def faire_wack():
    for pos in listWack:
        pyautogui.click(pos[0], pos[1])
        time.sleep(0.1)

def faire_inventaire():
    pyautogui.click(positionStuff[0], positionStuff[1])
    time.sleep(0.1)
    pyautogui.scroll(100)
    time.sleep(0.1)
    nbstuff, maxstuff = nb_stuff()
    if nbstuff is not None:
        print(f"📦 Stuff: {nbstuff}/{maxstuff}")
        for i in range(nbstuff):
            if not automation_running:
                break
            if changer_page(i):
                pyautogui.scroll(-1)
                time.sleep(0.1)
            pos = index_to_pos(i)
            pyautogui.click(pos[0], pos[1])
            time.sleep(0.1)
            if cube_zone_check():
                pyautogui.click(pos[0], pos[1])
    for pos in listeDeleteStuff:
        pyautogui.click(pos[0], pos[1])
        time.sleep(0.1)

def faire_vers():
    pyautogui.click(positionVers[0], positionVers[1])
    time.sleep(0.1)
    nbvers, texte_brut = extraire_nombre(prendre_screenshot_vers())
    print(f"Texte brut vers : {texte_brut} → {nbvers}")
    if nbvers is None:
        pyautogui.click(positionVers[0], positionVers[1])
        return
    pyautogui.click(positionEcrireVers[0], positionEcrireVers[1])
    pyautogui.typewrite(str(int(nbvers / 12)))
    pyautogui.press('enter')
    for i in range(3):
        pyautogui.click(positionChangerPageVers[i][0], positionChangerPageVers[i][1])
        time.sleep(0.1)
        for j in range(4):
            pyautogui.click(positionPlusVers[j][0], positionPlusVers[j][1])
            time.sleep(0.1)
    pyautogui.click(positionVers[0], positionVers[1])

def faire_larve():
    pyautogui.click(positionVers[0], positionVers[1])
    time.sleep(0.1)
    img = preparer_image_larve(prendre_screenshot_larve())
    img.save("debug_larve.png")
    nbvers, texte_brut = extraire_nombre(img)
    print(f"Texte brut larve : {texte_brut} → {nbvers}")
    if nbvers is None:
        pyautogui.click(positionVers[0], positionVers[1])
        return
    pyautogui.click(positionEcrireVers[0], positionEcrireVers[1])
    pyautogui.typewrite(str(int(nbvers / 12)))
    pyautogui.press('enter')
    for i in range(3):
        pyautogui.click(positionChangerPageVers[i][0], positionChangerPageVers[i][1])
        time.sleep(0.1)
        for j in range(4):
            pyautogui.click(positionPlusLarve[j][0], positionPlusLarve[j][1])
            time.sleep(0.1)
    pyautogui.click(positionVers[0], positionVers[1])
    
    
def faire_lait():
    pyautogui.click(postionLait[0], postionLait[1])
    pyautogui.click(positionPageLait[0][0], positionPageLait[0][1])
    time.sleep(0.1)
    nblait, texte_brut = extraire_nombre(preparer_image_lait(prendre_screenshot_lait()))
    print(f"Texte brut lait : {texte_brut} → {nblait}")
    if nblait is None:
        return
    pyautogui.click(positionEcrireLait[0], positionEcrireLait[1])
    pyautogui.typewrite(str(int(nblait / 6)))
    pyautogui.press('enter')
    for i in range(2):
        for j in range(4):
            pyautogui.click(positionPlusLait[j][0], positionPlusLait[j][1])
            time.sleep(0.1)
        if i + 1 < len(positionPageLait):
            pyautogui.click(positionPageLait[i + 1][0], positionPageLait[i + 1][1])
    pyautogui.click(postionLait[0], postionLait[1])

def faire_ferme():
    for i in range(3):
        pyautogui.click(listeFerme[i][0], listeFerme[i][1])
    for i in range(3):
        pyautogui.click(listeFerme[i+3][0], listeFerme[i+3][1])
        for j in range(7):
            pyautogui.click(positionAchatFerme[0], positionAchatFerme[1])
    pyautogui.click(listeFerme[0][0], listeFerme[0][1])

    
def spam():
    global clic_humain
    clic_humain = False  # désactive les prints

    start = time.time()
    while time.time() - start < 2 and automation_running:
        pyautogui.click(positionSpam[0], positionSpam[1])
        time.sleep(0.01)

# ─── BOUCLE PRINCIPALE ────────────────────────────────────────────────────────
def automation_loop2():
    global automation_running
    global timeInventaire, timeWack, timeVers, timeLait , timeFerme # ← utilise les globaux
    clic_humain = False  # toute l'automatisation est silencieuse
    cycle        = 0

    while automation_running:
        cycle += 1
        print(f"\n🔄 Cycle {cycle}")
        print("=" * 40)
        spam()
        # if time.time() - timeWack > TIMEWACK:
        #     faire_wack()
        #     timeWack = time.time()
        if(time.time() - timeFerme > TIMEFERME):
            faire_ferme()
            timeFerme = time.time()
            
        if verifier_wack():
            faire_wack()
            timeWack = time.time()
            
        if time.time() - timeInventaire > TIMEINVENTAIRE:
            faire_inventaire()
            timeInventaire = time.time()

        if time.time() - timeVers > TIMEVERS:
            faire_vers()
            faire_larve()
            timeVers = time.time()

        if time.time() - timeLait > TIMELAIT:
            faire_lait()
            timeLait = time.time()

        
        clic_humain = True  # réactive les prints
        afficher_temps_avant_action(timeLait, timeVers, timeWack, timeInventaire , timeFerme)

# ─── CONTRÔLES ────────────────────────────────────────────────────────────────
def stop_program(signum=None, frame=None):
    global listener, keyboard_listener, automation_running
    automation_running = False
    if listener:
        listener.stop()
    if keyboard_listener:
        keyboard_listener.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, stop_program)

def on_click(x, y, button, pressed):
    if pressed and button == mouse.Button.right:
        stop_program()
        return
    if not clic_humain:
        return
    # if pressed and button == mouse.Button.left:
        # print(f"Position: ({x}, {y}) | RGB: {get_pixel_color(x, y)}")

def on_key_press(key):
    global automation_running, automation_thread
    try:
        if key == keyboard.Key.esc:
            stop_program()
        elif key == keyboard.Key.space:
            if automation_running:
                print("\n⏸️  Arrêt de l'automatisation...")
                automation_running = False
                if automation_thread:
                    automation_thread.join()
            else:
                print("\n▶️  Automatisation démarrée!")
                automation_running = True
                automation_thread = threading.Thread(target=automation_loop2, daemon=True)
                automation_thread.start()
    except AttributeError:
        pass

# ─── DÉMARRAGE ────────────────────────────────────────────────────────────────
listener = mouse.Listener(on_click=on_click)
listener.start()

keyboard_listener = keyboard.Listener(on_press=on_key_press)
keyboard_listener.start()

print("🎯 Programme lancé!")
print("🖱️  Clic gauche = Position + RGB")
print("🖱️  Clic droit  = Arrêter")
print("⌨️  SPACE = Démarrer/Arrêter l'automatisation")
print("⌨️  ESC   = Arrêter")

try:
    listener.join()
except KeyboardInterrupt:
    stop_program()