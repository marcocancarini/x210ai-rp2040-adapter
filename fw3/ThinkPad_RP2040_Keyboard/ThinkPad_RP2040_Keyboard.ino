/*  fishgod's ThinkPad RP2040 Keyboard 

    Copyright (C) fishgod (2026)

    This program is free software: you can redistribute it and/or
    modify it under the terms of the GNU General Public License a
    published by the Free Software Foundation, version 3.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program. If not, see https://www.gnu.org/licenses/.
*/
/*
   based on the following code:
   https://github.com/thedalles77/USB_Laptop_Keyboard_Controller/tree/master/Example_Keyboards/Lenovo_ThinkPad_T61/Teensy%204p0
   but now so heavily extented, so it's more inspired than based anymore
   the most 1:1 code is probably the ps/2-protocol-stuff

   Copyright 2023 Frank Adams
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
  
   extended features
    - proper TrackPoint with scrolling
    - proper Fn-overlays
    - serial-console
    - hardcoded Fn-Key-Macros
    - massive refactoring
 */


#include "Keyboard2.h"
#include "Mouse2.h"
#include "keycodes.h"
#include "x210ai_pins.h"   // X210Ai rev 2.0: GPIO della scheda-ponte
#include <EEPROM.h>
#include <tusb.h>

// X210Ai: nessun LED (GPIO25 e' una riga della matrice)

// PS/2 Connection
#define TP_DATA_PIN         X210_TP_DATA_PIN
#define TP_CLOCK_PIN        X210_TP_CLOCK_PIN
#define TP_RESET_PIN        X210_TP_RESET_PIN
#define TP_PS2_TIMEOUT_MS 100

// StartUp-Behaviour
#define STARTUP_TRACKPOINT  1
#define STARTUP_DEBUG_OUT   0
#define STARTUP_INFO_OUT    1
#define STARTUP_CAPS_LOCK   0
#define STARTUP_NUM_LOCK    0

// Setup Keyboard-Matrix
const byte matrix_rows = 16;
const byte matrix_cols = 8;
// Fn-Key is not in the Matrix, but on a seperate Pin:
#define HOTKEY X210_FN_PIN  // Fn key 

// Load the normal key matrix with the Teensyduino key names described at www.pjrc.com/teensy/td_keyboard.html
// A zero indicates no normal key at that location.
int normal[matrix_rows][matrix_cols] = {
  {0,           KEY_SCROLL_LOCK, KEY_PRINT_SCREEN, MODIFIERKEY_RIGHT_ALT,  0,   0,             0,               MODIFIERKEY_LEFT_ALT},
  {KEY_HOME,    0,               KEY_END,         KEY_LEFT,      KEY_PAUSE,    0,             0,               KEY_UP},
  {KEY_INSERT,  0,               KEY_F12,         KEY_RIGHT,     0,            0,             0,               0},
  {KEY_DELETE,  KEY_MEDIA_VOLUME_INC, KEY_F11,    KEY_DOWN,      0,            KEY_MEDIA_MUTE,KEY_MEDIA_VOLUME_DEC, KEY_THINK_VANTAGE},
  {KEY_MINUS,   KEY_P,           KEY_0,           KEY_SLASH,     KEY_BACKSLASH,KEY_SEMICOLON, KEY_LEFT_BRACE,  KEY_QUOTE},
  {KEY_F8,      KEY_O,           KEY_9,           0,             KEY_PERIOD,   KEY_L,         KEY_F7,          0},
  {KEY_EQUAL,   KEY_I,           KEY_8,           0,             KEY_COMMA,    KEY_K,         KEY_RIGHT_BRACE, KEY_F6},
  {KEY_TILDE,   KEY_Q,           KEY_1,           0,             KEY_Z,        KEY_A,         KEY_TAB,         KEY_ESC},
  {0,           0,               0,               0,             MODIFIERKEY_RIGHT_SHIFT, 0,  MODIFIERKEY_LEFT_SHIFT,  0},
  {MODIFIERKEY_LEFT_CTRL,  0,    0,               0,             MODIFIERKEY_RIGHT_CTRL,  0,  0,               0},
  {KEY_F1,      KEY_W,           KEY_2,           0,             KEY_X,        KEY_S,         KEY_CAPS_LOCK,   KEY_NON_US_BS},
  {KEY_F2,      KEY_E,           KEY_3,           0,             KEY_C,        KEY_D,         KEY_F3,          KEY_F4},
  {KEY_5,       KEY_R,           KEY_4,           KEY_B,         KEY_V,        KEY_F,         KEY_T,           KEY_G},
  {KEY_F9,      0,               KEY_F10,         KEY_SPACE,     KEY_ENTER,    KEY_BACKSLASH, KEY_BACKSPACE,   KEY_F5},
  {KEY_6,       KEY_U,           KEY_7,           KEY_N,         KEY_M,        KEY_J,         KEY_Y,           KEY_H},
  {KEY_PAGE_UP, MODIFIERKEY_GUI, KEY_PAGE_DOWN,   KEY_AC_FORWARD,KEY_AC_BACK,  KEY_MENU,      0,               0}
};

// Load the num lock key matrix which is the same as the normal matrix except for the number pad keys
// A zero indicates no key at that location.
int numlock[matrix_rows][matrix_cols] = {
  {0,                      KEY_SCROLL_LOCK,      KEY_PRINT_SCREEN,     MODIFIERKEY_RIGHT_ALT,   0,             0,             0,               MODIFIERKEY_LEFT_ALT},
  {KEY_HOME,               0,                    KEY_END,              KEY_LEFT,                KEY_PAUSE,     0,             0,               KEY_UP},
  {KEY_INSERT,             0,                    KEY_F12,              KEY_RIGHT,               0,             0,             0,               0},
  {KEY_DELETE,             KEY_MEDIA_VOLUME_INC, KEY_F11,              KEY_DOWN,                0,             KEY_MEDIA_MUTE,KEY_MEDIA_VOLUME_DEC, KEY_THINK_VANTAGE},
  {KEY_MINUS,              KEYPAD_ASTERIX,       KEYPAD_SLASH,         KEYPAD_PLUS,             KEY_BACKSLASH, KEYPAD_MINUS,  KEY_LEFT_BRACE,  KEY_QUOTE},
  {KEY_F8,                 KEYPAD_6,             KEYPAD_9,             0,                       KEYPAD_PERIOD, KEYPAD_3,      KEY_F7,          0},
  {KEY_EQUAL,              KEYPAD_5,             KEYPAD_8,             0,                       KEY_COMMA,     KEYPAD_2,      KEY_RIGHT_BRACE, KEY_F6},
  {KEY_TILDE,              KEY_Q,                KEY_1,                0,                       KEY_Z,         KEY_A,         KEY_TAB,         KEY_ESC},
  {0,                      0,                    0,                    0,                       MODIFIERKEY_RIGHT_SHIFT, 0,  MODIFIERKEY_LEFT_SHIFT,  0},
  {MODIFIERKEY_LEFT_CTRL,  0,                    0,                    0,                       MODIFIERKEY_RIGHT_CTRL,  0,  0,               0},
  {KEY_F1,                 KEY_W,                KEY_2,                0,                       KEY_X,         KEY_S,         KEY_CAPS_LOCK,   KEY_NON_US_BS},
  {KEY_F2,                 KEY_E,                KEY_3,                0,                       KEY_C,         KEY_D,         KEY_F3,          KEY_F4},
  {KEY_5,                  KEY_R,                KEY_4,                KEY_B,                   KEY_V,         KEY_F,         KEY_T,           KEY_G},
  {KEY_F9,                 0,                    KEY_F10,              KEY_SPACE,               KEY_ENTER,     KEY_BACKSLASH, KEY_BACKSPACE,   KEY_F5},
  {KEY_6,                  KEYPAD_4,             KEYPAD_7,             KEY_N,                   KEYPAD_0,      KEYPAD_1,      KEY_Y,           KEY_H},
  {KEY_PAGE_UP,            MODIFIERKEY_GUI,      KEY_PAGE_DOWN,        KEY_AC_FORWARD,          KEY_AC_BACK,   KEY_MENU,      0,               0}
};

