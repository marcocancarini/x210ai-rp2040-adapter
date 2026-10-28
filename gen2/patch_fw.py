# -*- coding: utf-8 -*-
"""Applica le modifiche X210Ai rev 2.0 al firmware hektopuss (commit 970379d).

uso: python3 patch_fw.py <sketch_dir>   (la cartella ThinkPad_RP2040_Keyboard copiata dall'originale)
Ogni sostituzione deve trovare il testo originale esattamente una volta.
"""
import os
import sys

D = sys.argv[1]


def patch(fname, pairs):
    p = os.path.join(D, fname)
    raw = open(p, encoding="utf-8", newline="").read()
    crlf = "\r\n" in raw
    t = raw.replace("\r\n", "\n")
    for old, new in pairs:
        n = t.count(old)
        if n != 1:
            raise SystemExit(f"{fname}: trovato {n} volte:\n{old[:200]}")
        t = t.replace(old, new)
    if crlf:
        t = t.replace("\n", "\r\n")
    open(p, "w", encoding="utf-8", newline="").write(t)
    print(f"{fname}: {len(pairs)} modifiche")


# ------------------------------------------------------------------ keycodes.h
patch("keycodes.h", [(
    "#define KEY_THINKLIGHT      \t\t( 0x0001 | 0xE100 ) //use reserved range here ",
    "#define KEY_THINKLIGHT      \t\t( 0x0001 | 0xE100 ) //use reserved range here \n"
    "// X210Ai: tasti aggiuntivi della tastiera giapponese (HID Keyboard page 0x87-0x8B)\n"
    "#define KEY_INTERNATIONAL1      ( 0x87 | 0xF000 ) // ro  \\\\ _\n"
    "#define KEY_INTERNATIONAL2      ( 0x88 | 0xF000 ) // katakana/hiragana\n"
    "#define KEY_INTERNATIONAL3      ( 0x89 | 0xF000 ) // yen\n"
    "#define KEY_INTERNATIONAL4      ( 0x8A | 0xF000 ) // henkan\n"
    "#define KEY_INTERNATIONAL5      ( 0x8B | 0xF000 ) // muhenkan"),
])

