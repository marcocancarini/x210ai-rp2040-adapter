/*  fishgod's ThinkPad RP2040 Keyboard (2026)
    Keyboard2.h
    
    Extension to the Philhower-Core Keyboard.h Arduino file
    - allowes to send systemkeys
    - exposes the keyboard-leds as direct to query variables
    - low level sendReport access
    - defines own VID/PID and unique-id based on rp2040
    Defines global TP_Keyboard object

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

#pragma once

#ifdef USE_TINYUSB
#error Keyboard2 is not compatible with Adafruit TinyUSB
#endif

#include <Keyboard.h>

#include <tusb-hid.h>
#include <HID_Keyboard.h>


class Keyboard2 : public Keyboard_ {
public:
  void begin(const uint8_t *layout = KeyboardLayout_en_US) override;
  void end() override;

  volatile static bool numLockActive;
  volatile static bool scrollLockActive;
  volatile static bool capsLockActive;
  
  //overrides needed to make them public
  virtual void sendReport(KeyReport* keys) override;
  virtual void sendConsumerReport(uint16_t key) override;
  //added  
  virtual void sendSystemReport(uint8_t key);
  //keep from HID_Keyboard:
  //size_t consumerPress(uint16_t k);
  //size_t consumerRelease();
  //added
  void systemPress(uint8_t k);
  void systemRelease();
  //X210Ai: tasto radio (modalita' aereo) - Generic Desktop 0x0C/0xC6, Windows e Linux (KEY_RFKILL)
  void radioButton(bool pressed);

protected:
    //keep from Keyboard:
    //uint8_t _id;
    //uint8_t _idConsumer;
    //added:
    uint8_t _idSystem;
    uint8_t _idRadio;

public:
    Keyboard2(void);
};

extern Keyboard2 TP_Keyboard;