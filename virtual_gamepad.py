"""
virtual_gamepad.py - Gestor de gamepad virtual per a Windows

Aquest mòdul utilitza vgamepad per crear un controlador virtual XInput
que Ryujinx pot detectar com un comandament de Nintendo Switch Pro.
"""

import sys
from typing import Optional, Tuple, Dict, Any

# Intenta importar vgamepad (només disponible a Windows)
try:
    import vgamepad as vg
    VGAMEPAD_AVAILABLE = True
except ImportError:
    VGAMEPAD_AVAILABLE = False
    vg = None  # Defineix vg com a None per evitar errors
    print("AVÍS: vgamepad no està disponible. Només funciona a Windows.")
    print("Instal·la'l amb: pip install vgamepad")


def _get_buttons_map() -> Dict[str, Any]:
    """Retorna el mapeig de botons segons disponibilitat de vgamepad."""
    if VGAMEPAD_AVAILABLE and vg:
        # Compatibilitat amb diferents versions de vgamepad
        buttons_module = getattr(vg, 'XUSB_BUTTONS', None) or getattr(vg, 'XUSB_BUTTON', None)
        
        if not buttons_module:
            print("ERROR: No s'han trobat les constants de botons a vgamepad.")
            return {}
            
        return {
            'BUTTON_A': buttons_module.XUSB_GAMEPAD_A,
            'BUTTON_B': buttons_module.XUSB_GAMEPAD_B,
            'BUTTON_X': buttons_module.XUSB_GAMEPAD_X,
            'BUTTON_Y': buttons_module.XUSB_GAMEPAD_Y,
            'BUTTON_L': buttons_module.XUSB_GAMEPAD_LEFT_SHOULDER,
            'BUTTON_R': buttons_module.XUSB_GAMEPAD_RIGHT_SHOULDER,
            'BUTTON_ZL': None,  # Els triggers són analògics
            'BUTTON_ZR': None,
            'BUTTON_PLUS': buttons_module.XUSB_GAMEPAD_START,
            'BUTTON_MINUS': buttons_module.XUSB_GAMEPAD_BACK,
            'BUTTON_HOME': buttons_module.XUSB_GAMEPAD_GUIDE,
            'BUTTON_CAPTURE': None,  # No existeix a XInput, es pot mapejar a BACK
            'DPAD_UP': buttons_module.XUSB_GAMEPAD_DPAD_UP,
            'DPAD_DOWN': buttons_module.XUSB_GAMEPAD_DPAD_DOWN,
            'DPAD_LEFT': buttons_module.XUSB_GAMEPAD_DPAD_LEFT,
            'DPAD_RIGHT': buttons_module.XUSB_GAMEPAD_DPAD_RIGHT,
        }
    return {}