# ------------------------------------------------------------------ Keyboard2.h / .cpp
patch("Keyboard2.h", [
    ("  void systemPress(uint8_t k);\n  void systemRelease();\n",
     "  void systemPress(uint8_t k);\n  void systemRelease();\n"
     "  //X210Ai: tasto radio (modalita' aereo) - Generic Desktop 0x0C/0xC6, Windows e Linux (KEY_RFKILL)\n"
     "  void radioButton(bool pressed);\n"),
    ("    uint8_t _idSystem;\n", "    uint8_t _idSystem;\n    uint8_t _idRadio;\n"),
])
patch("Keyboard2.cpp", [
    ("//needed to copy this\n",
     "// X210Ai: Wireless Radio Controls (airplane mode). Il Report ID deve stare all'offset 6:\n"
     "// il core arduino-pico lo riscrive in base all'ordine di registrazione.\n"
     "#define TUD_HID_REPORT_DESC_RADIO_X210(...) \\\n"
     "  HID_USAGE_PAGE ( HID_USAGE_PAGE_DESKTOP     ) ,\\\n"
     "  HID_USAGE      ( 0x0C                       ) ,\\\n"
     "  HID_COLLECTION ( HID_COLLECTION_APPLICATION ) ,\\\n"
     "    __VA_ARGS__ \\\n"
     "    HID_LOGICAL_MIN  ( 0 ) ,\\\n"
     "    HID_LOGICAL_MAX  ( 1 ) ,\\\n"
     "    HID_USAGE        ( 0xC6 ) ,\\\n"
     "    HID_REPORT_COUNT ( 1 ) ,\\\n"
     "    HID_REPORT_SIZE  ( 1 ) ,\\\n"
     "    HID_INPUT        ( HID_DATA | HID_VARIABLE | HID_RELATIVE ) ,\\\n"
     "    HID_REPORT_SIZE  ( 7 ) ,\\\n"
     "    HID_INPUT        ( HID_CONSTANT ) ,\\\n"
     "  HID_COLLECTION_END \\\n\n"
     "//needed to copy this\n"),
    ("static const uint8_t desc_hid_report_system[] = { TUD_HID_REPORT_DESC_SYSTEM_CONTROL_KB2(HID_REPORT_ID(3)) };\n",
     "static const uint8_t desc_hid_report_system[] = { TUD_HID_REPORT_DESC_SYSTEM_CONTROL_KB2(HID_REPORT_ID(3)) };\n"
     "static const uint8_t desc_hid_report_radio[] = { TUD_HID_REPORT_DESC_RADIO_X210(HID_REPORT_ID(4)) };\n"),
    ("  _idSystem = USB.registerHIDDevice(desc_hid_report_system, sizeof(desc_hid_report_system), 12, 0x0002);\n",
     "  _idSystem = USB.registerHIDDevice(desc_hid_report_system, sizeof(desc_hid_report_system), 12, 0x0002);\n"
     "  _idRadio = USB.registerHIDDevice(desc_hid_report_radio, sizeof(desc_hid_report_radio), 13, 0x0004);\n"),
    ("    USB.unregisterHIDDevice(_idSystem);\n",
     "    USB.unregisterHIDDevice(_idSystem);\n    USB.unregisterHIDDevice(_idRadio);\n"),
    ("void Keyboard2::systemRelease() {\n  sendSystemReport(0);\n}\n",
     "void Keyboard2::systemRelease() {\n  sendSystemReport(0);\n}\n\n"
     "void Keyboard2::radioButton(bool pressed) {\n"
     "    if (!_running) {\n        return;\n    }\n"
     "    uint8_t v = pressed ? 1 : 0;\n"
     "    CoreMutex m(&USB.mutex);\n    tud_task();\n"
     "    if (USB.HIDReady()) {\n"
     "        tud_hid_report(USB.findHIDReportID(_idRadio), &v, sizeof(v));\n    }\n"
     "    tud_task();\n}\n"),
])

# ------------------------------------------------------------------ sketch
INO = "ThinkPad_RP2040_Keyboard.ino"

NEW_GLOBALS = r'''
// ===================== X210Ai rev 2.0: impostazioni, swap Fn/Ctrl, JIS, EC =====================
#define LCTRL_ROW      9     // posizione di Ctrl sinistro nella matrice (riga firmware, colonna firmware)
#define LCTRL_COL      0
#define TV_ROW         3     // ThinkVantage
#define TV_COL         7
#define TV_HOLD_MS     3000  // Fn+ThinkVantage tenuti 3 s = riavvio in modalita' UF2
#define SWAP_HOLD_MS   2000  // Fn+Ctrl sinistro tenuti 2 s = scambia Fn e Ctrl

// EEPROM emulata in flash: 0 = magic, 1 = swap Fn/Ctrl, 8..17 = 5 coppie (riga, colonna) dei tasti JIS
#define EE_SIZE        256
#define EE_MAGIC       0x5A
#define EE_ADDR_MAGIC  0
#define EE_ADDR_SWAP   1
#define EE_ADDR_JIS    8
#define JIS_KEYS       5

bool SWAP_FN_CTRL = false;
uint8_t jis_pos[JIS_KEYS][2];
uint8_t jis_learn = 0;                 // 0 = spento, 1..5 = in attesa del tasto n
const uint16_t jis_code[JIS_KEYS] = {KEY_INTERNATIONAL1, KEY_INTERNATIONAL2, KEY_INTERNATIONAL3,
                                     KEY_INTERNATIONAL4, KEY_INTERNATIONAL5};
const char* jis_name[JIS_KEYS] = {"ro (\\ _, accanto a Shift destro)", "katakana/hiragana (kana)",
                                  "yen (accanto a Backspace)", "henkan (a destra della barra)",
                                  "muhenkan (a sinistra della barra)"};

bool phys_fn_old = false;              // stato precedente del tasto Fn fisico (quando fa da Ctrl)
unsigned long swap_combo_ms = 0;
bool swap_combo_latched = false;
unsigned long tv_down_ms = 0;
bool tv_armed = false;

// Emulazione Fn+PgUp verso l'EC della scheda madre (ThinkLight)
enum { EC_IDLE, EC_FN_DOWN, EC_PGUP_DOWN, EC_PGUP_UP, EC_GAP };
typedef struct {
  uint8_t state;
  uint8_t pending;
  unsigned long t;
} EC_;
EC_ EC {EC_IDLE, 0, 0};
#define EC_FN_LEAD_MS   40
#define EC_PGUP_MS     100
#define EC_FN_TAIL_MS   40
#define EC_GAP_MS      150

void settings_load();
void settings_save();
void swap_toggle();
bool read_single_key(int row, int col);
uint16_t extra_key_at(int row, int col);
void ec_init();
void ec_thinklight();
void ec_task();
void printJis();
'''

