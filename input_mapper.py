import vgamepad as vg
from pynput import keyboard, mouse
import yaml
import math
import time
import sys

class InputMapper:
    def __init__(self, config_path='config.yaml'):
        self.config = self.load_config(config_path)
        self.gamepad = vg.VDS4Gamepad()  # Emula un DualShock 4, compatible amb Ryujinx
        
        # Estat actual dels inputs
        self.keys_pressed = set()
        self.mouse_x = 0.0
        self.mouse_y = 0.0
        self.camera_active = self.config['mouse_control']['always_active']
        
        # Variables per al moviment acumulat del ratolí
        self.last_mouse_time = time.time()
        self.last_mx = None
        self.last_my = None
        
        # Carregar mapes de tecles
        self.key_map = self.config['buttons']
        self.reverse_key_map = {v: k for k, v in self.key_map.items() if not k.startswith('stick') and not k.startswith('dpad')}
        
        # Inicialitzar listeners
        self.k_listener = None
        self.m_listener = None
        self.setup_listeners()

    def load_config(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Error: No s'ha trobat {path}. Creant un per defecte...")
            # Aquí podries generar un config per defecte si volguessis
            sys.exit(1)

    def setup_listeners(self):
        # Listener de teclat
        self.k_listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        # Listener de ratolí
        self.m_listener = mouse.Listener(
            on_move=self.on_mouse_move,
            on_click=self.on_click
        )
        
        self.k_listener.start()
        self.m_listener.start()

    def normalize_key(self, key):
        """Converteix objectes Key de pynput a strings comparables."""
        if isinstance(key, keyboard.KeyCode):
            if key.char:
                return key.char.lower()
            # Tecles especials sense caràcter (ex: shift)
            return str(key).replace('Key.', '')
        elif isinstance(key, keyboard.Key):
            return str(key).replace('Key.', '')
        return str(key).lower()

    def on_press(self, key):
        k_str = self.normalize_key(key)
        self.keys_pressed.add(k_str)
        
        # Lògica de toggles si calgués (ex: prémer 'M' per activar càmera)
        # Implementable mirant self.config

    def on_release(self, key):
        k_str = self.normalize_key(key)
        if k_str in self.keys_pressed:
            self.keys_pressed.remove(k_str)

    def on_mouse_move(self, x, y):
        if not self.camera_active:
            return

        # Inicialitzar la última posició si és el primer moviment
        if self.last_mx is None or self.last_my is None:
            self.last_mx = x
            self.last_my = y
            return

        dx = x - self.last_mx
        dy = y - self.last_my
        
        self.last_mx = x
        self.last_my = y
        self.last_mouse_time = time.time()  # Actualitzar el temps de l'últim moviment

        # Aplicar sensibilitat i inversió
        sens_x = self.config['camera']['sensitivity_x']
        sens_y = self.config['camera']['sensitivity_y']
        invert_y = -1 if self.config['camera']['invert_y'] else 1

        # Normalitzar valors (això és una aproximació, cal ajustar segons la resolució)
        # Un valor de 3000 píxels/segons sol ser ràpid.
        raw_x = dx * sens_x * 0.005 
        raw_y = dy * sens_y * 0.005 * invert_y

        # Deadzone
        deadzone = self.config['camera']['deadzone']
        if abs(raw_x) < deadzone: raw_x = 0
        if abs(raw_y) < deadzone: raw_y = 0

        # Clamp (limitar a -1.0 / 1.0)
        max_speed = self.config['camera']['max_speed']
        self.mouse_x = max(-max_speed, min(max_speed, raw_x))
        self.mouse_y = max(-max_speed, min(max_speed, raw_y))

    def on_click(self, x, y, button, pressed):
        # Gestió de botons del ratolí si es volguessin mapejar
        pass

    def get_analog_stick(self, up_k, down_k, left_k, right_k):
        """Calcula vector X,Y per a un stick basat en tecles premudes."""
        x = 0.0
        y = 0.0
        
        if up_k in self.keys_pressed: y += 1.0
        if down_k in self.keys_pressed: y -= 1.0
        if left_k in self.keys_pressed: x -= 1.0
        if right_k in self.keys_pressed: x += 1.0

        # Normalitzar diagonal (evitar que surti del cercle unitari)
        if x != 0 or y != 0:
            length = math.sqrt(x**2 + y**2)
            if length > 1.0:
                x /= length
                y /= length
        
        return x, y

    def update_gamepad(self):
        """Llegeix estat actual i actualitza el gamepad virtual."""
        cfg = self.config
        keys = self.keys_pressed
        
        # 1. Botons Digitals
        # Mapeig directe
        btn_map = {
            vg.DS4_BUTTONS.DS4_BUTTON_CROSS: cfg['buttons'].get('A'),
            vg.DS4_BUTTONS.DS4_BUTTON_CIRCLE: cfg['buttons'].get('B'),
            vg.DS4_BUTTONS.DS4_BUTTON_SQUARE: cfg['buttons'].get('X'),
            vg.DS4_BUTTONS.DS4_BUTTON_TRIANGLE: cfg['buttons'].get('Y'),
            vg.DS4_BUTTONS.DS4_BUTTON_SHARE: cfg['buttons'].get('MINUS'),
            vg.DS4_BUTTONS.DS4_BUTTON_OPTIONS: cfg['buttons'].get('PLUS'),
            vg.DS4_BUTTONS.DS4_BUTTON_L1: cfg['buttons'].get('L'),
            vg.DS4_BUTTONS.DS4_BUTTON_R1: cfg['buttons'].get('R'),
        }
        
        # Reset botons
        self.gamepad.reset()

        for btn, key_name in btn_map.items():
            if key_name and self.normalize_key_text(key_name) in keys:
                self.gamepad.press_button(btn)

        # D-Pad (HAT Switch)
        dpad_val = vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE
        dpad_up_key = self.normalize_key_text(cfg['buttons'].get('dpad_up'))
        dpad_down_key = self.normalize_key_text(cfg['buttons'].get('dpad_down'))
        dpad_left_key = self.normalize_key_text(cfg['buttons'].get('dpad_left'))
        dpad_right_key = self.normalize_key_text(cfg['buttons'].get('dpad_right'))
        
        if dpad_up_key in keys:
            if dpad_left_key in keys: 
                dpad_val = vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTHWEST
            elif dpad_right_key in keys: 
                dpad_val = vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTHEAST
            else: 
                dpad_val = vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NORTH
        elif dpad_down_key in keys:
            if dpad_left_key in keys: 
                dpad_val = vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTHWEST
            elif dpad_right_key in keys: 
                dpad_val = vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTHEAST
            else: 
                dpad_val = vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_SOUTH
        elif dpad_left_key in keys:
            dpad_val = vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_WEST
        elif dpad_right_key in keys:
            dpad_val = vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_EAST
            
        self.gamepad.directional_pad(dpad_val)

        # Triggers (Analògics 0-255)
        zl_key = self.normalize_key_text(cfg['buttons'].get('ZL'))
        zr_key = self.normalize_key_text(cfg['buttons'].get('ZR'))
        
        z_val = 255 if zl_key in keys else 0
        self.gamepad.left_trigger(z_val)
        
        zr_val = 255 if zr_key in keys else 0
        self.gamepad.right_trigger(zr_val)

        # 2. Stick Esquerre (Moviment)
        sl_up = self.normalize_key_text(cfg['buttons'].get('stick_left_up'))
        sl_down = self.normalize_key_text(cfg['buttons'].get('stick_left_down'))
        sl_left = self.normalize_key_text(cfg['buttons'].get('stick_left_left'))
        sl_right = self.normalize_key_text(cfg['buttons'].get('stick_left_right'))
        
        lx, ly = self.get_analog_stick(sl_up, sl_down, sl_left, sl_right)
        self.gamepad.left_joystick(lx, ly)

        # 3. Stick Dret (Càmera - Ratolí)
        # Aplicar suavitzat per evitar salts bruscos
        smoothing = 0.3  # Factor de suavitzat (0.0 a 1.0)
        smoothed_x = self.mouse_x * smoothing + (1 - smoothing) * (getattr(self, '_prev_mouse_x', 0))
        smoothed_y = self.mouse_y * smoothing + (1 - smoothing) * (getattr(self, '_prev_mouse_y', 0))
        self._prev_mouse_x = smoothed_x
        self._prev_mouse_y = smoothed_y
        
        self.gamepad.right_joystick(smoothed_x, smoothed_y)
        
        # Netejar buffer de ratolí si no hi ha moviment recent (evitar drift)
        current_time = time.time()
        if current_time - self.last_mouse_time > 0.1: # Si fa més de 100ms que no es mou
             self.mouse_x = 0.0
             self.mouse_y = 0.0
             self._prev_mouse_x = 0.0
             self._prev_mouse_y = 0.0
             # Actualitzem el gamepad immediatament per centrar-lo
             self.gamepad.right_joystick(0.0, 0.0)

        # Enviar estat al driver
        self.gamepad.update()

    def normalize_key_text(self, text):
        """Auxiliar per comparar strings del YAML amb els sets de tecles."""
        if text is None: return ""
        t = text.lower().strip()
        if t.startswith('key.'): t = t[4:]
        return t

    def run(self):
        """Bucle principal d'execució."""
        print("Iniciant pont Ratolí/Teclat -> Ryujinx...")
        print("Assegura't que Ryujinx tingui configurat el 'Player 1' com a controlador USB/DualShock 4.")
        
        # Verificar que els listeners s'han iniciat correctament
        if not self.k_listener or not self.m_listener:
            print("Error: Els listeners no s'han inicialitzat correctament.")
            return
            
        try:
            while True:
                self.update_gamepad()
                time.sleep(0.005) # 200Hz update rate, suficient per a jocs
        except KeyboardInterrupt:
            print("\nAturant sistema...")
            self.gamepad.reset()
            self.gamepad.update()
            self.k_listener.stop()
            self.m_listener.stop()
            self.k_listener.join()
            self.m_listener.join()