// Fn-Overlay: traditionally there are only a few mappings, here we have num-lock-keys additionally so we can use them with fn-down
// instead of toggeling num-state for this. this is like pressing the keys on the numpad while num-lock is off (resulting in arrows/Home/End/PgUp/PgDn)
// Fn+Document-Keys are mapped to fast-forward/backward, 
// media-keys on cursor keys are there. Display brightness is working too.
// special Fn+Fx Hotkeys are handled explicitily in code for now, because they perform more of a macro instead of a single 1:1 keystroke mapping
// unused Fn+Fx are mapped to the upper 12 Fn-Keys: F1 => F13 ... F12 => F24 to be used for hotkey-mappings on the operating-system-level.
// currently hardcoded:
//  Fn+ThinkVantage = Reboot RP2040
//  Fn+MUTE = Mute Microphone via Win + Alt + K
//  Fn+ScrollLock = NumLock-Key
//  Fn+F2  = F14 : Lock Workstation : Emulate Win+L
//  Fn+F5  = F17 : Wifi : Emulate Win+A
//  Fn+F7  = KEY_SYSTEM_PROJECT : Toggle internal/external screen : Emulate Win+P
//  Fn+F8  = F20 : TrackPoint/Touchpad-Key : Toggle Trackpoint on/off/restart ps/2
//  Fn+F9  = F21 : TrackPoint Reset
//  Fn+F10 = F22 : TrackPoint Init
//  Fn+F11 = F23 : TrackPoint toggle enable
//  Fn+WIN = Toggle Windows-Key
// Mapped here:
//  Fn+F1  = F13
//  Fn+F3  = F15
//  Fn+F4  = KEY_SYSTEM_SLEEP
//  Fn+F6  = F18
// x Fn+F9 = KEY_MEDIA_EJECT
// x Fn+F10= F22
// x Fn+F11= F23
//  Fn+F12 = KEY_SYSTEM_HIBERNATE
//  Fn+Space = AC_ZOOM - does nothing in windows :/
//  Fn+1 = Home    = WebBrowser
//  Fn+2 = Browser = Explorer
//  Fn+3 = Email
//  Fn+4 = Search  = Windows Startmenu Search
//  Fn+5 = Refresh - Läd im Browser neu (wie F5)
//  Fn+6 = Bookmarks
//  Fn+^ = Stop    - Stoppt im Browser das Laden
// x Fn+WIN = KEY_AL_CONSUMER_CONTROL_CONFIGURATION = Legacy Windows Medienwiedergabe

int fn_overlay[matrix_rows][matrix_cols] = {
  {0,                  KEY_SCROLL_LOCK,KEY_SYS_REQUEST,      0,                    0,             0,             0,                    0},
  {KEY_BRIGHTNESS_INC, 0,              KEY_BRIGHTNESS_DEC,   KEY_MEDIA_PREV_TRACK, KEY_PAUSE,     0,             0,                    KEY_MEDIA_STOP},
  {KEY_INSERT,         0,              KEY_SYSTEM_HIBERNATE, KEY_MEDIA_NEXT_TRACK, 0,             0,             0,                    0},
  {KEY_DELETE,         0,              KEY_F23,              KEY_MEDIA_PLAY_PAUSE, 0,             0,             0,                    KEY_THINK_VANTAGE},
  {0,                  KEYPAD_ASTERIX, KEYPAD_SLASH,         KEYPAD_PLUS,          0,             KEYPAD_MINUS,  0,                    0},
  {KEY_F20,            KEYPAD_6,       KEYPAD_9,             0,                    KEYPAD_PERIOD, KEYPAD_3,      KEY_SYSTEM_PROJECT,   0},
  {0,                  KEYPAD_5,       KEYPAD_8,             0,                    0,             KEYPAD_2,      0,                    KEY_F18},
  {KEY_AC_STOP,        KEY_AL_WORD_PROCESSOR,              KEY_AC_HOME,          0,                    0,             0,             0,                    0},
  {0,                  0,              0,                    0,                    0,             0,             0,                    0},
  {0,                  0,              0,                    0,                    0,             0,             0,                    0},
  {KEY_F13,            KEY_AL_TEXT_EDITOR,              KEY_AL_LOCAL_BROWSER, 0,                    0,             0,             0,                    0},
  {KEY_F14,            0,              KEY_AL_EMAIL_READER,  0,                    0,             0,             KEY_F15,              KEY_SYSTEM_SLEEP},
  {KEY_AC_REFRESH,     0,              KEY_AC_SEARCH,        0,                    0,             0,             0,                    0},
  {KEY_MEDIA_EJECT,    0,              KEY_F22,              KEY_AC_ZOOM,          0,             0,             0,                    KEY_F17},
  {KEY_AC_BOOKMARKS,   KEYPAD_4,       KEYPAD_7,             0,                    KEYPAD_0,      KEYPAD_1,      0,                    0},
  {KEY_THINKLIGHT,     KEY_AL_CONSUMER_CONTROL_CONFIGURATION,   0,  KEY_MEDIA_FAST_FORWARD, KEY_MEDIA_REWIND, 0, 0,                    0}
};

// Initialize the old_key matrix with one's. 
// 1 = key not pressed, 0 = key is pressed
// so we can determine what has changed
boolean old_key[matrix_rows][matrix_cols] = {
  {1,1,1,1,1,1,1,1},
  {1,1,1,1,1,1,1,1},
  {1,1,1,1,1,1,1,1},
  {1,1,1,1,1,1,1,1},
  {1,1,1,1,1,1,1,1},
  {1,1,1,1,1,1,1,1},
  {1,1,1,1,1,1,1,1},
  {1,1,1,1,1,1,1,1},
  {1,1,1,1,1,1,1,1},
  {1,1,1,1,1,1,1,1},
  {1,1,1,1,1,1,1,1},
  {1,1,1,1,1,1,1,1},
  {1,1,1,1,1,1,1,1},
  {1,1,1,1,1,1,1,1},
  {1,1,1,1,1,1,1,1},
  {1,1,1,1,1,1,1,1}
};

// ** Row Configuration
// Row FPC pin           # 32,28,24,20,16,12,08,04,22,26,30,18,14,10,06,02,24
// Teensy I/O            # 10,30,08,24,29,27,16,09,26,28,32,31,17,25,33,15,14 <-- what is 8 doing here, its a column down below
// Teensy I/O            # 10,30,24,29,27,16, 9,26,28,32,31,17,25,33,15,14 last known working
// RP2040 I/O            # 11,22,16,21,19,14,10,18,20,24,23,15,17,26,13,12
// X210Ai rev 2.0: vedi x210ai_pins.h
int Row_IO[matrix_rows] = X210_ROW_IO;

// ** Column Configuration **
// Column FPC pin        # 05,09,13,17,15,11,07,03
// Teensy I/O            # 07,06,20,21,04,05,19,08
// Teensy I/O            #  7, 6, 4,23,22, 5,19, 8 last known working
// RP2040 I/O            #  5, 4, 2, 9, 8, 3, 7, 6
// RP2040 I/O            #  5, 4, 6, 9, 8, 3, 7, 2 last known working (beim umbauen drähte vertauscht doh!)
int Col_IO[matrix_cols] = X210_COL_IO;


// TrackPoint Variables
typedef struct {
  boolean enabled;
  boolean error;
  bool    initiated;    // flag to store if the initialization was completed successfully
  char    mstat;        // trackpoint status reg = Y overflow, X overflow, Y sign bit, X sign bit, Always 1, Middle Btn, Right Btn, Left Btn
  char    mx;           // trackpoint x movement = 8 data bits. The sign bit is in the status register to 
                        // make a 9 bit 2's complement value. Left to right on the trackpoint gives a positive value. 
  char    my;           // trackpoint y movement also 8 bits plus sign. trackpoint movement away from the user gives a positive value.
  boolean over_flow;    // set if x or y movement values are bad due to overflow
  uint8_t buttons;      // buttons pressed (lower 3 bits from mstat) 
  uint8_t buttons_old;  // last state of the buttons
  bool    scrolled;     // flag to store if we scrolled after middle-btn-down to omit thw middle-btn-click release
  unsigned long watchdog; // watchdog timer
} TP_;
TP_ TP {STARTUP_TRACKPOINT,0,0,0,0,0,0,0,0,0,millis()};