NEW_FUNCS = r'''

// ===================== X210Ai rev 2.0: funzioni aggiunte =====================

void settings_save() {
  EEPROM.write(EE_ADDR_MAGIC, EE_MAGIC);
  EEPROM.write(EE_ADDR_SWAP, SWAP_FN_CTRL ? 1 : 0);
  for (int i = 0; i < JIS_KEYS; i++) {
    EEPROM.write(EE_ADDR_JIS + 2 * i, jis_pos[i][0]);
    EEPROM.write(EE_ADDR_JIS + 2 * i + 1, jis_pos[i][1]);
  }
  EEPROM.commit();
}

void settings_load() {
  EEPROM.begin(EE_SIZE);
  if (EEPROM.read(EE_ADDR_MAGIC) != EE_MAGIC) {
    SWAP_FN_CTRL = false;
    for (int i = 0; i < JIS_KEYS; i++) {
      jis_pos[i][0] = 0xFF;
      jis_pos[i][1] = 0xFF;
    }
    settings_save();
    return;
  }
  SWAP_FN_CTRL = (EEPROM.read(EE_ADDR_SWAP) == 1);
  for (int i = 0; i < JIS_KEYS; i++) {
    jis_pos[i][0] = EEPROM.read(EE_ADDR_JIS + 2 * i);
    jis_pos[i][1] = EEPROM.read(EE_ADDR_JIS + 2 * i + 1);
  }
}

// rilascia tutto quello che e' premuto verso il PC
void release_all_keys() {
  Keyboard_set_modifier(0);
  clear_all_slots();
  Keyboard_send(KB.state);
}

void swap_toggle() {
  SWAP_FN_CTRL = !SWAP_FN_CTRL;
  settings_save();
  release_all_keys();
  Serial.printf("Scambio Fn/Ctrl: %s (salvato)\r\n", SWAP_FN_CTRL ? "ATTIVO" : "spento");
  // conferma: la ThinkLight lampeggia due volte (4 comandi Fn+PgUp all'EC)
  for (int i = 0; i < 4; i++) {
    ec_thinklight();
  }
}

bool read_single_key(int row, int col) {
  go_0(Row_IO[row]);
  delayMicroseconds(50);
  bool p = !digitalRead(Col_IO[col]);
  go_z(Row_IO[row]);
  delayMicroseconds(10);
  return p;
}

// tasti JIS appresi con il comando seriale JIS (posizioni vuote della matrice)
uint16_t extra_key_at(int row, int col) {
  for (int i = 0; i < JIS_KEYS; i++) {
    if (jis_pos[i][0] == row && jis_pos[i][1] == col) {
      return jis_code[i];
    }
  }
  return 0;
}

void printJis() {
  for (int i = 0; i < JIS_KEYS; i++) {
    if (jis_pos[i][0] == 0xFF) {
      Serial.printf("  JIS %d %-36s: non appreso\r\n", i + 1, jis_name[i]);
    } else {
      Serial.printf("  JIS %d %-36s: matrice[%d,%d]\r\n", i + 1, jis_name[i], jis_pos[i][0], jis_pos[i][1]);
    }
  }
}

void ec_init() {
  pinMode(X210_EC_FN_PIN, OUTPUT);
  digitalWrite(X210_EC_FN_PIN, LOW);
  pinMode(X210_EC_PGUP_PIN, OUTPUT);
  digitalWrite(X210_EC_PGUP_PIN, LOW);
  EC.state = EC_IDLE;
  EC.pending = 0;
}

// accoda un comando ThinkLight (Fn+PgUp verso l'EC); al massimo 4 in coda
void ec_thinklight() {
  if (EC.pending < 4) {
    EC.pending++;
  }
}

void ec_task() {
  unsigned long now = millis();
  switch (EC.state) {
    case EC_IDLE:
      if (EC.pending) {
        EC.pending--;
        digitalWrite(X210_EC_FN_PIN, HIGH);      // Fn premuto per l'EC
        EC.t = now;
        EC.state = EC_FN_DOWN;
      }
      break;
    case EC_FN_DOWN:
      if (now - EC.t >= EC_FN_LEAD_MS) {
        digitalWrite(X210_EC_PGUP_PIN, HIGH);    // PgUp premuto (riga 24 - colonna 5)
        EC.t = now;
        EC.state = EC_PGUP_DOWN;
      }
      break;
    case EC_PGUP_DOWN:
      if (now - EC.t >= EC_PGUP_MS) {
        digitalWrite(X210_EC_PGUP_PIN, LOW);
        EC.t = now;
        EC.state = EC_PGUP_UP;
      }
      break;
    case EC_PGUP_UP:
      if (now - EC.t >= EC_FN_TAIL_MS) {
        digitalWrite(X210_EC_FN_PIN, LOW);
        EC.t = now;
        EC.state = EC_GAP;
      }
      break;
    default:
      if (now - EC.t >= EC_GAP_MS) {
        EC.state = EC_IDLE;
      }
      break;
  }
}
'''

