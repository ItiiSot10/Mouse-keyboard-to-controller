# Mouse-keyboard-to-controller

Aquest projecte converteix les entrades de ratolí i teclat en entrades de controlador (DualShock 4) per utilitzar-les amb emuladors com Ryujinx o jocs que requereixen controlador.

## Requisits

- Python 3.7+
- Windows (necessari per al driver ViGEmBus)
- [ViGEmBus](https://github.com/ViGEm/ViGEmBus/releases) instal·lat
- Controlador DualShock 4 configurat a Ryujinx o altre emulador/joc

## Instal·lació

1. Instal·la les dependències de Python:

```bash
pip install vgamepad pynput pyyaml
```

2. Assegura't que ViGEmBus està instal·lat al teu sistema Windows.

## Configuració

Edita el fitxer `config.yaml` per personalitzar:

- **Sensibilitat del ratolí**: Ajusta `sensitivity_x` i `sensitivity_y` per controlar la velocitat de la càmera.
- **Zona morta**: Configura `deadzone` per evitar drift no desitjat.
- **Mapeig de tecles**: Assigna les tecles del teclat als botons del controlador (A, B, X, Y, etc.).
- **Stick esquerre**: Configura les tecles de moviment (per defecte WASD).
- **D-Pad**: Assigna les tecles de fletxa del teclat.

Exemple de configuració:

```yaml
camera:
  sensitivity_x: 0.8
  sensitivity_y: 0.8
  invert_y: false
  deadzone: 0.15
  max_speed: 1.0

buttons:
  A: 'k'
  B: 'j'
  X: 'i'
  Y: 'l'
  stick_left_up: 'w'
  stick_left_down: 's'
  stick_left_left: 'a'
  stick_left_right: 'd'
```

## Ús

Executa el programa:

```bash
python main.py
```

El programa es quedarà executant-se en segon pla fins que premis `Ctrl+C` per aturar-lo.

## Notes Importants

- **Ryujinx**: Configura el "Player 1" com a controlador USB/DualShock 4.
- **Windows**: Aquest programa només funciona a Windows degut a la dependència de ViGEmBus.
- **Permís d'administrador**: Pot ser necessari executar el programa com a administrador per accedir al driver de ViGEmBus.

## Solució de Problemes

1. **El controlador no és detectat**: Verifica que ViGEmBus estigui correctament instal·lat.
2. **Les entrades no responen**: Comprova que el fitxer `config.yaml` tingui una sintaxi correcta.
3. **La càmera va massa lenta/ràpida**: Ajusta els valors de sensibilitat al `config.yaml`.

## Llicència

Lliure ús i modificació.