//Keyboard Variables
typedef struct {
  boolean Fn_pressed; // Initialize Fn key to HIGH = "not pressed"
  KeyReport state;
  int NUMLOCK_ON;
  int SCRLOCK_ON;
  int CAPSLOCK_ON;
  bool disable_winkey;
  bool disable_caps;
} KB_;
KB_ KB {HIGH, {0,0,{0,0,0,0,0,0}},-1,-1,-1,0,0};

#define FN_PRESSED (KB.Fn_pressed == LOW)

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

//keyboard functions
void keyboard_send_combo(bool pressed, uint8_t modifiers, uint8_t key1, uint8_t key2 = 0, uint8_t key3 = 0);
void key_click(uint16_t keycode);                  //presses and releases a key
void key_press(uint16_t keycode, uint8_t pressed); //wrapper to automatically select the right function from the following ones
void load_slot(uint8_t key);                       //regular keys
void clear_slot(uint8_t key);
void clear_all_slots();
void press_consumer(uint16_t keycode);             //consumer: media, volume, ...
void clear_consumer();
void press_system(uint16_t keycode);               //system: sleep, shutdown...
void clear_system();
void load_mod(uint8_t m_key);                      //modifier: strg,shift,alt,win,....
void clear_mod(uint8_t m_key);

void Keyboard_send(KeyReport &state);
void Keyboard_set_modifier(uint8_t mod);
void Keyboard_set_key(uint8_t index, uint8_t keycode);

//control of keyboard-states, also used as confirmation via blinking
void numlock_toggle();
void numlock_blink(long ms);
void capslock_toggle();
void capslock_blink(long ms);
void scrlk_toggle();
void scrlk_blink(long ms); //trough we don't have a led for that


// Trackpoint 
void trackpoint_init();
void trackpoint_reset();
void trackpoint_fix();
char trackp_read(void);
void trackp_write(char send_data);
void trackpoint_set_error();


/*** Support Functions ***/
void go_z(int pin);
void go_pu(int pin);
void go_0(int pin);
void go_1(int pin);
void go_0z(int pin, int state);

/*** Debug ***/
bool DEBUG_OUTPUT = STARTUP_DEBUG_OUT;
void debugPrint(const char str[]);
void debugPrintln(const char str[]);
void debugPressed(bool pressed);

void RebootUF2() {
  Serial.println("Rebooting to UF2 mode...");
  delay(100);
  // Parameter 1: LED-Pin für Aktivitätsanzeige (0 = aus)
  // Parameter 2: Deaktivierung von Interfaces (0 = Standard)
  reset_usb_boot(0, 0);   
}




// Main Structure
void setupRP();
void setupSerial();
void setupMouse();
void setupKeyboard();

void handleRP();
void handleMouse();
void handleKeyboard();
void handleKeyboardReport();
void handleKeyboardKeystrokes();
void handleSerial();


// Main Setup
void setup() {
  setupRP();
  setupSerial();
  setupKeyboard();
  setupMouse();
}

// Main Loop
void loop() {
  handleRP();
  handleSerial();
  handleKeyboard();
  ec_task();
  //maybe this can be lowered further, but should not be zero (both at 5ms starts to get unreliable)
  delay(5); // let voltages and everthing settle
  handleMouse();
  ec_task();
  delay(5); // let voltages and everthing settle back
}


void setupRP() {
  rp2040.enableDoubleResetBootloader();
  ec_init();
  settings_load();
}

void setupSerial() {
  Serial.begin();
  delay(1000); //wait 100ms to be able to catch this on the console
  Serial.println("\r\n\r\nThinkPad RP2040 Keyboard!");
  Serial.println("Type HELP for more.");
  Serial.println("Type DOFF to disable debug-output.");
}

void setupMouse() {
  TP_Mouse.begin();
  trackpoint_fix();
}


void setupKeyboard() {
  //Keyboard output to host init
  TP_Keyboard.begin(KeyboardLayout_de_DE);
 
  //Matrix Pins init
  for (int a = 0; a < matrix_cols; a++) {  // loop thru all column pins 
    go_pu(Col_IO[a]); // set each column pin as an input with a pullup
  }
  for (int b = 0; b < matrix_rows; b++) {  // loop thru all row pins 
    go_z(Row_IO[b]); // set each row pin as a floating output
  }  
  // Pull up the Fn "Hotkey" input so it can be read. If key pressed, it will be low.
  go_pu(HOTKEY);

  //disable Numlock on BootUp
  handleKeyboardReport();
  if(KB.NUMLOCK_ON) {
    numlock_toggle();
  }
}



//Minimal Input-Protocol via Serial :)
void printHelp() {
  Serial.println("HELP:\r\n\
  Current Commands:\r\n\
  BOOT - reboot into bootloader for flashing          Fn+ThinkVANTAGE\r\n\
  DOFF - Debug Off (only state changes and specials)  Fn+ESC (toggle)\r\n\
  DON  - Debug On  (mouse and key changes)            Fn+ESC (toggle)\r\n\
  HELP - this help\r\n\
  TPR  - Trackpoint Reset                             Fn+F9\r\n\
  TPI  - Trackpoint Init                              Fn+F10\r\n\
  TPER - Trackpoint Disable Error only                Fn+F11\r\n\
  TPE  - Trackpoint Enable/Disable                    Fn+F8\r\n\
  STAT - Current Status\r\n\
  SWAP - scambia Fn e Ctrl sinistro (salvato)         Fn+Ctrl tenuti 2 s\r\n\
  LIGHT- ThinkLight on/off tramite l'EC               Fn+PgUp\r\n\
  JIS  - impara i 5 tasti extra della tastiera giapponese\r\n\
  JISX - cancella i tasti JIS appresi\r\n\
  ");
}
void printStatus() {
  static const char* YES = "yes";
  static const char* NO  = "no";
  static const char* ENA = "enabled";
  static const char* DIS = "disabled";
  static const char* ON  = "ON";
  static const char* OFF = "off";

  Serial.printf("STATUS:\r\n\
  TrackPoint.enabled:   %s\r\n\
  TrackPoint.error:     %s\r\n\
  TrackPoint.initiated: %s\r\n\
  Keyboard.WinKey:      %s\r\n\
  Keyboard.CapsKey:     %s\r\n\
  Keyboard.NumLock:     %s\r\n\
  Keyboard.CapsLock:    %s\r\n\
  Keyboard.ScrollLock:  %s\r\n\
  "
  , (TP.enabled?YES:NO)
  , (TP.error?YES:NO)
  , (TP.initiated?YES:NO)
  , (KB.disable_winkey?DIS:ENA)
  , (KB.disable_caps?DIS:ENA)
  , (KB.NUMLOCK_ON?ON:OFF)
  , (KB.CAPSLOCK_ON?ON:OFF)
  , (KB.SCRLOCK_ON?ON:OFF)
  );
  Serial.printf("  X210Ai.SwapFnCtrl:   %s\r\n", (SWAP_FN_CTRL?ON:OFF));
  printJis();
}


void handleRP() {
  if(BOOTSEL) {
    Serial.println("BOOTSEL pressed");
  }
}


#define SERIAL_BUFF_LEN 10 //must be able to hold the longest possible command to receive incl. null-terminator
char serialbuff[SERIAL_BUFF_LEN] = {'\0', '\0', '\0', '\0', '\0', '\0', '\0', '\0', '\0', '\0'};
char serialbuffi = 0;

