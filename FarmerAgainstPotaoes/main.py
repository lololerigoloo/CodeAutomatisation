from pynput import mouse, keyboard
import pyautogui
import signal
import sys
import time
import threading  # Ajoutez cette import

listener = None
keyboard_listener = None
automation_running = False
automation_thread = None  # Nouveau: thread pour l'automatisation

couleurWack = (231, 231, 33)
positionWack = (-508, 405)
listWack = [(-508, 405), (-930, 1343),(-1615, 1349)]
couleurStuff= (131, 57, 26)
positionStuff = (-1616, 1336)
listeStuff = [(-1177, 1015),(-1064, 1020),(-958, 1022),(-851, 1020),(-755, 1015),(-628, 1029),(-551, 1021),(-428, 1030),(-311, 1013),(-236, 1021),
              (-1186, 1126),(-1055, 1121),(-961, 1125),(-845, 1131),(-764, 1127),(-652, 1130),(-531, 1130),(-436, 1126),(-327, 1126),(-215, 1129),
              (-1165, 1242),(-1058, 1232),(-960, 1242),(-846, 1227),(-753, 1238),(-641, 1230),(-539, 1235),(-425, 1236),(-330, 1235),(-216, 1232)]
listeDeleteStuff = [(-102, 1186),(-1107, 956),(-1837, 1351)]
cubeZoneStuff = [(-725, 481) , (-710, 500)]
couleurBonSuff = (0, 255, 0)
couleurMauvaisSuff = (255, 0, 0)
positionSpam = (-1506, 870)

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

def automation_loop():
    """Boucle d'automatisation principale"""
    global automation_running
    cycle = 0
    
    while automation_running:
        cycle += 1
        print(f"\n🔄 Cycle {cycle}")
        print("="*40)
        
        if verifier_wack():
            faire_wack()
        elif verifier_stuff():
            liste_stuff_check()
            supprimer_stuff()
        else:
            start_time = time.time()
            while time.time() - start_time < 2 and automation_running:  # Vérifiez automation_running
                pyautogui.click(positionSpam[0], positionSpam[1])
                time.sleep(0.01)


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
                automation_thread = threading.Thread(target=automation_loop, daemon=True)
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