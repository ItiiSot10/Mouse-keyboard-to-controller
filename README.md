# Controlador M&K per a Ryujinx - The Legend of Zelda: Tears of the Kingdom

Aquest projecte proporciona un sistema de compatibilitat per jugar amb **ratolí i teclat** a *The Legend of Zelda: Tears of the Kingdom* executant-se a l'emulador **Ryujinx** a Windows.

## 📋 Resum de Viabilitat

**ÉS VIABLE** utilitzant un controlador virtual XInput (vgamepad) que emula un comandament de Xbox 360, el qual Ryujinx pot detectar i mapejar com un control de Nintendo Switch Pro.

### Enfocament Recomanat per a Windows 11

1. **Controlador Virtual**: Utilitzar `vgamepad` (biblioteca Python per a XInput virtual)
2. **Captura d'Entrades**: Utilitzar `pynput` per capturar teclat i ratolí
3. **Configuració**: Fitxer YAML per a un mapeig flexible i editable
4. **Integració amb Ryujinx**: Configurar Ryujinx per usar el gamepad virtual com a "Pro Controller"

### Limitacions Tècniques

- **vgamepad només funciona a Windows**: Requereix drivers XInput
- **Pot requerir permisos d'administrador**: Per instal·lar els drivers del gamepad virtual
- **Latència mínima**: Hi ha un petit retard entre l'entrada i la simulació (~8-16ms)
- **No tots els botons són mapables**: El botó "Capture" no existeix a XInput, es mapa a "Back"
- **El cursor del ratolí**: Pot necessitar configuració addicional per a captura/llibertat

---

## 🛠️ Instruccions d'Instal·lació

### 1. Requisits Previs

- **Python 3.10 o superior** (el teu entorn: Python 3.14 ✅)
- **Windows 11** (el teu sistema: Windows 11 ✅)
- **Ryujinx 19.0.1** (la teva versió: 19.0.1 ✅)

### 2. Instal·lació de Dependències

Obre una terminal com a **Administrador** (necessari per als drivers de vgamepad):

```bash
# Crea un entorn virtual (recomanat)
python -m venv venv
venv\Scripts\activate

# Instal·la les dependències
pip install vgamepad pynput pyyaml
```

### 3. Configuració de Ryujinx