void handleSerial() {
  if (Serial.available()) {
    char ch = Serial.read();
    if(ch != '\n' && ch != '\r') {
      if(serialbuffi < SERIAL_BUFF_LEN-1) {
        if(ch == 0x7F || ch == 0x08) { //Backspace pressed, delete key frmo buffer
          serialbuffi--;
          serialbuff[serialbuffi] = 0;
        } else {
          serialbuff[serialbuffi] = ch;
          serialbuffi++;
        }
        Serial.write(ch);
      } else {
        Serial.write('-');
      }
    } else {
      Serial.print("\r\n");

      if (0 == strcmp(serialbuff,"BOOT")) {
        RebootUF2();
      }
      else if (0 == strcmp(serialbuff, "DOFF")) {
        DEBUG_OUTPUT = 0;
        Serial.println("Debug Off");
      }
      else if (0 == strcmp(serialbuff, "DON")) {
        DEBUG_OUTPUT = 1;
        Serial.println("Debug On");
      }
      else if (0 == strcmp(serialbuff, "HELP")) {
        printHelp();
      }
      else if (0 == strcmp(serialbuff, "STAT")) {
        printStatus();
      }
      else if (0 == strcmp(serialbuff, "TPI")) {
        trackpoint_init();
      }
      else if (0 == strcmp(serialbuff, "TPE")) {
        TP.enabled = HIGH;
      }
      else if (0 == strcmp(serialbuff, "TPER")) {
        TP.error = LOW;
      }
      else if (0 == strcmp(serialbuff, "TPR")) {
        trackpoint_reset();
      }
      else if (0 == strcmp(serialbuff, "SWAP")) {
        swap_toggle();
      }
      else if (0 == strcmp(serialbuff, "LIGHT")) {
        ec_thinklight();
      }
      else if (0 == strcmp(serialbuff, "JIS")) {
        jis_learn = 1;
        Serial.printf("Premi il tasto JIS 1: %s (ESC = salta)\r\n", jis_name[0]);
      }
      else if (0 == strcmp(serialbuff, "JISX")) {
        for (int i = 0; i < JIS_KEYS; i++) {
          jis_pos[i][0] = 0xFF;
          jis_pos[i][1] = 0xFF;
        }
        settings_save();
        Serial.println("Tasti JIS cancellati.");
      }
      else {
        Serial.print("Unknown Command '");
        Serial.print(serialbuff);
        Serial.println("'! Type HELP");
      }

      //clear buffer
      while(serialbuffi > 0) {
        serialbuffi--;
        serialbuff[serialbuffi] = '\0';
      }
    }
  }
}

void handleMouseBtn(bool pressed, uint8_t btn);
void handleMouse() {

  // Read TrackPoint
  if (TP.enabled && !TP.error) { // check if trackpoint is working and enabled
    // poll the trackpoint for new movement data
    TP.over_flow = 0; // assume no overflow until status is received 
    trackp_write(0xeb);  // request data
    if (trackp_read() != 0xfa) { // verify correct ack byte  
      trackpoint_set_error("HandleMouse: Bad Ack (Request Data)");
    }
    TP.mstat = trackp_read(); // save into status variable
    TP.mx = trackp_read(); // save into x variable
    TP.my = trackp_read(); // save into y variable
    if (((0x80 & TP.mstat) == 0x80) || ((0x40 & TP.mstat) == 0x40))  {   // x or y overflow bits set?
      TP.over_flow = 1; // set the overflow flag
    }   
    // change the x data from 9 bit to 8 bit 2's complement
    TP.mx >>= 1; // convert to 7 bits of data by dividing by 2
    TP.mx &= 0x7f; // don't allow sign extension
    if ((0x10 & TP.mstat) == 0x10) {   // move the sign into the 8th bit position
      TP.mx |= 0x80;        
    } 
    // change the y data from 9 bit to 8 bit 2's complement and then take the 2's complement 
    // because y movement on ps/2 format is opposite of touchpad.move function
    TP.my >>= 1; // convert to 7 bits of data by dividing by 2
    TP.my &= 0x7f; // don't allow sign extension
    if ((0x20 & TP.mstat) == 0x20) {   // move the sign into 
      TP.my |= 0x80;                   // the 8th bit position
    } 
    TP.my = (~TP.my + 0x01); // change the sign of y data by taking the 2's complement (invert and add 1)
    // zero out mx and my if over_flow or error is set
    if (TP.over_flow || TP.error) { 
      debugPrint("TrackPoint: HandleMouse: Ignore bad/overflowing data\r\n");
      TP.mx = 0x00;       // data is garbage so zero it out
      TP.my = 0x00;
    }
  } 

  
  // Process TrackPoint

  if (TP.enabled && !TP.error) { // check if trackpoint is working and enabled
    TP.buttons = (0x07 & TP.mstat);
  
    // check for movement
    if ((TP.mx != 0x00) || (TP.my != 0x00)) {

      if(DEBUG_OUTPUT) {
        //only output when non-zero, otherwise this would spam the serial
        Serial.printf("TP: Status: 0x%X, Pos:(%d,%d)\r\n", TP.mstat, TP.mx, TP.my);
      }

      if((TP.buttons & MOUSE_MIDDLE) || FN_PRESSED) {
        int8_t scrollX=0,scrollY=0;
        int8_t absX,absY;
        absX = abs((int8_t)TP.mx);
        absY = abs((int8_t)TP.my);
        
        const int8_t SCROLL_MAX = 16;

        if(absX > 4) {
          scrollX = max(1,min((absX-4)/4, SCROLL_MAX));
          if((int8_t)TP.mx < 0) {
            scrollX = 0 - scrollX;
          }
        }
        if(absY > 4) {
          scrollY = max(1,min((absY-4)/4, SCROLL_MAX));
          if((int8_t)TP.my > 0) { //note: y in inverted
            scrollY = 0 - scrollY;
          }
        }
        if(scrollY != 0 || scrollX != 0) {
          //when movement while middle click is down
          TP.buttons_old = TP.buttons; //"consume" this middle button, so it is not send down below
          TP.scrolled = true;
          TP_Mouse.move(0, 0, scrollY, scrollX);
          if(DEBUG_OUTPUT) {
            //only output when non-zero, otherwise this would spam the serial to much
            Serial.printf("Mouse.Scroll: %d, %d\r\n", scrollY, scrollX);
          }
          delay(30); //limit scroll speed
        }
      } else {
        int x = ((int8_t)TP.mx);
        int y = ((int8_t)TP.my);
        TP_Mouse.move(x, y, 0,0);
        if(DEBUG_OUTPUT) {
          Serial.printf("Mouse.Move: %d,%d\r\n", x, y);
        }
      }
    }


    int btnNr = 31 - __builtin_clz(TP.buttons);

    if (TP.buttons_old != TP.buttons) {
      // if physical buttons have changed
      if(DEBUG_OUTPUT) {
        Serial.printf("TP.Btn: 0x%X (%s,%s,%s)\r\n", TP.buttons, \
          ((TP.buttons&MOUSE_LEFT)?"LEFT":""), \
          ((TP.buttons&MOUSE_MIDDLE)?"MIDDLE":""), \
          ((TP.buttons&MOUSE_RIGHT)?"RIGHT":"")
        );
      }

      // Middle Button Release
      if(!(TP.buttons     & MOUSE_MIDDLE) 
       && (TP.buttons_old & MOUSE_MIDDLE)) {
        if (!TP.scrolled) {
          //if not scrolled: emit a full click now (btn down is allways held back for middle-btn to allow scrolling)
          handleMouseBtn(true,   MOUSE_MIDDLE);
          delay(10);
          handleMouseBtn(false,  MOUSE_MIDDLE);
        } else {
          //since we have scrolled, we don't send a middle-btn-click
          TP.scrolled = false; //reset scrolled state after btn-release
        }
      }

      // respond to normal clicks
      handleMouseBtn(TP.buttons & MOUSE_LEFT,  MOUSE_LEFT);
      handleMouseBtn(TP.buttons & MOUSE_RIGHT, MOUSE_RIGHT);

      //save last button state
      TP.buttons_old = TP.buttons;
    }
  }
}

