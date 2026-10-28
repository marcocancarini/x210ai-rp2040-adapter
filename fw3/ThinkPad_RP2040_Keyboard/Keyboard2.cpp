/*  fishgod's ThinkPad RP2040 Keyboard (2026)
    Keyboard2.cpp
    
    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
*/

#include "Keyboard2.h"
#include <USB.h>

#include <Keyboard.h>
#include <tusb.h>
#include <class/hid/hid_device.h>

#include <pico/unique_id.h>

char unique_id_str[17]; // 16 Zeichen für 64-Bit Hex + Null-Terminator

void read_pico_id() {
    pico_unique_board_id_t board_id;
    pico_get_unique_board_id(&board_id);

    // Wandelt die 8 Bytes der ID in einen Hex-String um
    for (int i = 0; i < 8; i++) {
        sprintf(&unique_id_str[i * 2], "%02X", board_id.id[i]);
    }
}


#define TUD_HID_REPORT_DESC_SYSTEM_CONTROL_KB2(...) \
  HID_USAGE_PAGE ( HID_USAGE_PAGE_DESKTOP           )        ,\
  HID_USAGE      ( HID_USAGE_DESKTOP_SYSTEM_CONTROL )        ,\
  HID_COLLECTION ( HID_COLLECTION_APPLICATION       )        ,\
    /* Report ID if any */\
    __VA_ARGS__ \
    /* 1 byte system control */ \
    HID_LOGICAL_MIN  ( 0x81                                ) ,\
    HID_LOGICAL_MAX  ( 0x8F                                ) ,\
    HID_USAGE_MIN    ( 0x81                                ) ,\
    HID_USAGE_MAX    ( 0x8F                                ) ,\
    HID_REPORT_COUNT ( 1                                   ) ,\
    HID_REPORT_SIZE  ( 8                                   ) ,\
    HID_INPUT        ( HID_DATA | HID_ARRAY | HID_ABSOLUTE ) ,\
  HID_COLLECTION_END \


// X210Ai: Wireless Radio Controls (airplane mode). Il Report ID deve stare all'offset 6:
// il core arduino-pico lo riscrive in base all'ordine di registrazione.
#define TUD_HID_REPORT_DESC_RADIO_X210(...) \
  HID_USAGE_PAGE ( HID_USAGE_PAGE_DESKTOP     ) ,\
  HID_USAGE      ( 0x0C                       ) ,\
  HID_COLLECTION ( HID_COLLECTION_APPLICATION ) ,\
    __VA_ARGS__ \
    HID_LOGICAL_MIN  ( 0 ) ,\
    HID_LOGICAL_MAX  ( 1 ) ,\
    HID_USAGE        ( 0xC6 ) ,\
    HID_REPORT_COUNT ( 1 ) ,\
    HID_REPORT_SIZE  ( 1 ) ,\
    HID_INPUT        ( HID_DATA | HID_VARIABLE | HID_RELATIVE ) ,\
    HID_REPORT_SIZE  ( 7 ) ,\
    HID_INPUT        ( HID_CONSTANT ) ,\
  HID_COLLECTION_END \

//needed to copy this
static const uint8_t desc_hid_report_keyboard[] = { TUD_HID_REPORT_DESC_KEYBOARD(HID_REPORT_ID(1))};
static const uint8_t desc_hid_report_consumer[] = { TUD_HID_REPORT_DESC_CONSUMER(HID_REPORT_ID(2))};
//added
static const uint8_t desc_hid_report_system[] = { TUD_HID_REPORT_DESC_SYSTEM_CONTROL_KB2(HID_REPORT_ID(3)) };
static const uint8_t desc_hid_report_radio[] = { TUD_HID_REPORT_DESC_RADIO_X210(HID_REPORT_ID(4)) };

uint16_t Custom_VID = 0xDEAD;
uint16_t Custom_PID = 0xABBA;
char manufacturer[] = "fish.systems";
char device[]       = "ThinkPad RP2040 Keyboard";


extern bool DEBUG_OUTPUT;

volatile bool Keyboard2::numLockActive = false;
volatile bool Keyboard2::scrollLockActive = false;
volatile bool Keyboard2::capsLockActive = false;

void Keyboard2_LEDHandler(bool numlock, bool capslock, bool scrolllock, bool compose, bool kana, void *cbData) {
  Keyboard2::numLockActive = numlock;
  Keyboard2::scrollLockActive = scrolllock;
  Keyboard2::capsLockActive = capslock;
}

Keyboard2::Keyboard2(void) 
  : Keyboard_() {
    // Base class clears the members we care about
}

void Keyboard2::begin(const uint8_t *layout) {
  if (_running) {
    return;
  }
  USB.disconnect();
  delay(300);
  
    
  _id = USB.registerHIDDevice(desc_hid_report_keyboard, sizeof(desc_hid_report_keyboard), 10, 0x0001);
  _idConsumer = USB.registerHIDDevice(desc_hid_report_consumer, sizeof(desc_hid_report_consumer), 11, 0x0000);
  
  //added
  _idSystem = USB.registerHIDDevice(desc_hid_report_system, sizeof(desc_hid_report_system), 12, 0x0002);
  _idRadio = USB.registerHIDDevice(desc_hid_report_radio, sizeof(desc_hid_report_radio), 13, 0x0004);
  
  USB.setVIDPID(Custom_VID, Custom_PID);
  USB.setManufacturer(manufacturer);
  USB.setProduct(device);
  read_pico_id();
  USB.setSerialNumber(unique_id_str);

  USB.connect();
  HID_Keyboard::begin(layout);
  
  //we hijack the original Keyboard-Class LED-Callback, as the assembly from Keyboard-lib allready created
  //a global tud_hid_set_report_cb()-callback-function that we cannot redefine. this function is tied to the
  //global Keyboard-instance but since the keyboard-report is rather global it doesn't matter if the callback
  //is tied a an uninitialized Keyboard-instance as long as it just calls our function
  Keyboard._ledCB = Keyboard2_LEDHandler;
}

void Keyboard2::end() {
    USB.disconnect();
    USB.unregisterHIDDevice(_id);
    USB.unregisterHIDDevice(_idConsumer);
    USB.unregisterHIDDevice(_idSystem);
    USB.unregisterHIDDevice(_idRadio);
    USB.connect();
    HID_Keyboard::end();
}

void Keyboard2::sendReport(KeyReport* keys) {
    Keyboard_::sendReport(keys);
}

void Keyboard2::sendConsumerReport(uint16_t key) {
    Keyboard_::sendConsumerReport(key);
}


void Keyboard2::sendSystemReport(uint8_t key) {
    if (!_running) {
        return;
    }
    CoreMutex m(&USB.mutex);
    tud_task();
    if (USB.HIDReady()) {
        tud_hid_report(USB.findHIDReportID(_idSystem), &key, sizeof(key));
    }
    tud_task();
}

//System Functions added

void Keyboard2::systemPress(uint8_t k) {
  sendSystemReport(k);
}

void Keyboard2::systemRelease() {
  sendSystemReport(0);
}

void Keyboard2::radioButton(bool pressed) {
    if (!_running) {
        return;
    }
    uint8_t v = pressed ? 1 : 0;
    CoreMutex m(&USB.mutex);
    tud_task();
    if (USB.HIDReady()) {
        tud_hid_report(USB.findHIDReportID(_idRadio), &v, sizeof(v));
    }
    tud_task();
}

Keyboard2 TP_Keyboard;