1. Obre **Ryujinx**
2. Ves a **Options** → **Settings** → **Input**
3. A "Input Device", selecciona **XInput Controller** (o "GamePad")
4. Configura els botons segons les teves preferències (o deixa'ls per defecte)
5. Assegura't que el perfil està **activat**

### 4. Verificació del Gamepad Virtual

Per verificar que el gamepad virtual funciona:

```bash
python test_gamepad.py
```

Hauries de veure un missatge confirmant que el gamepad està disponible.

---

## 📁 Estructura del Projecte

```
/workspace/
├── config.yaml           # Fitxer de configuració (editable)
├── config_manager.py     # Gestor de configuració
├── input_handler.py      # Captura de teclat i ratolí
├── virtual_gamepad.py    # Gamepad virtual XInput
├── mk_controller.py      # Controlador principal
├── test_gamepad.py       # Script de prova
└── README.md             # Aquest fitxer
```

---

## ⚙️ Ús

### Execució Bàsica

```bash
python mk_controller.py
```

### Execució amb Configuració Personalitzada

```bash
python mk_controller.py -c config.yaml
```

### Mode de Depuració

```bash
python mk_controller.py --debug
```

### Paràmetres de Línia de Comandes

| Paràmetre | Descripció |
|-----------|------------|
| `-c, --config` | Camí al fitxer de configuració YAML (per defecte: `config.yaml`) |
| `--debug` | Activa el mode de depuració (mostra entrades en temps real) |

---

## 🎮 Configuració del Fitxer `config.yaml`

### Mapeig de Teclat

```yaml
keyboard_mapping:
  # Botons principals
  a: BUTTON_A
  b: BUTTON_B
  x: BUTTON_X
  y: BUTTON_Y
  
  # Gallets
  q: BUTTON_L
  e: BUTTON_R
  z: BUTTON_ZL
  c: BUTTON_ZR
  
  # Botons especials
  space: BUTTON_A
  enter: BUTTON_PLUS
  backspace: BUTTON_MINUS
  f: BUTTON_HOME
  tab: BUTTON_CAPTURE
  
  # D-Pad
  up: DPAD_UP
  down: DPAD_DOWN
  left: DPAD_LEFT
  right: DPAD_RIGHT
  
  # Stick esquerre (moviment)
  w: STICK_LEFT_UP
  s: STICK_LEFT_DOWN
  a_key: STICK_LEFT_LEFT
  d: STICK_LEFT_RIGHT
```

### Configuració del Ratolí (Càmera)

```yaml
mouse_camera:
  enabled: true              # Habilita el control de càmera
  toggle_key: right_alt      # Tecla per activar/desactivar
  sensitivity_x: 0.5         # Sensibilitat horitzontal (0.1 - 2.0)
  sensitivity_y: 0.5         # Sensibilitat vertical (0.1 - 2.0)
  invert_y: false            # Inverteix l'eix Y (com a FPS)
  deadzone: 0.1              # Zona morta (0.0 - 0.3)
  max_speed: 1.0             # Velocitat màxima del stick (0.5 - 1.0)
  capture_cursor: false      # Captura el cursor (experimental)
```

### Configuració General

```yaml
general:
  update_interval_ms: 16     # Interval d'actualització (60 FPS = 16ms)
  debug_mode: false          # Mode de depuració
```

---

## 🔧 Solució de Problemes

### 1. "vgamepad no està disponible"

**Causa**: Els drivers XInput no estan instal·lats o no tens permisos d'administrador.

**Solució**:
```bash
# Executa la terminal com a Administrador
pip install vgamepad --force-reinstall
```

Si persisteix, instal·la manualment els drivers:
- Descarga [ViGEmBus](https://github.com/ViGEm/ViGEmBus/releases)
- Instal·la el paquet `ViGEmBus_Setup_1.17.333.exe`
- Reinicia l'ordinador

### 2. Ryujinx No Detecta el Gamepad

**Causa**: El gamepad virtual no està actiu abans d'obrir Ryujinx.

**Solució**:
1. Executa `python mk_controller.py` **abans** d'obrir Ryujinx
2. A Ryujinx, ves a Input i canvia el dispositiu a "XInput Controller"
3. Reinicia Ryujinx si cal

### 3. La Càmera No Es Mou

**Causa**: El toggle de la càmera no està activat.

**Solució**:
- Prem la tecla `Alt Dret` (per defecte) per activar el control de càmera
- Verifica que `mouse_camera.enabled` sigui `true` al `config.yaml`
- Prova amb `--debug` per veure si es detecten els moviments del ratolí

### 4. Moviment de Càmera Massa Lent/Ràpid

**Solució**: Ajusta `sensitivity_x` i `sensitivity_y` al `config.yaml`:
- Valors més alts (1.0-2.0): moviment més ràpid
- Valors més baixos (0.1-0.3): moviment més precís

### 5. Conflicte amb Tecles del Sistema

**Causa**: Algunes tecles poden estar interceptades per Windows.

**Solució**:
- Evita tecles com `Win`, `Alt+Tab`, `Ctrl+Esc`
- Utilitza tecles de funció (F1-F12) o combinacions menys comunes

---

## ⚠️ Consideracions Legals i de Seguretat

Aquest projecte:
- ✅ **NO modifica** el joc ni els fitxers de Ryujinx
- ✅ **NO fa bypass** de cap protecció o DRM
- ✅ **Només simula** entrades de gamepad estàndard (XInput)
- ✅ És **legal** sempre que tinguis una còpia legal del joc

**Permisos Necessaris**:
- Pot requerir **permisos d'administrador** per instal·lar drivers de gamepad virtual
- No requereix accés a fitxers del sistema més enllà dels drivers estàndard

---

## 🧪 Script de Prova

S'inclou un script `test_gamepad.py` per verificar que el gamepad virtual funciona correctament.

```bash
python test_gamepad.py
```

Aquest script:
1. Crea un gamepad virtual
2. Simula prems de botons
3. Mostra l'estat del gamepad

---

## 📝 Notes Addicionals

### Alternatives si vgamepad No Funciona

1. **Steam Input**: Configura el joc via Steam i usa el seu sistema de mapeig
2. **reWASD**: Programa de pagament per a mapeig avançat
3. **Xpadder**: Programa clàssic per a mapeig de teclat a gamepad

### Optimitzacions Futures

- [ ] Suport per a múltiples perfils de configuració
- [ ] Interfície gràfica (GUI) per a configuració
- [ ] Suport per a Linux (evdev/uinput)
- [ ] Integració amb API de giroscopi (si disponible)

---

## 📄 Llicència

Aquest codi es proporciona amb finalitats educatives i de recerca. Assegura't de complir amb els termes de llicència de Ryujinx i de posseir una còpia legal del joc.

---

## 🤝 Contribucions

Les contribucions són benvingudes! Si trobes errors o tens millores, obre un issue o pull request.