void handleMouseBtn(bool pressed, uint8_t btn) {
  char debugstr[100];
  int btnNr = 31 - __builtin_clz(btn);
  if(FN_PRESSED) {
    if(DEBUG_OUTPUT) {
      sprintf(debugstr, "Mouse: Fn+Btn%d => Btn%d", btnNr, btnNr+3);
      Serial.println(debugstr);
    }
    btn  <<= 3; //shift btn-code by 3 bits when fn is pressed, that makes btn1 becomes btn4, btn2 becomes btn5, etc. btn4,5 are normally used for back and forward
    btnNr += 3;
  }
  if (pressed) {
    if (!TP_Mouse.isPressed(btn)) {
      TP_Mouse.press(btn);
      if(DEBUG_OUTPUT) {
        sprintf(debugstr, "Mouse: Fn+Btn%d.Down", btnNr);
        Serial.println(debugstr);
      }
    }
  } else {
    if (TP_Mouse.isPressed(btn)) {
      TP_Mouse.release(btn);
      if(DEBUG_OUTPUT) {
        sprintf(debugstr, "Mouse: Fn+Btn%d.Up", btnNr);
        Serial.println(debugstr);
      }
    }
  }
}


void handleKeyboard() {
  handleKeyboardReport();
  handleKeyboardKeystrokes();
}


void handleKeyboardReport() {
  //Handle changes on Num-Lock-State
  if(Keyboard2::numLockActive != KB.NUMLOCK_ON || KB.NUMLOCK_ON == -1) {
    KB.NUMLOCK_ON = Keyboard2::numLockActive;
    Serial.print("NumLock: ");
    Serial.println(KB.NUMLOCK_ON?"ON":"OFF");
  }
  if(Keyboard2::scrollLockActive != KB.SCRLOCK_ON || KB.SCRLOCK_ON == -1) {
    KB.SCRLOCK_ON = Keyboard2::scrollLockActive;
    Serial.print("ScrollLock: ");
    Serial.println(KB.SCRLOCK_ON?"ON":"OFF");
  }
  if(Keyboard2::capsLockActive != KB.CAPSLOCK_ON || KB.CAPSLOCK_ON == -1) {
    KB.CAPSLOCK_ON = Keyboard2::capsLockActive;
    Serial.print("CapsLock: ");
    Serial.println(KB.CAPSLOCK_ON?"ON":"OFF");
  }
}

void handleKeyboardKeystrokes() {
  // Read the Fn key (aka Hotkey) which is not part of the key matrix
  int old_fn = KB.Fn_pressed;
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
  
  if(KB.Fn_pressed != old_fn && KB.Fn_pressed == HIGH) { //Fn Released: Release all modifier which might have been set while held down
    if(KB.state.modifiers != 0) {
      Keyboard_set_modifier(0);
      Keyboard_send(KB.state);
      debugPrint("Released all Modifiers\r\n");
    }
    debugPrint("FN-Release\r\n");
  }
  if(KB.Fn_pressed != old_fn && KB.Fn_pressed == LOW) {
    debugPrint("FN-Keydown\r\n");
  }

  // Scan keyboard matrix with an outer loop that drives each row low and an inner loop that reads every column (with pull ups).
  // The routine looks at each key's present state (by reading the column input pin) and also the previous state from the last scan
  // that was 30msec ago. The status of a key that was just pressed or just released is sent over USB and the state is saved in the old_key matrix. 
  // The keyboard keys will read as logic low if they are pressed (negative logic).
  // The old_key matrix also uses negative logic (low=pressed). 

  for (int x = 0; x < matrix_rows; x++) {   // loop thru the rows
    go_0(Row_IO[x]); // Activate Row (send it low)
    delayMicroseconds(50); // give the row time to go low and settle out

    for (int y = 0; y < matrix_cols; y++) {   // loop thru the columns
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
          Serial.printf("Matrix[%d,%d] = %d\r\n",x,y,pressed);
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
            Serial.printf("JIS %d = matrice[%d,%d]\r\n", jis_learn, x, y);
            jis_learn++;
            if (jis_learn > JIS_KEYS) {
              jis_learn = 0;
              settings_save();
              Serial.println("Tasti JIS salvati.");
            } else {
              Serial.printf("Premi il tasto JIS %d: %s (ESC = salta)\r\n", jis_learn, jis_name[jis_learn - 1]);
            }
            continue;
          } else if (normalCode == KEY_ESC) {
            Serial.printf("JIS %d saltato\r\n", jis_learn);
            jis_learn++;
            if (jis_learn > JIS_KEYS) {
              jis_learn = 0;
              settings_save();
              Serial.println("Tasti JIS salvati.");
            } else {
              Serial.printf("Premi il tasto JIS %d: %s (ESC = salta)\r\n", jis_learn, jis_name[jis_learn - 1]);
            }
            continue;
          }
        }

        
        // Fn Overlay
        if(FN_PRESSED) {

          //Hardcoded Fn-Makros first 

          //Fn+ThinkVantage = Reboot RP2040 (X210Ai: solo se tenuti premuti 3 s)
          if(fnCode == KEY_THINK_VANTAGE) {
            Serial.printf("Fn+ThinkVantage %s\r\n", (pressed?"pressed (tieni 3 s per UF2)":"released"));
            tv_armed = pressed;
            tv_down_ms = millis();
          }

          //Fn+PgUp = ThinkLight: lo gestisce l'EC della scheda madre, glielo inviamo noi
          else if(fnCode == KEY_THINKLIGHT) {
            Serial.printf("Fn+PgUp %s (ThinkLight via EC)\r\n", (pressed?"pressed":"released"));
            if(pressed) {
              ec_thinklight();
            }
          }

          //Fn+ESC = Toggle DebugMode
          else if(normalCode == KEY_ESC) {
            Serial.printf("Fn+ESC %s\r\n", (pressed?"pressed":"released"));
            if(pressed) {
              DEBUG_OUTPUT = !DEBUG_OUTPUT;
              Serial.print("Toggle-Debug-Mode: ");
              Serial.println((DEBUG_OUTPUT?"ON":"OFF"));
            }
          }

          //Fn+MUTE = Mute Microphone via Win + Alt + K
          else if(fnCode == KEY_MUTE) {
            Serial.printf("Fn+MUTE %s (emulate Win+Alt+K)\r\n", (pressed?"pressed":"released"));
            keyboard_send_combo(pressed, (uint8_t)(MODIFIERKEY_GUI|MODIFIERKEY_LEFT_ALT), (uint8_t)KEY_K);
          }

          //Fn+ScrollLock = NumLock-Key
          else if(fnCode == KEY_SCROLL_LOCK) {
            Serial.printf("Fn+ScrlLck %s (toggle NumLock)\r\n", (pressed?"pressed":"released"));
            key_press(KEY_NUM_LOCK, pressed);
          }

          //Fn+F2 = Lock Workstation : Emulate Win+L
          else if(normalCode == KEY_F2) { 
            Serial.printf("Fn+F2 %s (emulate Win+L)\r\n", (pressed?"pressed":"released"));
            keyboard_send_combo(pressed, (uint8_t)MODIFIERKEY_GUI, (uint8_t)KEY_L);
          }

          //Fn+F5 = Wireless: tasto radio HID (modalita' aereo su Windows, rfkill su Linux)
          else if(normalCode == KEY_F5) {
            Serial.printf("Fn+F5 %s (radio/airplane mode)\r\n", (pressed?"pressed":"released"));
            TP_Keyboard.radioButton(pressed);
          }

          //Fn+F7 = Toggle internal/external screen : Emulate Win+P
          else if(normalCode == KEY_F7) {
            Serial.printf("Fn+F7 %s (emulate Win+P)\r\n", (pressed?"pressed":"released"));
            keyboard_send_combo(pressed, (uint8_t)MODIFIERKEY_GUI, (uint8_t)KEY_P);
          }

          //Fn+F8 = TrackPoint/Touchpad-Key : Toggle TrackPoint on/off/restart ps/2
          else if(normalCode == KEY_F8) {
            Serial.printf("Fn+F8 %s (TrackPoint toggle)\r\n", (pressed?"pressed":"released"));
            if(pressed) {
              Serial.printf("TrackPoint %s\r\n", (TP.enabled?"disabled":"enabled"));
              TP.enabled = !TP.enabled; // invert the state of the trackpoint enable flag to turn it on or off
              debugPrint("Blink Numlock as confirmation.\r\n");
              numlock_blink(250);
              //try init if never initiated successfully
              if(TP.enabled) {
                if(!TP.initiated) {
                  debugPrint("TrackPoint: Never initiated, try it now...\r\n");
                  trackpoint_init();
                } else {
                  if(TP.error == LOW) {
                    debugPrint("TrackPoint: allready initiated (just enabled again).\r\n");
                    handleMouse();
                    delay(5);
                  }
                  if(TP.error == HIGH) {
                    Serial.printf("TrackPoint: Did not respond, trying to fix...\r\n");
                    trackpoint_fix();
                    if(TP.error == HIGH) {
                      Serial.printf("TrackPoint: Failed to fix :( disabled TrackPoint for now\r\n");
                      TP.enabled = false;
                    }
                  }
                  if(TP.error == LOW) {
                    Serial.printf("TrackPoint: Responded successfully.\r\n");
                  }
                }
              }
            }
          }
          //Fn+F9 = TrackPoint Debug Reset
          else if(normalCode == KEY_F9) {
            Serial.printf("Fn+F9 %s (TrackPoint reset)\r\n", (pressed?"pressed":"released"));
            if(pressed) {
              trackpoint_reset();
            }
          }
          //Fn+F10 = TrackPoint Debug Init
          else if(normalCode == KEY_F10) {
            Serial.printf("Fn+F10 %s (TrackPoint init)\r\n", (pressed?"pressed":"released"));
            if(pressed) {
              TP.error = LOW;
              trackpoint_init();
            }
          }
          //Fn+F11 = TrackPoint Debug toggle without init
          else if(normalCode == KEY_F11) {
            Serial.printf("Fn+F11 %s (TrackPoint toggle error)\r\n", (pressed?"pressed":"released"));
            if(pressed) {
              TP.error = !TP.error; // invert the state of the trackpoint error flag to turn it on or off
              Serial.printf("TrackPoint error:%s", (TP.error?"set\r\n":"unset\r\n"));
            }
          }
          //Fn+GUI = Toggle Win-Key-Enabled
          else if(normalCode == MODIFIERKEY_GUI) {
            Serial.printf("Fn+GUI %s (Windows-Key-Enabled)\r\n", (pressed?"pressed":"released"));
            if(pressed) {
              KB.disable_winkey = !KB.disable_winkey; // invert the state
              Serial.printf("Disable GUI-Key: %s", (KB.disable_winkey?"active\r\n":"inactive\r\n"));
              debugPrint("DoubleBlink Numlock as confirmation.\r\n");
              numlock_blink(150);
              delay(50);
              numlock_blink(150);
            }
          }
          //Fn+CAPS = Toggle Caps-Key-Enabled
          else if(normalCode == KEY_CAPS_LOCK) {
            Serial.printf("Fn+CAPS %s (Caps-Allowed)\r\n", (pressed?"pressed":"released"));
            if(pressed) {
              KB.disable_caps = !KB.disable_caps; // invert the state
              Serial.printf("Disable CAPS-Key: %s", (KB.disable_caps?"active\r\n":"inactive\r\n"));
              debugPrint("DoubleBlink Capslock as confirmation.\r\n");
              bool caps_state = KB.CAPSLOCK_ON; //save state before messing with it
              capslock_blink(150);
              delay(50);
              capslock_blink(150);            
              if(caps_state && KB.disable_caps) {
                //if on, disable
                capslock_toggle();
              }
            }
          }
          
          //Normal KeyStroke defined by overlay-Keymap
          else {
            //if numlock is active and fn is pressed and the key is a keypad_key
            if(KB.NUMLOCK_ON && numlock[x][y] >= KEYPAD_FIRST_CODE && numlock[x][y] <= KEYPAD_LAST_CODE) {
              //we press the key from the normal-layer as fn overrides our numlock-layer
              key_press(normalCode, pressed);
            }
            //otherwise if the fn-overlay contains a key, just press it
            else if (fnCode != 0) {
              key_press(fnCode, pressed);
            }
          }
        }
        //end-fn

        // check if normal key exists at this location in the array (a non-zero value)
        else if (normalCode != 0) {
          // if numlock is active, replace key with numlock-table (the numlock-table should hold all entries from the normal-table plus changes, but it never undefines a key, so we do not need to check it )
          // but only if fn is not held down. so you can use fn to override active num-lock
          if(KB.NUMLOCK_ON && !FN_PRESSED) {
            normalCode = numlock[x][y];
          }
          key_press(normalCode, pressed);
        }
        // X210Ai: posizione vuota della mappa: tasto JIS appreso oppure tasto sconosciuto
        else {
          uint16_t jc = extra_key_at(x, y);
          if (jc != 0) {
            key_press(jc, pressed);
          } else if (pressed) {
            Serial.printf("Tasto senza codice: matrice[%d,%d] (usa JIS per assegnarlo)\r\n", x, y);
          }
        }

      }
    }
    go_z(Row_IO[x]); // De-activate Row (send it to hi-z)
  }

  // X210Ai: Fn+ThinkVantage tenuti 3 s
  if (tv_armed && FN_PRESSED && !old_key[TV_ROW][TV_COL] && millis() - tv_down_ms >= TV_HOLD_MS) {
    RebootUF2();
  }
}





