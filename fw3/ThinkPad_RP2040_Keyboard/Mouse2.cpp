/*  fishgod's ThinkPad RP2040 Keyboard (2026)
    Mouse2.cpp
    
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

#include "Mouse2.h"

#include <USB.h>

#include "tusb.h"
#include <tusb-hid.h>
#include "class/hid/hid_device.h"

static const uint8_t desc_hid_report_mouse2[] = { TUD_HID_REPORT_DESC_MOUSE(HID_REPORT_ID(1)) };

Mouse2::Mouse2(void)
  : HID_Mouse() {
}

void Mouse2::begin() {
    if (_running) {
        return;
    }
    USB.disconnect();
    _id = USB.registerHIDDevice(desc_hid_report_mouse2, sizeof(desc_hid_report_mouse2), 20, 0x0002);
    USB.connect();
    HID_Mouse::begin();
}

void Mouse2::end() {
    if (_running) {
        USB.disconnect();
        USB.unregisterHIDDevice(_id);
        USB.connect();
    }
    HID_Mouse::end();
}

void Mouse2::move(int x, int y, signed char wheel) {
    if (!_running) {
        return;
    }
    CoreMutex m(&USB.mutex);
    tud_task();
    if (USB.HIDReady()) {
        tud_hid_mouse_report(USB.findHIDReportID(_id), _buttons, limit_xy(x), limit_xy(y), wheel, 0);
    }
    tud_task();
}

void Mouse2::move(int x, int y, signed char wheelY, signed char wheelX) {
    if (!_running) {
        return;
    }
    CoreMutex m(&USB.mutex);
    tud_task();
    if (USB.HIDReady()) {
        tud_hid_mouse_report(USB.findHIDReportID(_id), _buttons, limit_xy(x), limit_xy(y), wheelY, wheelX);
    }
    tud_task();
}

Mouse2 TP_Mouse;
