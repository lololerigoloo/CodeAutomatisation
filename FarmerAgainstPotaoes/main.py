from pynput import mouse, keyboard
import pyautogui
import signal
import sys
import time
import threading  # Ajoutez cette import
import mss
from PIL import Image
import pytesseract
import re

listener = None
keyboard_listener = None
automation_running = False
automation_thread = None  # Nouveau: thread pour l'automatisation
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

couleurWack = (231, 231, 33)
positionWack = (-508, 405)
listWack = [(-508, 405), (-930, 1343),(-1615, 1349)]
couleurStuff= (131, 57, 26)
positionStuff = (-1616, 1336)
listeDeleteStuff = [(-102, 1186),(-1107, 956),(-1837, 1351)]
cubeZoneStuff = [(-722, 488) , (-715, 498)]
couleurBonSuff = (0, 255, 0)
couleurMauvaisSuff = (255, 0, 0)
positionSpam = (-1506, 870)
positionVers =  (-1154, 1346)
positionPlusVers = [(-706, 519), (-708, 701), (-711, 885), (-710, 1067)]
positionChangerPageVers = [(-1153, 1241), (-1022, 1246), (-898, 1249)]
positionEcrireVers =  (-332, 1218)
postionLait = (-765, 1358) 
positionEcrireLait = (-332, 1107) 
positionPlusLait = [(-1851, 564), (-1855, 708), (-1846, 867), (-1845, 1026)]
positionPageLait = [(-1587, 1251), (-1461, 1249)]



TIMELAIT = 9000 # 15 minutes
TIMEVERS = 3000 # 15 minutes
TIMEINVENTAIRE = 6000 # 10 minutes
TIMEWACK = 3000 # 5 minutes


def prendre_screenshot_inventaire():
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
    "top": 383,
    "width": 144,   # -998 - (-1142)
    "height": 38    # 421 - 383
    }

        screenshot = sct.grab(region)

        img = Image.frombytes(
            "RGB",
            screenshot.size,
            screenshot.rgb
        )

        return img
    
def extraire_nombre(img):
    texte = pytesseract.image_to_string(img, config="--psm 7")
    texte = texte.strip()
    
    # Cherche un nombre avec suffixe B, M, K (ex: 4.49B, 505M, 2.3K)
    match = re.search(r'([\d,\.]+)\s*([TBMKtbmk]?)', texte)
    
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
        't': 1_000_000_000_000,
        'b': 1_000_000_000,
        'm': 1_000_000,
        'k': 1_000,
    }
    
    if suffixe:
        nombre *= multiplicateurs.get(suffixe.lower(), 1)
    
    return nombre, texte

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

def nb_stuff():
    img = prendre_screenshot_inventaire()
    texte = pytesseract.image_to_string(img, config="--psm 7")

    match = re.search(r"(\d+)/(\d+)", texte)

    if match:
        return int(match.group(1)), int(match.group(2))
    else:        
        print("Aucun match trouvé")
        return None, None

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
def stop_program(signum=None, frame=None):
    """Arrête proprement le programme"""
    global listener, keyboard_listener, automation_running
    automation_running = False
    if listener:
        listener.stop()
    if keyboard_listener:
        keyboard_listener.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, stop_program)

def cube_zone_check():
    """Vérifie si la couleur dans la zone du cube est correcte"""
    x1, y1 = cubeZoneStuff[0]
    x2, y2 = cubeZoneStuff[1]
    total_pixels = (x2 - x1) * (y2 - y1)
    correct_pixels = 0
    for x in range(x1, x2):
        for y in range(y1, y2):
            color = get_pixel_color(x, y)
            if color == couleurBonSuff:
                print( "trouver en total : ", correct_pixels, "/", total_pixels)
                return True
            elif color == couleurMauvaisSuff:
                print( "trouver en total : ", correct_pixels, "/", total_pixels)
                
                return False
            else:
                correct_pixels += 1
    return False