// *****************Functions for Keyboard*****************************

//Send a Key-Combo with modifier and up to 3 normal keys set
void keyboard_send_combo(bool pressed, uint8_t modifiers, uint8_t key1, uint8_t key2, uint8_t key3) {
  if(pressed) {
    Keyboard_set_modifier(modifiers);
    clear_all_slots();
    load_slot(key1);
    load_slot(key2);
    load_slot(key3);
    Keyboard_send(KB.state);
  } else {
    //this still keeps the modifiers set, they will be release on fn-release
    clear_all_slots();
    Keyboard_send(KB.state);
  }
}

void key_click(uint16_t keycode) {
  key_press(keycode, 0xFF);
  delay(5);
  key_press(keycode, false);
}

void key_press(uint16_t keycode, uint8_t pressed) {
  if(pressed && pressed != 0xFF && keycode == MODIFIERKEY_GUI && KB.disable_winkey) {
    Serial.printf("GUI-Key: Ignored (disabled) - Press Fn+GUI to enable again!\r\n");
    numlock_blink(50);
    return;
  }
  if(pressed && pressed != 0xFF && keycode == KEY_CAPS_LOCK && KB.disable_caps) {
    Serial.printf("CAPS-Key: Ignored (disabled) - Press Fn+CAPS to enable again!\r\n");
    capslock_blink(50);
    return;
  }

  // Modifier Keys
  if(keycode >= 0xE000 && keycode < 0xE100) {
    if(pressed)  load_mod(keycode); // function reads which modifier key is pressed and loads it into the appropriate mod_... variable   
    if(!pressed) clear_mod(keycode); // function reads which modifier key was released and loads 0 into the appropriate mod_... variable
    Keyboard_send(KB.state); // function sends all mod's over usb including the one that just released
  }
  // Reserved
  else if(keycode >= 0xE100 && keycode < 0xE200) {
    //reserved
  }
  // System key section. Note PJRC states that these should be sent with Keyboard.press function. 
  else if(keycode >= 0xE200 && keycode < 0xE400) {

    if(pressed)  press_system(keycode - 0xE200);
    if(!pressed) clear_system();
  }
  // Consumer/Media key section. Note PJRC states that these should be sent with Keyboard.press function. 
  else if(keycode >= 0xE400 && keycode < 0xF000) {

    if(pressed)  press_consumer(keycode - 0xE400);
    if(!pressed) clear_consumer();
  }
  
  // Normal Keys via Slots
  else {
    if(pressed)  load_slot(keycode); //update first available slot with key name from numlock matrix
    if(!pressed) clear_slot(keycode); //clear the slot that contains the normal key name
    Keyboard_send(KB.state); // send all slots over USB including the key that was just released 
  } 
}