SCAN_FN_OLD = """  int old_fn = KB.Fn_pressed;
  KB.Fn_pressed = digitalRead(HOTKEY); // Fn key is pressed (active low)
"""
SCAN_FN_NEW = """  int old_fn = KB.Fn_pressed;
  // X210Ai: Fn fisico e Ctrl sinistro fisico, eventualmente scambiati
  bool phys_fn = (digitalRead(HOTKEY) == LOW); // Fn key is pressed (active low)
  bool phys_lctrl = read_single_key(LCTRL_ROW, LCTRL_COL);
  if (phys_fn && phys_lctrl) {                 // Fn+Ctrl tenuti 2 s: scambio
    if (swap_combo_ms == 0) swap_combo_ms = millis();
    if (!swap_combo_latched && millis() - swap_combo_ms >= SWAP_HOLD_MS) {
      swap_combo_latched = true;
      swap_toggle();
      phys_fn_old = phys_fn;
      old_key[LCTRL_ROW][LCTRL_COL] = !phys_lctrl;
    }
  } else {
    swap_combo_ms = 0;
    swap_combo_latched = false;
  }
  if (SWAP_FN_CTRL) {
    KB.Fn_pressed = phys_lctrl ? LOW : HIGH;   // il Ctrl fisico fa da Fn
    if (phys_fn != phys_fn_old) {              // il Fn fisico fa da Ctrl sinistro
      phys_fn_old = phys_fn;
      if (!swap_combo_latched) key_press(MODIFIERKEY_LEFT_CTRL, phys_fn);
      if (phys_fn && tud_suspended()) tud_remote_wakeup();
    }
  } else {
    KB.Fn_pressed = phys_fn ? LOW : HIGH;
    phys_fn_old = phys_fn;
  }
  if (KB.Fn_pressed == LOW && old_fn == HIGH && tud_suspended()) {
    tud_remote_wakeup();                       // risveglio del PC dalla sospensione
  }
  if (KB.Fn_pressed == HIGH) {
    tv_armed = false;
  }
"""

