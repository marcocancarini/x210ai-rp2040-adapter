/*  fishgod's ThinkPad RP2040 Keyboard (2026)
    Mouse2.h

    Replacment for the Philhower-Core Keyboard.h Arduino file
    - added function for horizontal scrolling
    - defined MOUSE_BTN4 .. MOUSE_BTN8
    Defines global TP_Mouse object

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
#error Mouse2 is not compatible with Adafruit TinyUSB
#endif

#include <HID_Mouse.h>

//Btn 1-3 allready defined in HID_Mouse.h
/*
#define MOUSE_LEFT   (1<<0) //Mouse Button 1
#define MOUSE_RIGHT  (1<<1) //Mouse Button 2
#define MOUSE_MIDDLE (1<<2) //Mouse Button 3
*/
#define MOUSE_BACK   (1<<3) //Mouse Button 4: zurück
#define MOUSE_FORE   (1<<4) //Mouse Button 5: vor

#define MOUSE_BTN4   (1<<3) //Mouse Button 4: zurück
#define MOUSE_BTN5   (1<<4) //Mouse Button 5: vor
#define MOUSE_BTN6   (1<<5) //Mouse Button 6: 
#define MOUSE_BTN7   (1<<6) //Mouse Button 7: 
#define MOUSE_BTN8   (1<<7) //Mouse Button 8: 


class Mouse2 : public HID_Mouse {
public:
    Mouse2(void);
    //we need to refine everything from original Mouse.h as we cannot access die private _id
    void begin() override;
    void end() override;
    virtual void move(int x, int y, signed char wheel = 0) override;
    //everthing the same except this new function:
    void move(int x, int y, signed char wheelY, signed char wheelX);

protected:
    uint8_t _id;
};
extern Mouse2 TP_Mouse;