// Function to load the key name into the first available slot
void load_slot(uint8_t keycode) {
  for(uint8_t i = 0; i < 6; i++) {
    if(KB.state.keys[i] == 0 || KB.state.keys[i] == keycode) {
      KB.state.keys[i] = keycode;
      return;
    }
  }
  //not returned above, all slots full
  //set all 6 key-codes to 0x01 to indicate key-overflow
  KeyReport errState = {0,0,{1,1,1,1,1,1}};
  Keyboard_send(errState);
  if(DEBUG_OUTPUT) {
    Serial.println("6KRO Overflow");
  }
}

// Function to clear the slot that contains the key name
void clear_slot(uint8_t keycode) {
  for(uint8_t i = 0; i < 6; i++) {
    if(KB.state.keys[i] == keycode) {
      KB.state.keys[i] = 0;
      return;
    }
  }
}
void clear_all_slots() {
  for(uint8_t i = 0; i < 6; i++) {
    KB.state.keys[i] = 0;
  }
}

// Functions to load/clear the modifier key name into the appropriate mod variable
void load_mod(uint8_t m_key) {
  KB.state.modifiers |= m_key;
}
void clear_mod(uint8_t m_key) {
  KB.state.modifiers &= ~m_key;
}

void keyboard_serial_print_modifiers() {
    Serial.printf("Modifiers: [%s,%s,%s,%s,%s,%s,%s]\r\n", 
      (KB.state.modifiers&MODIFIERKEY_LEFT_SHIFT?"LSHIFT":""), 
      (KB.state.modifiers&MODIFIERKEY_RIGHT_SHIFT?"RSHIFT":""), 
      (KB.state.modifiers&MODIFIERKEY_LEFT_CTRL?"LCTRL":""), 
      (KB.state.modifiers&MODIFIERKEY_RIGHT_CTRL?"RCTRL":""), 
      (KB.state.modifiers&MODIFIERKEY_LEFT_ALT?"LALT":""), 
      (KB.state.modifiers&MODIFIERKEY_RIGHT_ALT?"RALT":""),
      (KB.state.modifiers&MODIFIERKEY_GUI?"GUI":"")
    );
}

void Keyboard_set_modifier(uint8_t mod) {
  KB.state.modifiers = mod;

  if(DEBUG_OUTPUT) {
    keyboard_serial_print_modifiers();
  }
}


void Keyboard_send(KeyReport &state) {
  if(DEBUG_OUTPUT) {
    Serial.printf("Keyboard.sendReport(\r\n\
  Normals:   [0x%X,0x%X,0x%X,0x%X,0x%X,0x%X],\r\n",
      state.keys[0], state.keys[1], state.keys[2], state.keys[3], state.keys[4], state.keys[5]);
    keyboard_serial_print_modifiers();      
  }

  TP_Keyboard.sendReport(&state);
}

void Keyboard_set_key(uint8_t index, uint8_t keycode) {
  KB.state.keys[index] = keycode;
  if(DEBUG_OUTPUT) {
    Serial.printf("Set-Key(%d): 0x%X\r\n", index, keycode);
  }
}



void press_consumer(uint16_t keycode) {
  TP_Keyboard.consumerPress(keycode); // send media key press
  if(DEBUG_OUTPUT) {
    Serial.printf("Keyboard.consumerPress: 0x%X\r\n", keycode);
  }
}

void clear_consumer() {
  TP_Keyboard.consumerRelease(); // send media key press
  debugPrint("Keyboard.consumerRelease\r\n");
}


void press_system(uint16_t keycode) {
  keycode -= 0x80;
  TP_Keyboard.systemPress(keycode); // send system key press
  if(DEBUG_OUTPUT) {
    Serial.printf("Keyboard.systemPress: 0x%X\r\n", keycode);
  }
}
void clear_system() {
  TP_Keyboard.systemRelease(); // send system key press
  debugPrint("Keyboard.systemRelease\r\n");
}

void numlock_toggle() {
  key_click(KEY_NUM_LOCK);
  delay(1);
  handleKeyboardReport();
}
void scrlock_toggle() {
  key_click(KEY_SCROLL_LOCK);
  delay(1);
  handleKeyboardReport();
}
void capslock_toggle() {
  key_click(KEY_CAPS_LOCK);
  delay(1);
  handleKeyboardReport();
}

void numlock_blink(long delay_ms) {
  numlock_toggle();
  delay(delay_ms);
  numlock_toggle();
}
void scrlock_blink(long delay_ms) {
  scrlock_toggle();
  delay(delay_ms);
  scrlock_toggle();
}
void capslock_blink(long delay_ms) {
  capslock_toggle();
  delay(delay_ms);
  capslock_toggle();
}



/*** Support Functions ***/

// Function to set a pin to high impedance (acts like open drain output)
void go_z(int pin)
{
  pinMode(pin, INPUT);
  digitalWrite(pin, HIGH);
}
//
// Function to set a pin as an input with a pullup
void go_pu(int pin)
{
  pinMode(pin, INPUT_PULLUP);
  digitalWrite(pin, HIGH);
}
//
// Function to send a pin to a logic low
void go_0(int pin)
{
  pinMode(pin, OUTPUT);
  digitalWrite(pin, LOW);
}
//
// Function to send a pin to a logic high
void go_1(int pin)
{
  pinMode(pin, OUTPUT);
  digitalWrite(pin, HIGH);
}
// Function to send a pin to a logic value supplied as parameter
void go_0z(int pin, int state)
{
  if(state) go_1(pin); else go_0(pin);
}



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


void debugPrint(const char str[]) {
  if(DEBUG_OUTPUT) {
    Serial.print(str);
  }
}
void debugPressed(bool pressed) {
  debugPrint(pressed ? " pressed\r\n":"released\r\n");
}




//
// *****************Functions for Trackpoint***************************

void trackpoint_set_error(const char errstr[]) {
  if(DEBUG_OUTPUT) {
    if(strlen(errstr) > 0) {
      Serial.printf("TrackPoint: Error (%s)\r\n", errstr);
    } else {
      Serial.println("TrackPoint: Error!");
    }
  }
  TP.error = HIGH; // set error flag 
}

void trackp_watchdog_reset() {
  TP.watchdog = millis();  
}
void trackp_wait_for_clock(uint8_t state, const char* errstr) {
  delayMicroseconds(1); // delay to let the clock settle out
  while (digitalRead(TP_CLOCK_PIN) == state) { // loop until the clock goes low
    if ((millis()-TP.watchdog) >= TP_PS2_TIMEOUT_MS) { //check for infinite loop
      if(DEBUG_OUTPUT)Serial.printf("Watchdog Timeout: %d\r\n", ((millis()-TP.watchdog)) );
      trackpoint_set_error(errstr);
      break; // break out of infinite loop
    }
  }
}
bool trackp_read_bit() {
  delayMicroseconds(1); // delay to let the clock settle out
  return digitalRead(TP_DATA_PIN);
}
void trackp_expect_data_bit(bool state, const char* errstr) {
  int dat = trackp_read_bit();
  if(dat != state) {
    if(DEBUG_OUTPUT)Serial.printf("Expected: %d, got %d\r\n", state, dat);
    trackpoint_set_error(errstr);
  }
}
void trackp_expect_data_byte(char expectedbyte, const char* errstr) {
  if (trackp_read() != expectedbyte) { // verify basic assurance test passed
    trackpoint_set_error(errstr);
  }
}
void trackp_write_expect_ack(char writebyte, const char* errstr) {
  trackp_write(writebyte);
  char dat = trackp_read();
  if (dat != 0xFA) { // verify correct ack byte
    if(DEBUG_OUTPUT)Serial.printf("Expected: 0x%X(ACK), got 0x%X\r\n", 0xFA, dat);
    trackpoint_set_error(errstr);
  }
}