def liste_stuff_check():
    """Vérifie les couleurs aux positions de stuff"""
    pyautogui.click(positionStuff[0], positionStuff[1])
    time.sleep(0.1)
    for pos in listeStuff:
        if not automation_running:
            break
        click_x, click_y = pos
        pyautogui.click(click_x, click_y)
        time.sleep(0.1)
        if(cube_zone_check()):
            pyautogui.click(click_x, click_y)
        else:
            time.sleep(0.1)
        
def supprimer_stuff():
    """Supprime les stuffs aux positions de suppression"""
    for pos in listeDeleteStuff:
        if not automation_running:
            break
        click_x, click_y = pos
        pyautogui.click(click_x, click_y)
        time.sleep(0.1)
        
def verifier_wack():
    color = get_pixel_color(positionWack[0], positionWack[1])
    if color == couleurWack:
        return True
    else:
        return False
        
def faire_wack():
    for pos in listWack:
        click_x, click_y = pos
        pyautogui.click(click_x, click_y)
        time.sleep(0.1)
        
def verifier_stuff():
    for _ in range(20):
        color = get_pixel_color(positionStuff[0], positionStuff[1])
        if color[0] <= couleurStuff[0]+20:
            print(f"✅ Stuff est correct!")
            return True
        else:
            time.sleep(0.05)
    return False

def get_pixel_color(x, y):
    """Récupère la couleur RGB à la position (x, y)"""
    try:
        pixel = pyautogui.pixel(x, y)
        return pixel
    except Exception as e:
        return (0, 0, 0)
    
def changer_page(index):
    return index % 30 == 0


def faire_inventaire():
    pyautogui.click(positionStuff[0], positionStuff[1])
    pyautogui.scroll(100)  # Scroll up pour être sûr de partir du début
    nbstuff, maxstuff = nb_stuff()
    if nbstuff is not None and maxstuff is not None:
        print(f"📦 Stuff: {nbstuff}/{maxstuff}")
        for i in range(nbstuff):
            if changer_page(i):
                pyautogui.scroll(-1)  # Scroll down pour changer de page
            pos = index_to_pos(i)
            pyautogui.click(pos[0], pos[1])
            time.sleep(0.1)
            if(cube_zone_check()):
                pyautogui.click(pos[0], pos[1])
    supprimer_stuff()

def faire_vers():
    pyautogui.click(positionVers[0], positionVers[1])
    nbvers, texte_brut = extraire_nombre(prendre_screenshot_vers())
    print(f"Texte brut : {texte_brut}")
    print(f"Nombre de vers : {nbvers}")
    nbvers = int(nbvers) /12
    pyautogui.click(positionEcrireVers[0], positionEcrireVers[1])
    pyautogui.typewrite(str(int(nbvers)))
    pyautogui.press('enter')
    pyautogui.click(positionChangerPageVers[0][0], positionChangerPageVers[0][1])
    for i in range(3):
        pyautogui.click(positionChangerPageVers[i][0], positionChangerPageVers[i][1])
        time.sleep(0.1)
        for j in range(4): 
            pyautogui.click(positionPlusVers[j][0], positionPlusVers[j][1])
            time.sleep(0.1)
    pyautogui.click(positionVers[0], positionVers[1])
    
def faire_lait():
    pyautogui.click(postionLait[0], postionLait[1])
    pyautogui.click(positionPageLait[0][0], positionPageLait[0][1])
    nblait, texte_brut = extraire_nombre(preparer_image(prendre_screenshot_lait()))
    print(f"Texte brut : {texte_brut}")
    print(f"Nombre de lait : {nblait}")
    nblait = int(nblait) /6
    pyautogui.click(positionEcrireLait[0], positionEcrireLait[1])
    pyautogui.typewrite(str(int(nblait)))
    pyautogui.press('enter')
    for i in range(2):
        for j in range(4):
            pyautogui.click(positionPlusLait[j][0], positionPlusLait[j][1])
            time.sleep(0.1)
        pyautogui.click(positionPageLait[i+1][0], positionPageLait[i+1][1])
    pyautogui.click(postionLait[0], postionLait[1])
        
        
    
