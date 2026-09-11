"""
config_manager.py - Gestor de configuració per al sistema de control M&K per a Ryujinx

Aquest mòdul s'encarrega de carregar i validar la configuració des del fitxer YAML.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Gestiona la càrrega i validació de la configuració."""
    
    DEFAULT_CONFIG = {
        'keyboard_mapping': {
            'a': 'BUTTON_A',
            'b': 'BUTTON_B',
            'x': 'BUTTON_X',
            'y': 'BUTTON_Y',
            'q': 'BUTTON_L',
            'e': 'BUTTON_R',
            'z': 'BUTTON_ZL',
            'c': 'BUTTON_ZR',
            'space': 'BUTTON_A',
            'enter': 'BUTTON_PLUS',
            'backspace': 'BUTTON_MINUS',
            'up': 'DPAD_UP',
            'down': 'DPAD_DOWN',
            'left': 'DPAD_LEFT',
            'right': 'DPAD_RIGHT',
            'w': 'STICK_LEFT_UP',
            's': 'STICK_LEFT_DOWN',
            'a_key': 'STICK_LEFT_LEFT',
            'd': 'STICK_LEFT_RIGHT',
            'f': 'BUTTON_HOME',
            'tab': 'BUTTON_CAPTURE'
        },
        'mouse_camera': {
            'enabled': True,
            'toggle_key': 'right_alt',
            'sensitivity_x': 0.5,
            'sensitivity_y': 0.5,
            'invert_y': False,
            'deadzone': 0.1,
            'max_speed': 1.0,
            'capture_cursor': False
        },
        'general': {
            'update_interval_ms': 16,
            'debug_mode': False
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicialitza el gestor de configuració.
        
        Args:
            config_path: Camí al fitxer de configuració YAML. Si és None, usa valors per defecte.
        """
        self.config_path = Path(config_path) if config_path else None
        self.config = self.DEFAULT_CONFIG.copy()
        
        if self.config_path and self.config_path.exists():
            self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Carrega la configuració des del fitxer YAML.
        
        Returns:
            Diccionari amb la configuració carregada.
        """
        if not self.config_path or not self.config_path.exists():
            return self.config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
            
            if loaded_config:
                # Fusió de configuracions (els valors carregats sobrescriuen els per defecte)
                self._merge_config(loaded_config)
            
            return self.config
        except Exception as e:
            print(f"Error carregant la configuració: {e}")
            print("S'utilitzarà la configuració per defecte.")
            return self.config
    
    def _merge_config(self, loaded_config: Dict[str, Any]) -> None:
        """
        Fusiona la configuració carregada amb la per defecte.
        
        Args:
            loaded_config: Configuració carregada del fitxer YAML.
        """
        for section, values in loaded_config.items():
            if section in self.config and isinstance(values, dict):
                self.config[section].update(values)
            elif section in self.config:
                self.config[section] = values
    
    def get_keyboard_mapping(self) -> Dict[str, str]:
        """Retorna el mapeig de teclat."""
        return self.config.get('keyboard_mapping', {})
    
    def get_mouse_camera_config(self) -> Dict[str, Any]:
        """Retorna la configuració del ratolí per a la càmera."""
        return self.config.get('mouse_camera', {})
    
    def get_general_config(self) -> Dict[str, Any]:
        """Retorna la configuració general."""
        return self.config.get('general', {})
    
    def get_toggle_key(self) -> str:
        """Retorna la tecla per activar/desactivar el control de càmera."""
        return self.config['mouse_camera'].get('toggle_key', 'right_alt')
    
    def is_debug_mode(self) -> bool:
        """Indica si el mode de depuració està activat."""
        return self.config['general'].get('debug_mode', False)
    
    def save_config(self, path: Optional[str] = None) -> bool:
        """
        Desa la configuració actual en un fitxer YAML.
        
        Args:
            path: Camí on desar la configuració. Si és None, usa el camí original.
        
        Returns:
            True si s'ha desat correctament, False altrament.
        """
        save_path = Path(path) if path else self.config_path
        
        if not save_path:
            print("No s'ha especificat un camí per desar la configuració.")
            return False
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            print(f"Error desant la configuració: {e}")
            return False
    
    def create_default_config(self, path: str) -> bool:
        """
        Crea un fitxer de configuració per defecte.
        
        Args:
            path: Camí on crear el fitxer de configuració.
        
        Returns:
            True si s'ha creat correctament, False altrament.
        """
        try:
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(self.DEFAULT_CONFIG, f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            print(f"Error creant la configuració per defecte: {e}")
            return False