SCAN_LOOP_OLD = """    for (int y = 0; y < matrix_cols; y++) {   // loop thru the columns
      bool pressed = !digitalRead(Col_IO[y]);
      bool old = !old_key[x][y];
      uint16_t normalCode = normal[x][y];
      uint16_t fnCode = fn_overlay[x][y];

      if (pressed != old) { // check if key is pressed and was not previously pressed or vice versa (aka only process changes)
        if(DEBUG_OUTPUT) {
          Serial.printf("Matrix[%d,%d] = %d\\r\\n",x,y,pressed);
        }
        old_key[x][y] = !pressed; // Save state of key
"""
SCAN_LOOP_NEW = """    for (int y = 0; y < matrix_cols; y++) {   // loop thru the columns
      bool pressed = !digitalRead(Col_IO[y]);
      bool old = !old_key[x][y];
      uint16_t normalCode = normal[x][y];
      uint16_t fnCode = fn_overlay[x][y];

      if (SWAP_FN_CTRL && x == LCTRL_ROW && y == LCTRL_COL) {
        old_key[x][y] = !pressed;  // con lo scambio attivo questo tasto e' il Fn
        continue;
      }

      if (pressed != old) { // check if key is pressed and was not previously pressed or vice versa (aka only process changes)
        if(DEBUG_OUTPUT) {
          Serial.printf("Matrix[%d,%d] = %d\\r\\n",x,y,pressed);
        }
        old_key[x][y] = !pressed; // Save state of key

        if (pressed && tud_suspended()) {
          tud_remote_wakeup();     // un tasto qualsiasi risveglia il PC
        }

        // X210Ai: apprendimento dei tasti JIS (comando seriale JIS)
        if (jis_learn && pressed) {
          if (normalCode == 0 && extra_key_at(x, y) == 0) {
            jis_pos[jis_learn - 1][0] = x;
            jis_pos[jis_learn - 1][1] = y;
            Serial.printf("JIS %d = matrice[%d,%d]\\r\\n", jis_learn, x, y);
            jis_learn++;
            if (jis_learn > JIS_KEYS) {
              jis_learn = 0;
              settings_save();
              Serial.println("Tasti JIS salvati.");
            } else {
              Serial.printf("Premi il tasto JIS %d: %s (ESC = salta)\\r\\n", jis_learn, jis_name[jis_learn - 1]);
            }
            continue;
          } else if (normalCode == KEY_ESC) {
            Serial.printf("JIS %d saltato\\r\\n", jis_learn);
            jis_learn++;
            if (jis_learn > JIS_KEYS) {
              jis_learn = 0;
              settings_save();
              Serial.println("Tasti JIS salvati.");
            } else {
              Serial.printf("Premi il tasto JIS %d: %s (ESC = salta)\\r\\n", jis_learn, jis_name[jis_learn - 1]);
            }
            continue;
          }
        }
"""

TV_OLD = """          //Fn+ThinkVantage = Reboot RP2040
          if(fnCode == KEY_THINK_VANTAGE) {
            Serial.printf("Fn+ThinkVantage %s\\r\\n", (pressed?"pressed":"released"));
            RebootUF2();
          }
"""
TV_NEW = """          //Fn+ThinkVantage = Reboot RP2040 (X210Ai: solo se tenuti premuti 3 s)
          if(fnCode == KEY_THINK_VANTAGE) {
            Serial.printf("Fn+ThinkVantage %s\\r\\n", (pressed?"pressed (tieni 3 s per UF2)":"released"));
            tv_armed = pressed;
            tv_down_ms = millis();
          }

          //Fn+PgUp = ThinkLight: lo gestisce l'EC della scheda madre, glielo inviamo noi
          else if(fnCode == KEY_THINKLIGHT) {
            Serial.printf("Fn+PgUp %s (ThinkLight via EC)\\r\\n", (pressed?"pressed":"released"));
            if(pressed) {
              ec_thinklight();
            }
          }
"""