void trackp_write(char send_data)  
{
  trackp_watchdog_reset();
  char odd_parity = 0;    // clear parity bit count
  go_z(TP_CLOCK_PIN);     // Enable the bus by floating the clock 
  go_z(TP_DATA_PIN);      //   and data
  delayMicroseconds(250); // wait before requesting the bus
  go_0(TP_CLOCK_PIN);     // Send the Clock line low to request to transmit data
  delayMicroseconds(100); // wait for 100 microseconds per bus spec
  go_0(TP_DATA_PIN);      // Send the Data line low (the start bit)
  delayMicroseconds(1);   //
  go_z(TP_CLOCK_PIN);     // Release the Clock line so it is pulled high
  
  if(!TP.error) trackp_wait_for_clock(HIGH, "No Answer (write#1)");
  for (int j=0; j<8; j++) {        // send the 8 bits of send_data 
    odd_parity += (send_data & 1); // keep running total of 1's sent
    go_0z(TP_DATA_PIN, (send_data & 1));
    if(!TP.error) trackp_wait_for_clock(LOW, "No Answer (write#2)");
    if(!TP.error) trackp_wait_for_clock(HIGH, "No Answer (write#3)");
    send_data = send_data >> 1;    // shift data right by 1 to prepare for next loop
  }
  // send the parity bit
  go_0z(TP_DATA_PIN, !(odd_parity & 1)); // already odd so send a 0 to TP
  if(!TP.error) trackp_wait_for_clock(LOW, "No Answer (write#4)");
  if(!TP.error) trackp_wait_for_clock(HIGH, "No Answer (write#5)");
  go_z(TP_DATA_PIN);     // Release the Data line so it goes high as the stop bit
  delayMicroseconds(80); // testing shows delay needed here is at least 40us 
  if(!TP.error) trackp_wait_for_clock(HIGH, "No Answer (write#6)");
  if(!TP.error) trackp_expect_data_bit(LOW, "Ack-Bit not low (write#7)");

  while ((digitalRead(TP_CLOCK_PIN) == LOW) || (digitalRead(TP_DATA_PIN) == LOW)) { // loop if clock or data are low => wait until both are high
    if ((millis()-TP.watchdog) >= TP_PS2_TIMEOUT_MS) { //check for infinite loop
      trackpoint_set_error("No Answer (write#8)");
      break; // break out of infinite loop
    }
  }
  // Inhibit the bus so the tp only talks when we're listening
  go_0(TP_CLOCK_PIN);
}

//
// Function to get a byte of data from the trackpoint
//
char trackp_read(void)
{
  trackp_watchdog_reset();
  char rcv_data = 0; // initialize to zero
  char mask = 1; // shift a 1 across the 8 bits to select where to load the data
  char rcv_parity = 0; // count the ones received
  go_z(TP_CLOCK_PIN); // release the clock
  go_z(TP_DATA_PIN); // release the data
  delayMicroseconds(5); // delay to let clock go high

  if(!TP.error) trackp_wait_for_clock(HIGH, "No Answer (read#1)");
  if(!TP.error) trackp_expect_data_bit(LOW, "No Start Bit (read#2)");
  if(!TP.error) trackp_wait_for_clock(LOW, "No Answer (read#3)");
  for (int k=0; k<8; k++) {  
    if(!TP.error) trackp_wait_for_clock(HIGH, "No Answer (read#4)");
    if (trackp_read_bit()) { // check if data is high
      rcv_data = rcv_data | mask; // set the appropriate bit in the rcv data
      rcv_parity++; // increment the parity bit counter
    }
    mask = mask << 1;
    if(!TP.error) trackp_wait_for_clock(LOW, "No Answer (read#5)");
  }
  // receive parity
  if(!TP.error) trackp_wait_for_clock(HIGH, "No Answer (read#6)");
  if (trackp_read_bit())  { // check if received parity is high
    rcv_parity++; // increment the parity bit counter
  }
  rcv_parity = rcv_parity & 1; // mask off all bits except the lsb
  if (rcv_parity == 0) { // check for bad (even) parity
    trackpoint_set_error("Bad Parity (read#7)");
  } 
  if(!TP.error) trackp_wait_for_clock(LOW, "No Answer (read#8)");  
  if(!TP.error) trackp_wait_for_clock(HIGH, "No Answer (read#9)"); // stop bit
  if(!TP.error) trackp_expect_data_bit(HIGH, "Bad Stop-Bit (read#10)");
  if(!TP.error) trackp_wait_for_clock(LOW, "No Answer (read#11)");
  
  // Inhibit the bus so the tp only talks when we're listening
  go_0(TP_CLOCK_PIN);
  return rcv_data; // pass the received data back
}

void trackpoint_reset()
{
  debugPrint("TrackPoint: Reset\r\n");
  go_1(TP_RESET_PIN);
  delay(10);
  go_0(TP_RESET_PIN);
}

void trackpoint_fix()
{
  if(TP.enabled) { //if enabled at start
    trackpoint_reset(); //trigger reset-line
    delay(50);
    trackpoint_init(); // reset trackpoint via ps/2 command, then set it's resolution and put it in remote mode 
    if (TP.error) {
      debugPrint("TrackPoint: Init Failed, retry after .5 seconds\r\n");
      delay(500); // wait 1/2 sec
      trackpoint_init(); // try one more time to initialize the trackpoint
      if (TP.error) {
        debugPrint("TrackPoint: Init Failed two times. giving up.\r\n");
        TP.enabled = false;
      }
    }  
  }
}

void trackpoint_init()
{
  debugPrint("TrackPoint: Init Routine\r\n");

  TP.error = LOW; // start with no error
  go_z(TP_CLOCK_PIN); // float the clock and data to trackpoint
  go_z(TP_DATA_PIN);
  //  Sending reset command to trackpoint
  if(!TP.error) trackp_write_expect_ack(0xFF, "Bad Ack (Init#1)");
  delay(400); // wait 1000ms so tp can run its self diagnostic //400ms seems to be enough
  if(!TP.error) trackp_expect_data_byte(0xAA, "Bad Comm (init#2)");
  if(!TP.error) trackp_expect_data_byte(0x00, "Bad Comm (init#3)");
  if(!TP.error) trackp_write_expect_ack(0xF5, "Bad Ack (Init#4)");       //  Send touchpad disable code 
  // Load Mode Byte with 00 using the following special sequence from page 38.
  // Send set resolution to 0 four times followed by a set sample rate to 0x14
  if(!TP.error) trackp_write_expect_ack(0xE8, "Bad Ack (Resolution#1)"); // #1 set resolution
  if(!TP.error) trackp_write_expect_ack(0x01, "Bad Ack (Resolution#2)");
  if(!TP.error) trackp_write_expect_ack(0xE8, "Bad Ack (Resolution#3)"); // #2
  if(!TP.error) trackp_write_expect_ack(0x00, "Bad Ack (Resolution#4)");
  if(!TP.error) trackp_write_expect_ack(0xE8, "Bad Ack (Resolution#5)"); // #3
  if(!TP.error) trackp_write_expect_ack(0x00, "Bad Ack (Resolution#6)");
  if(!TP.error) trackp_write_expect_ack(0xE8, "Bad Ack (Resolution#7)"); // #4
  if(!TP.error) trackp_write_expect_ack(0x00, "Bad Ack (Resolution#8)");
  if(!TP.error) trackp_write_expect_ack(0xF3, "Bad Ack (Sample Rate#1)");// Set sample rate
  if(!TP.error) trackp_write_expect_ack(0x14, "Bad Ack (Sample Rate#2)");
  if(!TP.error) trackp_write_expect_ack(0xE8, "Bad Ack (Resolution#3)"); // set the resolution 
  if(!TP.error) trackp_write_expect_ack(0x03, "Bad Ack (Resolution#4)");
  if(!TP.error) trackp_write_expect_ack(0xF3, "Bad Ack (Sample Rate#4)");// set the sample rate 
  if(!TP.error) trackp_write_expect_ack(0x28, "Bad Ack (Sample Rate#6)");
  if(!TP.error) trackp_write_expect_ack(0xF0, "Bad Ack (Remote Mode)");  // Sending remote mode code so the touchpad will send data only when polled
  if(!TP.error) trackp_write_expect_ack(0xF4, "Bad Ack (Enable)");       // Sending touchpad enable code (needed for Elan touchpads)
  if(!TP.error) {
    Serial.println("TrackPoint: PS/2 INITIATED :)\r\n");
    TP.initiated = true;
  }
}