class VirtualGamepad:
    """Gestiona un gamepad virtual XInput per a Windows."""
    
    # Constants de botons XInput
    BUTTONS_MAP: Dict[str, Any] = _get_buttons_map()
    
    def __init__(self):
        """Inicialitza el gamepad virtual."""
        if not VGAMEPAD_AVAILABLE:
            raise RuntimeError("vgamepad no està disponible. Aquest mòdul només funciona a Windows.")
        
        self.gamepad = vg.VX360Gamepad()
        self.pressed_buttons = set()
        self.left_stick_x = 0
        self.left_stick_y = 0
        self.right_stick_x = 0
        self.right_stick_y = 0
        self.left_trigger = 0
        self.right_trigger = 0
    
    def press_button(self, button_name: str) -> None:
        """
        Prem un botó del gamepad.
        
        Args:
            button_name: Nom del botó segons la configuració.
        """
        if button_name in self.pressed_buttons:
            return
        
        xinput_button = self.BUTTONS_MAP.get(button_name)
        
        if xinput_button:
            self.gamepad.press_button(button=xinput_button)
            self.pressed_buttons.add(button_name)
        elif button_name == 'BUTTON_ZL':
            self.left_trigger = 255
            self.gamepad.left_trigger(value=self.left_trigger)
        elif button_name == 'BUTTON_ZR':
            self.right_trigger = 255
            self.gamepad.right_trigger(value=self.right_trigger)
        elif button_name == 'BUTTON_CAPTURE':
            # Mapeja Capture a BACK com a alternativa
            # Utilitza la mateixa lògica per trobar la constant
            buttons_module = getattr(vg, 'XUSB_BUTTONS', None) or getattr(vg, 'XUSB_BUTTON', None)
            if buttons_module:
                self.gamepad.press_button(button=buttons_module.XUSB_GAMEPAD_BACK)
                self.pressed_buttons.add(button_name)
    
    def release_button(self, button_name: str) -> None:
        """
        Allibera un botó del gamepad.
        
        Args:
            button_name: Nom del botó segons la configuració.
        """
        if button_name not in self.pressed_buttons:
            return
        
        xinput_button = self.BUTTONS_MAP.get(button_name)
        
        if xinput_button:
            self.gamepad.release_button(button=xinput_button)
            self.pressed_buttons.discard(button_name)
        elif button_name == 'BUTTON_ZL':
            self.left_trigger = 0
            self.gamepad.left_trigger(value=self.left_trigger)
        elif button_name == 'BUTTON_ZR':
            self.right_trigger = 0
            self.gamepad.right_trigger(value=self.right_trigger)
        elif button_name == 'BUTTON_CAPTURE':
            # Mapeja Capture a BACK com a alternativa
            buttons_module = getattr(vg, 'XUSB_BUTTONS', None) or getattr(vg, 'XUSB_BUTTON', None)
            if buttons_module:
                self.gamepad.release_button(button=buttons_module.XUSB_GAMEPAD_BACK)
                self.pressed_buttons.discard(button_name)
    
    def set_left_stick(self, x: float, y: float) -> None:
        """
        Estableix la posició del stick esquerre.
        
        Args:
            x: Valor horitzontal (-1.0 a 1.0).
            y: Valor vertical (-1.0 a 1.0).
        """
        # Converteix de -1.0/1.0 a 0-65535 (rang XInput)
        x_int = int((x + 1) * 32767.5)
        y_int = int((y + 1) * 32767.5)
        
        # Clamp als valors vàlids
        x_int = max(0, min(65535, x_int))
        y_int = max(0, min(65535, y_int))
        
        self.left_stick_x = x
        self.left_stick_y = y
        self.gamepad.left_joystick(x_value=x_int, y_value=y_int)
    
    def set_right_stick(self, x: float, y: float) -> None:
        """
        Estableix la posició del stick dret (càmera).
        
        Args:
            x: Valor horitzontal (-1.0 a 1.0).
            y: Valor vertical (-1.0 a 1.0).
        """
        # Converteix de -1.0/1.0 a 0-65535 (rang XInput)
        x_int = int((x + 1) * 32767.5)
        y_int = int((-y + 1) * 32767.5)  # Inverteix Y per compatibilitat
        
        # Clamp als valors vàlids
        x_int = max(0, min(65535, x_int))
        y_int = max(0, min(65535, y_int))
        
        self.right_stick_x = x
        self.right_stick_y = y
        self.gamepad.right_joystick(x_value=x_int, y_value=y_int)
    
    def update(self) -> None:
        """Actualitza l'estat del gamepad virtual."""
        self.gamepad.update()
    
    def reset(self) -> None:
        """Reinicia tots els inputs del gamepad."""
        self.gamepad.reset()
        self.pressed_buttons.clear()
        self.left_stick_x = 0
        self.left_stick_y = 0
        self.right_stick_x = 0
        self.right_stick_y = 0
        self.left_trigger = 0
        self.right_trigger = 0
    
    def is_available(self) -> bool:
        """Indica si el gamepad virtual està disponible."""
        return VGAMEPAD_AVAILABLE


class DummyGamepad:
    """Gamepad dummy per a sistemes on vgamepad no està disponible."""
    
    def __init__(self):
        self.pressed_buttons = set()
        self.left_stick_x = 0
        self.left_stick_y = 0
        self.right_stick_x = 0
        self.right_stick_y = 0
    
    def press_button(self, button_name: str) -> None:
        self.pressed_buttons.add(button_name)
        print(f"[Dummy] Botó premut: {button_name}")
    
    def release_button(self, button_name: str) -> None:
        self.pressed_buttons.discard(button_name)
        print(f"[Dummy] Botó alliberat: {button_name}")
    
    def set_left_stick(self, x: float, y: float) -> None:
        self.left_stick_x = x
        self.left_stick_y = y
        print(f"[Dummy] Stick esquerre: ({x:.2f}, {y:.2f})")
    
    def set_right_stick(self, x: float, y: float) -> None:
        self.right_stick_x = x
        self.right_stick_y = y
        print(f"[Dummy] Stick dret: ({x:.2f}, {y:.2f})")
    
    def update(self) -> None:
        pass
    
    def reset(self) -> None:
        self.pressed_buttons.clear()
        self.left_stick_x = 0
        self.left_stick_y = 0
        self.right_stick_x = 0
        self.right_stick_y = 0
    
    def is_available(self) -> bool:
        return False


def create_gamepad() -> Optional['VirtualGamepad | DummyGamepad']:
    """
    Crea una instància de gamepad virtual.
    
    Returns:
        Instància de VirtualGamepad o DummyGamepad segons disponibilitat.
    """
    if VGAMEPAD_AVAILABLE:
        try:
            return VirtualGamepad()
        except Exception as e:
            print(f"Error creant el gamepad virtual: {e}")
            return DummyGamepad()
    else:
        return DummyGamepad()