F5_OLD = """          //Fn+F5 = Wifi Toggle/Status
          else if(normalCode == KEY_F5) {
            Serial.printf("Fn+F5 %s (emulate Win+A)\\r\\n", (pressed?"pressed":"released"));
            keyboard_send_combo(pressed, (uint8_t)MODIFIERKEY_GUI, (uint8_t)KEY_A);
          }
"""
F5_NEW = """          //Fn+F5 = Wireless: tasto radio HID (modalita' aereo su Windows, rfkill su Linux)
          else if(normalCode == KEY_F5) {
            Serial.printf("Fn+F5 %s (radio/airplane mode)\\r\\n", (pressed?"pressed":"released"));
            TP_Keyboard.radioButton(pressed);
          }
"""

NORMAL_OLD = """        // check if normal key exists at this location in the array (a non-zero value)
        else if (normalCode != 0) {
          // if numlock is active, replace key with numlock-table (the numlock-table should hold all entries from the normal-table plus changes, but it never undefines a key, so we do not need to check it )
          // but only if fn is not held down. so you can use fn to override active num-lock
          if(KB.NUMLOCK_ON && !FN_PRESSED) {
            normalCode = numlock[x][y];
          }
          key_press(normalCode, pressed);
        }
"""
NORMAL_NEW = NORMAL_OLD + """        // X210Ai: posizione vuota della mappa: tasto JIS appreso oppure tasto sconosciuto
        else {
          uint16_t jc = extra_key_at(x, y);
          if (jc != 0) {
            key_press(jc, pressed);
          } else if (pressed) {
            Serial.printf("Tasto senza codice: matrice[%d,%d] (usa JIS per assegnarlo)\\r\\n", x, y);
          }
        }
"""

SCAN_END_OLD = """    go_z(Row_IO[x]); // De-activate Row (send it to hi-z)
  }

}
"""
SCAN_END_NEW = """    go_z(Row_IO[x]); // De-activate Row (send it to hi-z)
  }

  // X210Ai: Fn+ThinkVantage tenuti 3 s
  if (tv_armed && FN_PRESSED && !old_key[TV_ROW][TV_COL] && millis() - tv_down_ms >= TV_HOLD_MS) {
    RebootUF2();
  }
}
"""