def spam():
    start_time = time.time()
    while time.time() - start_time < 2 and automation_running:  # Vérifiez automation_running
        pyautogui.click(positionSpam[0], positionSpam[1])
        time.sleep(0.01)
        
def afficher_temps_avant_action(lait, vers, wack, inventaire):
    print(f"⏳ Temps avant prochaine action:")
    print(f"🥛 Lait: {max(0, int(TIMELAIT - (time.time() - lait)))}s")
    print(f"🐛 Vers: {max(0, int(TIMEVERS - (time.time() - vers)))}s")
    print(f"⚔️  Wack: {max(0, int(TIMEWACK - (time.time() - wack)))}s")
    print(f"📦 Inventaire: {max(0, int(TIMEINVENTAIRE - (time.time() - inventaire)))}s")
# def automation_loop():
#     """Boucle d'automatisation principale"""
#     global automation_running
#     cycle = 0
    
#     while automation_running:
#         cycle += 1
#         print(f"\n🔄 Cycle {cycle}")
#         print("="*40)
        
#         if verifier_wack():
#             faire_wack()
#         elif verifier_stuff():
#             liste_stuff_check()
#             supprimer_stuff()
#         else:
#             start_time = time.time()
#             while time.time() - start_time < 2 and automation_running:  # Vérifiez automation_running
#                 pyautogui.click(positionSpam[0], positionSpam[1])
#                 time.sleep(0.01)

def automation_loop2():
    """Boucle d'automatisation secondaire"""
    global automation_running
    cycle = 0
    timeInventaire = time.time()
    timeWack = time.time()
    timeVers= time.time()
    timeLait= time.time()
    while automation_running:
        cycle += 1
        print(f"\n🔄 Cycle {cycle}")
        print("="*40)
    if(time.time() - timeWack > TIMEWACK):
        faire_wack()
    if(time.time() - timeInventaire > TIMEINVENTAIRE):
       faire_inventaire()
       timeInventaire = time.time()
    if(time.time() - timeVers > TIMEVERS):
        faire_vers()
        timeVers = time.time()
    if(time.time() - timeLait > TIMELAIT):
        faire_lait()
        timeLait = time.time()
    spam()
    afficher_temps_avant_action(timeLait, timeVers, timeWack, timeInventaire)
    

def on_click(x, y, button, pressed):
    if pressed and button == mouse.Button.left:
        rgb = get_pixel_color(x, y)
        # with open('coordoner.txt', 'a') as f:
        #     f.write(f'({x}, {y}),')
        print(f'Position: ({x}, {y}) | RGB: {rgb}')
    
    if pressed and button == mouse.Button.right:
        stop_program()

def on_key_press(key):
    """Contrôler l'automatisation au clavier"""
    global automation_running, automation_thread
    try:
        if key == keyboard.Key.esc:
            stop_program()
        elif key == keyboard.Key.space:
            if automation_running:
                print("\n⏸️  Arrêt de l'automatisation...")
                automation_running = False
                if automation_thread:
                    automation_thread.join()  # Attendre que le thread se termine
            else:
                print("\n▶️  Automatisation démarrée!")
                automation_running = True
                automation_thread = threading.Thread(target=automation_loop2, daemon=True)
                automation_thread.start()
    except AttributeError:
        pass

listener = mouse.Listener(on_click=on_click)
listener.start()

keyboard_listener = keyboard.Listener(on_press=on_key_press)
keyboard_listener.start()

print("🎯 Programme lancé!")
print("🖱️  Clic gauche = Enregistrer position + RGB")
print("🖱️  Clic droit = Arrêter complètement")
print("⌨️  SPACE = Démarrer/Arrêter l'automatisation")
print("⌨️  ESC = Arrêter")
print("⌨️  Ctrl+C = Arrêter")

try:
    listener.join()
except KeyboardInterrupt:
    stop_program()