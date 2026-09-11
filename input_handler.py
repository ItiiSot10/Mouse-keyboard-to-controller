"""
input_handler.py - Gestor d'entrades de teclat i ratolí

Aquest mòdul captura les entrades de teclat i ratolí utilitzant pynput
i les converteix en esdeveniments que el sistema pot processar.
"""

import threading
from typing import Dict, Set, Callable, Optional, Any
from pynput import keyboard, mouse
from pynput.keyboard import Key, KeyCode


class InputHandler:
    """Gestiona la captura d'entrades de teclat i ratolí."""
    
    # Mapeig de tecles especials
    SPECIAL_KEYS = {
        Key.space: 'space',
        Key.enter: 'enter',
        Key.backspace: 'backspace',
        Key.up: 'up',
        Key.down: 'down',
        Key.left: 'left',
        Key.right: 'right',
        Key.shift: 'shift',
        Key.ctrl: 'ctrl',
        Key.alt: 'alt',
        Key.tab: 'tab',
        Key.esc: 'escape',
        Key.caps_lock: 'caps_lock',
        Key.home: 'home',
        Key.end: 'end',
        Key.page_up: 'page_up',
        Key.page_down: 'page_down',
        Key.insert: 'insert',
        Key.delete: 'delete',
    }
    
    # Tecles modificadores dretes
    RIGHT_MODIFIERS = {
        Key.shift_r: 'right_shift',
        Key.ctrl_r: 'right_ctrl',
        Key.alt_r: 'right_alt',
    }
    
    def __init__(self, 
                 on_key_press: Optional[Callable[[str], None]] = None,
                 on_key_release: Optional[Callable[[str], None]] = None,
                 on_mouse_move: Optional[Callable[[float, float], None]] = None,
                 on_mouse_click: Optional[Callable[[str, bool], None]] = None):
        """
        Inicialitza el gestor d'entrades.
        
        Args:
            on_key_press: Callback quan es prem una tecla (rep el nom de la tecla).
            on_key_release: Callback quan s'allibera una tecla.
            on_mouse_move: Callback quan es mou el ratolí (rep dx, dy).
            on_mouse_click: Callback quan es fa clic (rep botó, estat).
        """
        self.on_key_press = on_key_press
        self.on_key_release = on_key_release
        self.on_mouse_move = on_mouse_move
        self.on_mouse_click = on_mouse_click
        
        self.pressed_keys: Set[str] = set()
        self.mouse_buttons: Set[str] = set()
        
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._mouse_listener: Optional[mouse.Listener] = None
        
        self._running = False
        self._lock = threading.Lock()
    
    def _get_key_name(self, key) -> Optional[str]:
        """
        Converteix un objecte Key o KeyCode a un nom de tecla llegible.
        
        Args:
            key: Objecte Key o KeyCode de pynput.
        
        Returns:
            Nom de la tecla o None si no es pot identificar.
        """
        if isinstance(key, KeyCode):
            # Tecla normal (caràcter)
            if key.char:
                return key.char.lower()
            elif key.vk:
                return f'vk_{key.vk}'
        elif isinstance(key, Key):
            # Tecla especial
            if key in self.SPECIAL_KEYS:
                return self.SPECIAL_KEYS[key]
            elif key in self.RIGHT_MODIFIERS:
                return self.RIGHT_MODIFIERS[key]
        
        return None
    
    def _on_key_press(self, key) -> Optional[bool]:
        """Callback intern per a prems de tecla."""
        key_name = self._get_key_name(key)
        
        if key_name:
            with self._lock:
                if key_name not in self.pressed_keys:
                    self.pressed_keys.add(key_name)
                    if self.on_key_press:
                        self.on_key_press(key_name)
        
        # No retornem False per no bloquejar les tecles
        return None
    
    def _on_key_release(self, key) -> Optional[bool]:
        """Callback intern per a alliberaments de tecla."""
        key_name = self._get_key_name(key)
        
        if key_name:
            with self._lock:
                if key_name in self.pressed_keys:
                    self.pressed_keys.discard(key_name)
                    if self.on_key_release:
                        self.on_key_release(key_name)
        
        return None
    
    def _on_mouse_move(self, x: int, y: int, dx: int, dy: int) -> None:
        """Callback intern per a moviment del ratolí."""
        if self.on_mouse_move:
            self.on_mouse_move(dx, dy)
    
    def _on_mouse_click(self, x: int, y: int, button, pressed: bool) -> None:
        """Callback intern per a clics del ratolí."""
        button_name = None
        
        if button == mouse.Button.left:
            button_name = 'left'
        elif button == mouse.Button.right:
            button_name = 'right'
        elif button == mouse.Button.middle:
            button_name = 'middle'
        
        if button_name:
            with self._lock:
                if pressed:
                    self.mouse_buttons.add(button_name)
                else:
                    self.mouse_buttons.discard(button_name)
                
                if self.on_mouse_click:
                    self.on_mouse_click(button_name, pressed)
    
    def _on_mouse_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        """Callback intern per a scroll del ratolí."""
        # El scroll es pot implementar si cal
        pass
    
    def start(self) -> None:
        """Inicia la captura d'entrades en fils separats."""
        if self._running:
            return
        
        self._running = True
        
        # Inicia el listener de teclat
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self._keyboard_listener.start()
        
        # Inicia el listener de ratolí amb moviments relatius
        self._mouse_listener = mouse.Listener(
            on_move=self._on_mouse_move,
            on_click=self._on_mouse_click,
            on_scroll=self._on_mouse_scroll
        )
        self._mouse_listener.start()
    
    def stop(self) -> None:
        """Atura la captura d'entrades."""
        self._running = False
        
        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None
        
        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None
        
        with self._lock:
            self.pressed_keys.clear()
            self.mouse_buttons.clear()
    
    def is_key_pressed(self, key_name: str) -> bool:
        """
        Comprova si una tecla està actualment premuda.
        
        Args:
            key_name: Nom de la tecla a comprovar.
        
        Returns:
            True si la tecla està premuda, False altrament.
        """
        with self._lock:
            return key_name in self.pressed_keys
    
    def is_mouse_button_pressed(self, button_name: str) -> bool:
        """
        Comprova si un botó del ratolí està actualment premut.
        
        Args:
            button_name: Nom del botó ('left', 'right', 'middle').
        
        Returns:
            True si el botó està premut, False altrament.
        """
        with self._lock:
            return button_name in self.mouse_buttons
    
    def get_all_pressed_keys(self) -> Set[str]:
        """Retorna el conjunt de totes les tecles actualment premudes."""
        with self._lock:
            return self.pressed_keys.copy()
    
    def get_all_pressed_mouse_buttons(self) -> Set[str]:
        """Retorna el conjunt de tots els botons del ratolí actualment premuts."""
        with self._lock:
            return self.mouse_buttons.copy()
