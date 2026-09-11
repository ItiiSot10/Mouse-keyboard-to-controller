"""
test_gamepad.py - Script de prova per al gamepad virtual

Aquest script verifica que el gamepad virtual funciona correctament
simulant diferents entrades i mostrant l'estat.
"""

import time
import sys


def test_virtual_gamepad():
    """Prova el funcionament del gamepad virtual."""
    print("=" * 60)
    print("TEST DE GAMEPAD VIRTUAL")
    print("=" * 60)
    
    try:
        from virtual_gamepad import create_gamepad, VGAMEPAD_AVAILABLE
    except Exception as e:
        print(f"ERROR: No s'ha pogut importar el mòdul virtual_gamepad: {e}")
        return False
    
    # Verifica disponibilitat
    if not VGAMEPAD_AVAILABLE:
        print("\n⚠️  AVÍS: vgamepad no està disponible.")
        print("Això és normal si no estàs executant a Windows.")
        print("\nPer instal·lar vgamepad a Windows:")
        print("  1. Obre una terminal com a Administrador")
        print("  2. Executa: pip install vgamepad")
        print("  3. Si cal, instal·la ViGEmBus des de:")
        print("     https://github.com/ViGEm/ViGEmBus/releases")
        return False
    
    print("\n✓ vgamepad està disponible")
    
    # Crea el gamepad
    try:
        gamepad = create_gamepad()
        print("✓ Gamepad virtual creat correctament")
    except Exception as e:
        print(f"✗ ERROR creant el gamepad: {e}")
        return False
    
    # Prova els botons
    print("\n--- Provant botons ---")
    test_buttons = ['BUTTON_A', 'BUTTON_B', 'BUTTON_X', 'BUTTON_Y']
    
    for button in test_buttons:
        print(f"  Premient {button}...")
        gamepad.press_button(button)
        gamepad.update()
        time.sleep(0.2)
        gamepad.release_button(button)
        gamepad.update()
        time.sleep(0.1)
    
    print("✓ Botons provats correctament")
    
    # Prova els sticks
    print("\n--- Provant sticks analògics ---")
    
    # Stick esquerre
    print("  Stick esquerre: centre")
    gamepad.set_left_stick(0.0, 0.0)
    gamepad.update()
    time.sleep(0.2)
    
    print("  Stick esquerre: amunt-esquerra")
    gamepad.set_left_stick(-0.5, 0.5)
    gamepad.update()
    time.sleep(0.2)
    
    print("  Stick esquerre: baix-dreta")
    gamepad.set_left_stick(0.5, -0.5)
    gamepad.update()
    time.sleep(0.2)
    
    # Stick dret
    print("  Stick dret: centre")
    gamepad.set_right_stick(0.0, 0.0)
    gamepad.update()
    time.sleep(0.2)
    
    print("  Stick dret: amunt")
    gamepad.set_right_stick(0.0, 0.5)
    gamepad.update()
    time.sleep(0.2)
    
    print("  Stick dret: avall")
    gamepad.set_right_stick(0.0, -0.5)
    gamepad.update()
    time.sleep(0.2)
    
    # Torna al centre
    gamepad.set_left_stick(0.0, 0.0)
    gamepad.set_right_stick(0.0, 0.0)
    gamepad.update()
    
    print("✓ Sticks provats correctament")
    
    # Prova triggers
    print("\n--- Provant triggers ---")
    print("  Trigger esquerre (L)...")
    gamepad.press_button('BUTTON_L')
    gamepad.update()
    time.sleep(0.3)
    gamepad.release_button('BUTTON_L')
    gamepad.update()
    
    print("  Trigger dret (R)...")
    gamepad.press_button('BUTTON_R')
    gamepad.update()
    time.sleep(0.3)
    gamepad.release_button('BUTTON_R')
    gamepad.update()
    
    print("✓ Triggers provats correctament")
    
    # Neteja
    gamepad.reset()
    gamepad.update()
    
    print("\n" + "=" * 60)
    print("✅ TOTES LES PROVES S'HAN COMPLETAT CORRECTAMENT")
    print("=" * 60)
    print("\nEl gamepad virtual està llest per usar-se amb Ryujinx.")
    print("\nPròxims passos:")
    print("  1. Executa: python mk_controller.py")
    print("  2. Obre Ryujinx")
    print("  3. Ves a Options → Settings → Input")
    print("  4. Selecciona 'XInput Controller' com a dispositiu")
    print("  5. Comença a jugar!")
    
    return True


def test_input_handler():
    """Prova el gestor d'entrades de teclat i ratolí."""
    print("\n" + "=" * 60)
    print("TEST D'INPUT HANDLER")
    print("=" * 60)
    
    try:
        from input_handler import InputHandler
    except Exception as e:
        print(f"ERROR: No s'ha pogut importar InputHandler: {e}")
        return False
    
    print("\n✓ InputHandler importat correctament")
    
    # Callbacks de prova
    pressed_keys = []
    mouse_moves = []
    
    def on_key_press(key_name):
        pressed_keys.append(key_name)
        print(f"  [Teclat] Tecla premuda: {key_name}")
    
    def on_key_release(key_name):
        print(f"  [Teclat] Tecla alliberada: {key_name}")
    
    def on_mouse_move(dx, dy):
        if abs(dx) > 10 or abs(dy) > 10:  # Només mostra moviments significatius
            mouse_moves.append((dx, dy))
            print(f"  [Ratolí] Moviment: ({dx}, {dy})")
    
    # Crea l'input handler
    handler = InputHandler(
        on_key_press=on_key_press,
        on_key_release=on_key_release,
        on_mouse_move=on_mouse_move
    )
    
    print("\nIniciant captura d'entrades...")
    print("Prem tecles i mou el ratolí durant 5 segons.")
    print("(o prem Ctrl+C per cancel·lar)")
    
    handler.start()
    
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        print("\nCaptura cancel·lada per l'usuari.")
    finally:
        handler.stop()
    
    print(f"\n✓ Captura completada")
    print(f"  Tecles registrades: {len(pressed_keys)}")
    print(f"  Moviments de ratolí: {len(mouse_moves)}")
    
    return True


def main():
    """Funció principal."""
    print("\n🎮 SISTEMA DE CONTROL M&K PER A RYUJINX 🎮")
    print("The Legend of Zelda: Tears of the Kingdom")
    print()
    
    # Test del gamepad
    gamepad_ok = test_virtual_gamepad()
    
    # Test de l'input handler (opcional)
    if gamepad_ok:
        response = input("\nVols provar també l'Input Handler? (s/n): ").lower()
        if response == 's':
            test_input_handler()
    
    print("\n" + "=" * 60)
    print("Tests finalitzats.")
    print("=" * 60)


if __name__ == '__main__':
    main()
