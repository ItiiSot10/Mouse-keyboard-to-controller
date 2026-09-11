"""
mk_controller.py - Controlador principal per a Ratolí i Teclat (M&K)

Aquest mòdul integra tots els components per crear un sistema complet
de control amb ratolí i teclat per a Ryujinx.
"""

import time
import math
from typing import Optional, Dict, Any
from config_manager import ConfigManager
from input_handler import InputHandler
from virtual_gamepad import create_gamepad, VirtualGamepad, DummyGamepad


class MKController:
    """Controlador principal que integra teclat, ratolí i gamepad virtual."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicialitza el controlador M&K.
        
        Args:
            config_path: Camí al fitxer de configuració YAML.
        """
        self.config_manager = ConfigManager(config_path)
        self.gamepad = create_gamepad()
        
        # Configuració
        self.keyboard_mapping = self.config_manager.get_keyboard_mapping()
        self.mouse_config = self.config_manager.get_mouse_camera_config()
        self.general_config = self.config_manager.get_general_config()
        
        # Estat del control de càmera
        self.camera_enabled = self.mouse_config.get('enabled', True)
        self.toggle_key = self.config_manager.get_toggle_key()
        self.camera_active = False  # Estat actual del toggle
        
        # Configuració del ratolí
        self.sensitivity_x = self.mouse_config.get('sensitivity_x', 0.5)
        self.sensitivity_y = self.mouse_config.get('sensitivity_y', 0.5)
        self.invert_y = self.mouse_config.get('invert_y', False)
        self.deadzone = self.mouse_config.get('deadzone', 0.1)
        self.max_speed = self.mouse_config.get('max_speed', 1.0)
        
        # Estat dels sticks
        self.left_stick_x = 0.0
        self.left_stick_y = 0.0
        self.right_stick_x = 0.0
        self.right_stick_y = 0.0
        
        # Tecles actuals premudes per al stick esquerre
        self.stick_left_keys = {
            'STICK_LEFT_UP': set(),
            'STICK_LEFT_DOWN': set(),
            'STICK_LEFT_LEFT': set(),
            'STICK_LEFT_RIGHT': set(),
        }
        
        # Inicialitza el gestor d'entrades
        self.input_handler = InputHandler(
            on_key_press=self._on_key_press,
            on_key_release=self._on_key_release,
            on_mouse_move=self._on_mouse_move
        )
        
        # Inversió de mapeig: de nom de botó a tecla
        self.reverse_mapping: Dict[str, str] = {}
        for key, button in self.keyboard_mapping.items():
            self.reverse_mapping[button] = key
        
        self.debug_mode = self.config_manager.is_debug_mode()
    
    def _on_key_press(self, key_name: str) -> None:
        """Callback quan es prem una tecla."""
        if self.debug_mode:
            print(f"[DEBUG] Tecla premuda: {key_name}")
        
        # Comprova si és la tecla de toggle de la càmera
        if key_name == self.toggle_key:
            self.camera_active = not self.camera_active
            if self.debug_mode:
                estat = "ACTIU" if self.camera_active else "INACTIU"
                print(f"[DEBUG] Control de càmera: {estat}")
            return
        
        # Comprova si la tecla està mapejada
        if key_name in self.keyboard_mapping:
            button_name = self.keyboard_mapping[key_name]
            
            # Gestiona els botons normals
            if button_name.startswith('BUTTON_') or button_name.startswith('DPAD_'):
                self.gamepad.press_button(button_name)
            
            # Gestiona les direccions del stick esquerre
            elif button_name.startswith('STICK_LEFT_'):
                self._update_left_stick_from_keys()
    
    def _on_key_release(self, key_name: str) -> None:
        """Callback quan s'allibera una tecla."""
        if self.debug_mode:
            print(f"[DEBUG] Tecla alliberada: {key_name}")
        
        # Comprova si és la tecla de toggle de la càmera
        if key_name == self.toggle_key:
            return  # El toggle ja s'ha gestionat en prémer
        
        # Comprova si la tecla està mapejada
        if key_name in self.keyboard_mapping:
            button_name = self.keyboard_mapping[key_name]
            
            # Gestiona els botons normals
            if button_name.startswith('BUTTON_') or button_name.startswith('DPAD_'):
                self.gamepad.release_button(button_name)
            
            # Gestiona les direccions del stick esquerre
            elif button_name.startswith('STICK_LEFT_'):
                self._update_left_stick_from_keys()
    
    def _on_mouse_move(self, dx: int, dy: int) -> None:
        """
        Callback quan es mou el ratolí.
        
        Args:
            dx: Moviment horitzontal.
            dy: Moviment vertical.
        """
        if not self.camera_active or not self.camera_enabled:
            return
        
        # Aplica sensibilitat
        move_x = dx * self.sensitivity_x * 0.01
        move_y = dy * self.sensitivity_y * 0.01
        
        # Inverteix Y si cal
        if self.invert_y:
            move_y = -move_y
        
        # Acumula el moviment
        self.right_stick_x += move_x
        self.right_stick_y += move_y
        
        # Aplica zona morta
        if abs(self.right_stick_x) < self.deadzone:
            self.right_stick_x = 0.0
        if abs(self.right_stick_y) < self.deadzone:
            self.right_stick_y = 0.0
        
        # Limita la velocitat màxima
        magnitude = math.sqrt(self.right_stick_x**2 + self.right_stick_y**2)
        if magnitude > self.max_speed:
            scale = self.max_speed / magnitude
            self.right_stick_x *= scale
            self.right_stick_y *= scale
        
        # Clamp a [-1, 1]
        self.right_stick_x = max(-1.0, min(1.0, self.right_stick_x))
        self.right_stick_y = max(-1.0, min(1.0, self.right_stick_y))
    
    def _update_left_stick_from_keys(self) -> None:
        """Actualitza la posició del stick esquerre basant-se en les tecles premudes."""
        x = 0.0
        y = 0.0
        
        # Direccions actives
        if self.input_handler.is_key_pressed('w'):
            y += 1.0
        if self.input_handler.is_key_pressed('s'):
            y -= 1.0
        if self.input_handler.is_key_pressed('a_key') or self.input_handler.is_key_pressed('a'):
            # Evita conflicte amb BUTTON_A
            if 'a_key' in self.keyboard_mapping or self.keyboard_mapping.get('a') == 'STICK_LEFT_LEFT':
                x -= 1.0
        if self.input_handler.is_key_pressed('d'):
            x += 1.0
        
        # Normalitza si hi ha moviment diagonal
        magnitude = math.sqrt(x**2 + y**2)
        if magnitude > 1.0:
            x /= magnitude
            y /= magnitude
        
        self.left_stick_x = x
        self.left_stick_y = y
    
    def update(self) -> None:
        """Actualitza l'estat del gamepad virtual."""
        # Actualitza sticks
        self.gamepad.set_left_stick(self.left_stick_x, self.left_stick_y)
        self.gamepad.set_right_stick(self.right_stick_x, self.right_stick_y)
        
        # Actualitza el gamepad
        self.gamepad.update()
        
        # Decau gradualment el stick dret cap a zero (simula tornar al centre)
        if self.right_stick_x != 0:
            decay = 0.1
            if abs(self.right_stick_x) < decay:
                self.right_stick_x = 0.0
            else:
                self.right_stick_x -= decay if self.right_stick_x > 0 else -decay
        
        if self.right_stick_y != 0:
            decay = 0.1
            if abs(self.right_stick_y) < decay:
                self.right_stick_y = 0.0
            else:
                self.right_stick_y -= decay if self.right_stick_y > 0 else -decay
    
    def start(self) -> None:
        """Inicia el controlador."""
        print("Iniciant controlador M&K per a Ryujinx...")
        print(f"Gamepad virtual disponible: {self.gamepad.is_available()}")
        print(f"Tecla de toggle per a càmera: {self.toggle_key}")
        print(f"Control de càmera inicial: {'HABILITAT' if self.camera_enabled else 'DESABILITAT'}")
        print("\nPrem Ctrl+C per aturar.")
        
        self.input_handler.start()
    
    def stop(self) -> None:
        """Atura el controlador i neteja recursos."""
        print("\nAturant controlador...")
        self.input_handler.stop()
        self.gamepad.reset()
        print("Controlador aturat correctament.")
    
    def run(self) -> None:
        """Executa el bucle principal del controlador."""
        self.start()
        
        update_interval = self.general_config.get('update_interval_ms', 16) / 1000.0
        
        try:
            while True:
                # Actualitza l'estat del stick esquerre des de les tecles
                self._update_left_stick_from_keys()
                
                # Actualitza el gamepad
                self.update()
                
                # Espera fins al següent cicle
                time.sleep(update_interval)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()


def main():
    """Funció principal per executar el controlador."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Controlador M&K per a Ryujinx - The Legend of Zelda: Tears of the Kingdom'
    )
    parser.add_argument(
        '-c', '--config',
        type=str,
        default='config.yaml',
        help='Camí al fitxer de configuració YAML (per defecte: config.yaml)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Activa el mode de depuració'
    )
    
    args = parser.parse_args()
    
    # Carrega la configuració
    config_path = args.config
    
    # Crea i executa el controlador
    controller = MKController(config_path=config_path)
    
    if args.debug:
        controller.debug_mode = True
    
    controller.run()


if __name__ == '__main__':
    main()