patch(INO, [
    ('#include "keycodes.h"\n',
     '#include "keycodes.h"\n#include "x210ai_pins.h"   // X210Ai rev 2.0: GPIO della scheda-ponte\n'
     '#include <EEPROM.h>\n#include <tusb.h>\n'),
    ("// LED used for Num-Lock\n#define PIN_LED_BUILTIN    25\n",
     "// X210Ai: nessun LED (GPIO25 e' una riga della matrice)\n"),
    ("#define TP_DATA_PIN         1\n#define TP_CLOCK_PIN        0\n#define TP_RESET_PIN       28\n",
     "#define TP_DATA_PIN         X210_TP_DATA_PIN\n#define TP_CLOCK_PIN        X210_TP_CLOCK_PIN\n"
     "#define TP_RESET_PIN        X210_TP_RESET_PIN\n"),
    ("#define HOTKEY 27          // Fn key \n", "#define HOTKEY X210_FN_PIN  // Fn key \n"),
    ("int Row_IO[matrix_rows] = {11,22,16,21,19,14,10,18,20,24,23,15,17,26,13,12};\n",
     "// X210Ai rev 2.0: vedi x210ai_pins.h\nint Row_IO[matrix_rows] = X210_ROW_IO;\n"),
    ("int Col_IO[matrix_cols] = { 5, 4, 6, 9, 8, 3, 7, 2};\n",
     "int Col_IO[matrix_cols] = X210_COL_IO;\n"),
    ("#define FN_PRESSED (KB.Fn_pressed == LOW)\n", "#define FN_PRESSED (KB.Fn_pressed == LOW)\n" + NEW_GLOBALS),
    ("void setupRP() {\n  rp2040.enableDoubleResetBootloader();\n\n}\n",
     "void setupRP() {\n  rp2040.enableDoubleResetBootloader();\n  ec_init();\n  settings_load();\n}\n"),
    ("  handleKeyboard();\n  //maybe this can be lowered further, but should not be zero (both at 5ms starts to get unreliable)\n"
     "  delay(5); // let voltages and everthing settle\n  handleMouse();\n  delay(5); // let voltages and everthing settle back\n",
     "  handleKeyboard();\n  ec_task();\n  //maybe this can be lowered further, but should not be zero (both at 5ms starts to get unreliable)\n"
     "  delay(5); // let voltages and everthing settle\n  handleMouse();\n  ec_task();\n"
     "  delay(5); // let voltages and everthing settle back\n"),
    ("  //Num-Lock LED\n  pinMode(PIN_LED_BUILTIN, OUTPUT);\n\n", ""),
    ("    digitalWrite(PIN_LED_BUILTIN, KB.NUMLOCK_ON);\n", ""),
    ("  TPE  - Trackpoint Enable/Disable                    Fn+F8\\r\\n\\\n  STAT - Current Status\\r\\n\\\n",
     "  TPE  - Trackpoint Enable/Disable                    Fn+F8\\r\\n\\\n  STAT - Current Status\\r\\n\\\n"
     "  SWAP - scambia Fn e Ctrl sinistro (salvato)         Fn+Ctrl tenuti 2 s\\r\\n\\\n"
     "  LIGHT- ThinkLight on/off tramite l'EC               Fn+PgUp\\r\\n\\\n"
     "  JIS  - impara i 5 tasti extra della tastiera giapponese\\r\\n\\\n"
     "  JISX - cancella i tasti JIS appresi\\r\\n\\\n"),
    ("  , (KB.SCRLOCK_ON?ON:OFF)\n  );\n}\n",
     "  , (KB.SCRLOCK_ON?ON:OFF)\n  );\n"
     "  Serial.printf(\"  X210Ai.SwapFnCtrl:   %s\\r\\n\", (SWAP_FN_CTRL?ON:OFF));\n"
     "  printJis();\n}\n"),
    ("      else if (0 == strcmp(serialbuff, \"TPR\")) {\n        trackpoint_reset();\n      }\n",
     "      else if (0 == strcmp(serialbuff, \"TPR\")) {\n        trackpoint_reset();\n      }\n"
     "      else if (0 == strcmp(serialbuff, \"SWAP\")) {\n        swap_toggle();\n      }\n"
     "      else if (0 == strcmp(serialbuff, \"LIGHT\")) {\n        ec_thinklight();\n      }\n"
     "      else if (0 == strcmp(serialbuff, \"JIS\")) {\n        jis_learn = 1;\n"
     "        Serial.printf(\"Premi il tasto JIS 1: %s (ESC = salta)\\r\\n\", jis_name[0]);\n      }\n"
     "      else if (0 == strcmp(serialbuff, \"JISX\")) {\n        for (int i = 0; i < JIS_KEYS; i++) {\n"
     "          jis_pos[i][0] = 0xFF;\n          jis_pos[i][1] = 0xFF;\n        }\n        settings_save();\n"
     "        Serial.println(\"Tasti JIS cancellati.\");\n      }\n"),
    (SCAN_FN_OLD, SCAN_FN_NEW),
    (SCAN_LOOP_OLD, SCAN_LOOP_NEW),
    (TV_OLD, TV_NEW),
    (F5_OLD, F5_NEW),
    (NORMAL_OLD, NORMAL_NEW),
    (SCAN_END_OLD, SCAN_END_NEW),
    ("void debugPrint(const char str[]) {\n", NEW_FUNCS.lstrip("\n") + "\n\nvoid debugPrint(const char str[]) {\n"),
])
print("ok")
