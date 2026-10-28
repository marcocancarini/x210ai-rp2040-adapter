/*  fishgod's ThinkPad RP2040 Keyboard (2026)
    keycodes.h

    Key definitions mostly taken from Teensyduino, some keycodes are added.
    The keycodes here are all defined as 16bit values like in Teensyduino-lib
    where this project is ported from.
    With the upper most bits denominating the key-type (regular,consumer,system)
    allowing to store different types of keys as a single value in our matrices.


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

// Keycodes-Ranges:
//     32 - 127     ASCII direct (U+0020 to U+007F) <-- uses layout
//    128 - 0xC1FF  Unicode direct (U+0080 to U+C1FF) <-- uses layout
// 0xC200 - 0xDFFF  Unicode UTF8 packed (U+0080 to U+07FF) <-- uses layout
// 0xE000 - 0xE0FF  Modifier key (bitmap, 8 keys, shift/ctrl/alt/gui)
// 0xE1..           Reserved/unused
// 0xE200 - 0xE2FF  System key (HID usage code, within usage page 1)
// 0xE400 - 0xE7FF  Media/Consumer key (HID usage code, within usage page 12)
// 0xF000 - 0xFFFF  Normal key (HID usage code, within usage page 7)

//Keys defined by HID_Keyboard.h are not what we want, we need to redefine them all for our needs
//so lets undefine them here 


#undef KEY_BACKSPACE
#undef KEY_TAB
#undef KEY_MENU
#undef KEY_ESC
#undef KEY_INSERT
#undef KEY_DELETE
#undef KEY_PAGE_UP
#undef KEY_PAGE_DOWN
#undef KEY_HOME
#undef KEY_END
#undef KEY_CAPS_LOCK
#undef KEY_SCROLL_LOCK
#undef KEY_PAUSE
#undef KEY_NUM_LOCK
#undef KEY_PRINT_SCREEN
#undef KEY_F1
#undef KEY_F2
#undef KEY_F3
#undef KEY_F4
#undef KEY_F5
#undef KEY_F6
#undef KEY_F7
#undef KEY_F8
#undef KEY_F9
#undef KEY_F10
#undef KEY_F11
#undef KEY_F12
#undef KEY_F13
#undef KEY_F14
#undef KEY_F15
#undef KEY_F16
#undef KEY_F17
#undef KEY_F18
#undef KEY_F19
#undef KEY_F20
#undef KEY_F21
#undef KEY_F22
#undef KEY_F23
#undef KEY_F24
#undef KEY_POWER

#undef KEY_AL_CONSUMER_CONTROL_CONFIGURATION

#undef KEY_AC_STOP          //^
#undef KEY_AC_HOME          //1
#undef KEY_AL_LOCAL_BROWSER //2
#undef KEY_AL_EMAIL_READER  //3
#undef KEY_AC_SEARCH        //4
#undef KEY_AC_REFRESH       //5
#undef KEY_AC_BOOKMARKS     //6
#undef KEY_AL_CALCULATOR    //ThinkVantage
#undef KEY_AC_BACK          //otherwise
#undef KEY_AC_FORWARD       //otherwise




/*
AL Calculator	0x0192	�ffnet den Windows-Rechner.
AL Email Reader	0x018A	�ffnet das Standard-E-Mail-Programm.
AL Browser	0x0194	�ffnet den Standard-Webbrowser.
AC Search	0x0221	�ffnet die Windows-Suche.
AC Home		0x0223	Geht im Browser zur Startseite.
AC Back / Forward	0x0224 / 0x0225	Browser-Navigation (Zur�ck/Vor).
*/


#define KEY_AL_CONSUMER_CONTROL_CONFIGURATION  ( 0x0183 | 0xE400 )

#define KEY_AL_WORD_PROCESSOR                  ( 0x0184 | 0xE400 )
#define KEY_AL_TEXT_EDITOR                     ( 0x0185 | 0xE400 )
#define KEY_AL_SPREADSHEET                     ( 0x0186 | 0xE400 )
#define KEY_AL_GRAPHICS_EDITOR                 ( 0x0187 | 0xE400 )
#define KEY_AL_PRESENTATION_APP                ( 0x0188 | 0xE400 )

#define KEY_AC_SEARCH                          ( 0x0221 | 0xE400 )
#define KEY_AC_HOME                            ( 0x0223 | 0xE400 )
#define KEY_AC_BACK                            ( 0x0224 | 0xE400 )
#define KEY_AC_FORWARD                         ( 0x0225 | 0xE400 )
#define KEY_AC_STOP                            ( 0x0226 | 0xE400 )
#define KEY_AC_REFRESH                         ( 0x0227 | 0xE400 )
#define KEY_AC_BOOKMARKS                       ( 0x022A | 0xE400 )

#define KEY_AL_EMAIL_READER                    ( 0x018A | 0xE400 )
#define KEY_AL_CALCULATOR                      ( 0x0192 | 0xE400 )
#define KEY_AL_LOCAL_BROWSER                   ( 0x0194 | 0xE400 )



//own definitions missing from the pjrc headers

#define KEY_POWER               ( 102  | 0xF000 )
#define KEYPAD_EQUAL            ( 103  | 0xF000 )

#define KEY_BRIGHTNESS_INC      ( 0x6F | 0xE400 )//working on windows
#define KEY_BRIGHTNESS_DEC      ( 0x70 | 0xE400 )//working on windows
#define KEY_BACKLIGHT_TOGGLE    ( 0x72 | 0xE400 )

#define KEY_SYSTEM_HIBERNATE    ( 0x81 | 0xE200 )//working on windows

#define KEY_SYSTEM_UNDOCK       ( 0xA1 | 0xE200 )
#define KEY_SYSTEM_PROJECT      ( 0xB5 | 0xE200 )

#define KEY_AC_ZOOM             ( 0x22F | 0xE400 )
#define KEY_AL_SCREEN_SAVER     ( 0x1B1 | 0xE400 )
#define KEY_AL_WIFI_STATUS      ( 0x1AD | 0xE400 )
#define KEY_AL_TERMINAL_LOCK    ( 0x19E | 0xE400 )

#define KEY_THINK_VANTAGE	KEY_AL_CALCULATOR

#define KEY_THINKLIGHT      		( 0x0001 | 0xE100 ) //use reserved range here 
// X210Ai: tasti aggiuntivi della tastiera giapponese (HID Keyboard page 0x87-0x8B)
#define KEY_INTERNATIONAL1      ( 0x87 | 0xF000 ) // ro  \\ _
#define KEY_INTERNATIONAL2      ( 0x88 | 0xF000 ) // katakana/hiragana
#define KEY_INTERNATIONAL3      ( 0x89 | 0xF000 ) // yen
#define KEY_INTERNATIONAL4      ( 0x8A | 0xF000 ) // henkan
#define KEY_INTERNATIONAL5      ( 0x8B | 0xF000 ) // muhenkan



/* Teensyduino Core Library
 * http://www.pjrc.com/teensy/
 * Copyright (c) 2023 PJRC.COM, LLC.
 *
 * taken codes from Teensyduino
 */

// Explanation why 16 bits and the purpose of upper 8 bits of these defines
// https://forum.pjrc.com/threads/71874?p=318669&viewfull=1#post318669

#define KEY_NON_US_BS           ( 100  | 0xF000 )

#define MODIFIERKEY_CTRL        ( 0x01 | 0xE000 )
#define MODIFIERKEY_SHIFT       ( 0x02 | 0xE000 )
#define MODIFIERKEY_ALT         ( 0x04 | 0xE000 )
#define MODIFIERKEY_GUI         ( 0x08 | 0xE000 )
#define MODIFIERKEY_LEFT_CTRL   ( 0x01 | 0xE000 )
#define MODIFIERKEY_LEFT_SHIFT  ( 0x02 | 0xE000 )
#define MODIFIERKEY_LEFT_ALT    ( 0x04 | 0xE000 )
#define MODIFIERKEY_LEFT_GUI    ( 0x08 | 0xE000 )
#define MODIFIERKEY_RIGHT_CTRL  ( 0x10 | 0xE000 )
#define MODIFIERKEY_RIGHT_SHIFT ( 0x20 | 0xE000 )
#define MODIFIERKEY_RIGHT_ALT   ( 0x40 | 0xE000 )
#define MODIFIERKEY_RIGHT_GUI   ( 0x80 | 0xE000 )

#define KEY_SYSTEM_POWER_DOWN   ( 0x81 | 0xE200 )
#define KEY_SYSTEM_SLEEP        ( 0x82 | 0xE200 )
#define KEY_SYSTEM_WAKE_UP      ( 0x83 | 0xE200 )

#define KEY_MEDIA_POWER         ( 0x30 | 0xE400 )
#define KEY_MEDIA_RESET         ( 0x31 | 0xE400 )
#define KEY_MEDIA_SLEEP         ( 0x32 | 0xE400 )

#define KEY_MEDIA_MEDIA         ( 0x40 | 0xE400 )

/*
79 Keyboard Brightness Increment [42] OSC 15.22
7A Keyboard Brightness Decrement [42] OSC 15.22
7B Keyboard Backlight Set Level [42] LC 15.22
7C Keyboard Backlight OOC [42] OOC 15.22
7D Keyboard Backlight Set Minimum [42] OSC 15.22
7E Keyboard Backlight Set Maximum [42] OSC 15.22
7F Keyboard Backlight Auto [42] OOC 15.22
*/

#define KEY_MEDIA_PLAY          ( 0xB0 | 0xE400 )
#define KEY_MEDIA_PAUSE         ( 0xB1 | 0xE400 )
#define KEY_MEDIA_RECORD        ( 0xB2 | 0xE400 )
#define KEY_MEDIA_FAST_FORWARD  ( 0xB3 | 0xE400 )
#define KEY_MEDIA_REWIND        ( 0xB4 | 0xE400 )
#define KEY_MEDIA_NEXT_TRACK    ( 0xB5 | 0xE400 )
#define KEY_MEDIA_PREV_TRACK    ( 0xB6 | 0xE400 )
#define KEY_MEDIA_STOP          ( 0xB7 | 0xE400 )
#define KEY_MEDIA_EJECT         ( 0xB8 | 0xE400 )
#define KEY_MEDIA_RANDOM_PLAY   ( 0xB9 | 0xE400 )
#define KEY_MEDIA_PLAY_PAUSE    ( 0xCD | 0xE400 )
#define KEY_MEDIA_PLAY_SKIP     ( 0xCE | 0xE400 )
#define KEY_MEDIA_MUTE          ( 0xE2 | 0xE400 )
#define KEY_MEDIA_VOLUME_INC    ( 0xE9 | 0xE400 )
#define KEY_MEDIA_VOLUME_DEC    ( 0xEA | 0xE400 )


// Software support for these GUI application control keys is spotty.
// For example, GIMP 3.0.4 running on Fedora Linux 41 does respond
// to KEY_GUI_ZOOM_IN & KEY_GUI_ZOOM_OUT, but Final Cut Pro 11.1.1
// running on MacOS 14.7.4 Sonoma ignores them.
#define KEY_GUI_NEW               ( 0x201 | 0xE400 )
#define KEY_GUI_OPEN              ( 0x202 | 0xE400 )
#define KEY_GUI_CLOSE             ( 0x203 | 0xE400 )
#define KEY_GUI_EXIT              ( 0x204 | 0xE400 )
#define KEY_GUI_MAXIMIZE          ( 0x205 | 0xE400 )
#define KEY_GUI_MINIMIZE          ( 0x206 | 0xE400 )
#define KEY_GUI_SAVE              ( 0x207 | 0xE400 )
#define KEY_GUI_PRINT             ( 0x208 | 0xE400 )
#define KEY_GUI_PROPERTIES        ( 0x209 | 0xE400 )
#define KEY_GUI_UNDO              ( 0x21A | 0xE400 )
#define KEY_GUI_COPY              ( 0x21B | 0xE400 )
#define KEY_GUI_CUT               ( 0x21C | 0xE400 )
#define KEY_GUI_PASTE             ( 0x21D | 0xE400 )
#define KEY_GUI_SELECT_ALL        ( 0x21E | 0xE400 )
#define KEY_GUI_FIND              ( 0x21F | 0xE400 )
#define KEY_GUI_FIND_REPLACE      ( 0x220 | 0xE400 )
#define KEY_GUI_SEARCH            ( 0x221 | 0xE400 )
#define KEY_GUI_GO_TO             ( 0x222 | 0xE400 )
#define KEY_GUI_HOME              ( 0x223 | 0xE400 )
#define KEY_GUI_BACK              ( 0x224 | 0xE400 )
#define KEY_GUI_FORWARD           ( 0x225 | 0xE400 )
#define KEY_GUI_STOP              ( 0x226 | 0xE400 )
#define KEY_GUI_REFRESH           ( 0x227 | 0xE400 )
#define KEY_GUI_PREVIOUS_LINK     ( 0x228 | 0xE400 )
#define KEY_GUI_NEXT_LINK         ( 0x209 | 0xE400 )
#define KEY_GUI_BOOKMARKS         ( 0x22A | 0xE400 )
#define KEY_GUI_HISTORY           ( 0x22B | 0xE400 )
#define KEY_GUI_SUBSCRIPTIONS     ( 0x22C | 0xE400 )
#define KEY_GUI_ZOOM_IN           ( 0x22D | 0xE400 )
#define KEY_GUI_ZOOM_OUT          ( 0x22E | 0xE400 )
#define KEY_GUI_FULL_SCREEN_VIEW  ( 0x230 | 0xE400 )
#define KEY_GUI_NORMAL_VIEW       ( 0x231 | 0xE400 )
#define KEY_GUI_VIEW_TOGGLE       ( 0x232 | 0xE400 )
#define KEY_GUI_SCROLL_UP         ( 0x233 | 0xE400 )
#define KEY_GUI_SCROLL_DOWN       ( 0x234 | 0xE400 )
#define KEY_GUI_PAN_LEFT          ( 0x236 | 0xE400 )
#define KEY_GUI_PAN_RIGHT         ( 0x237 | 0xE400 )
#define KEY_GUI_NEW_WINDOW        ( 0x239 | 0xE400 )
#define KEY_GUI_TILE_HORIZONTALLY ( 0x23A | 0xE400 )
#define KEY_GUI_TILE_VERTICALLY   ( 0x23B | 0xE400 )
#define KEY_GUI_FORMAT            ( 0x23C | 0xE400 )
#define KEY_GUI_EDIT              ( 0x23D | 0xE400 )
#define KEY_GUI_BOLD              ( 0x23E | 0xE400 )
#define KEY_GUI_ITALICS           ( 0x23F | 0xE400 )
#define KEY_GUI_UNDERLINE         ( 0x240 | 0xE400 )
#define KEY_GUI_STRIKETHROUGH     ( 0x241 | 0xE400 )
#define KEY_GUI_SUBSCRIPT         ( 0x242 | 0xE400 )
#define KEY_GUI_SUPERSCRIPT       ( 0x243 | 0xE400 )
#define KEY_GUI_ALL_CAPS          ( 0x244 | 0xE400 )
#define KEY_GUI_ROTATE            ( 0x245 | 0xE400 )
#define KEY_GUI_RESIZE            ( 0x246 | 0xE400 )
#define KEY_GUI_FLIP_HORIZONTAL   ( 0x247 | 0xE400 )
#define KEY_GUI_FLIP_VERTICAL     ( 0x248 | 0xE400 )
#define KEY_GUI_MIRROR_HORIZONTAL ( 0x249 | 0xE400 )
#define KEY_GUI_MIRROR_VERTICAL   ( 0x24A | 0xE400 )
#define KEY_GUI_FONT_SELECT       ( 0x24B | 0xE400 )
#define KEY_GUI_FONT_COLOR        ( 0x24C | 0xE400 )
#define KEY_GUI_FONT_SIZE         ( 0x24D | 0xE400 )
#define KEY_GUI_JUSTIFY_LEFT      ( 0x24E | 0xE400 )
#define KEY_GUI_JUSTIFT_CENTER_H  ( 0x24F | 0xE400 )
#define KEY_GUI_JUSTIFY_RIGHT     ( 0x250 | 0xE400 )
#define KEY_GUI_JUSTIFY_BLOCK_H   ( 0x251 | 0xE400 )
#define KEY_GUI_JUSTIFY_TOP       ( 0x252 | 0xE400 )
#define KEY_GUI_JUSTIFY_CENTER_V  ( 0x253 | 0xE400 )
#define KEY_GUI_JUSTIFY_BOTTOM    ( 0x254 | 0xE400 )
#define KEY_GUI_JUSTIFY_BLOCK_V   ( 0x255 | 0xE400 )
#define KEY_GUI_INDENT_DECREASE   ( 0x256 | 0xE400 )
#define KEY_GUI_INDENT_INCREASE   ( 0x257 | 0xE400 )
#define KEY_GUI_NUMBERED_LIST     ( 0x258 | 0xE400 )
#define KEY_GUI_RESTART_NUMBERING ( 0x259 | 0xE400 )
#define KEY_GUI_BULLETED_LIST     ( 0x25A | 0xE400 )
#define KEY_GUI_PROMOTE           ( 0x25B | 0xE400 )
#define KEY_GUI_DEMOTE            ( 0x25C | 0xE400 )
#define KEY_GUI_YES               ( 0x25D | 0xE400 )
#define KEY_GUI_NO                ( 0x25E | 0xE400 )
#define KEY_GUI_CANCEL            ( 0x25F | 0xE400 )
#define KEY_GUI_CATALOG           ( 0x260 | 0xE400 )
#define KEY_GUI_BUY_CHECKOUT      ( 0x261 | 0xE400 )
#define KEY_GUI_ADD_TO_CART       ( 0x262 | 0xE400 )
#define KEY_GUI_EXPAND            ( 0x263 | 0xE400 )
#define KEY_GUI_EXPAND_ALL        ( 0x264 | 0xE400 )
#define KEY_GUI_COLLAPSE          ( 0x265 | 0xE400 )
#define KEY_GUI_COLLAPSE_ALL      ( 0x266 | 0xE400 )
#define KEY_GUI_PRINT_PREVIEW     ( 0x267 | 0xE400 )
#define KEY_GUI_PASTE_SPECIAL     ( 0x268 | 0xE400 )
#define KEY_GUI_INSERT_MODE       ( 0x269 | 0xE400 )
#define KEY_GUI_DELETE            ( 0x26A | 0xE400 )
#define KEY_GUI_LOCK              ( 0x26B | 0xE400 )
#define KEY_GUI_UNLOCK            ( 0x26C | 0xE400 )
#define KEY_GUI_PROTECT           ( 0x26D | 0xE400 )
#define KEY_GUI_UNPROTECT         ( 0x26E | 0xE400 )
#define KEY_GUI_ATTACH_COMMENT    ( 0x26F | 0xE400 )
#define KEY_GUI_DELETE_COMMENT    ( 0x270 | 0xE400 )
#define KEY_GUI_VIEW_COMMENT      ( 0x271 | 0xE400 )
#define KEY_GUI_SELECT_WORD       ( 0x272 | 0xE400 )
#define KEY_GUI_SELECT_SENTENCE   ( 0x273 | 0xE400 )
#define KEY_GUI_SELECT_PARAGRAPH  ( 0x274 | 0xE400 )
#define KEY_GUI_SELECT_COLUMN     ( 0x275 | 0xE400 )
#define KEY_GUI_SELECT_ROW        ( 0x276 | 0xE400 )
#define KEY_GUI_SELECT_TABLE      ( 0x277 | 0xE400 )
#define KEY_GUI_SELECT_OBJECT     ( 0x278 | 0xE400 )
#define KEY_GUI_REDO              ( 0x279 | 0xE400 )
#define KEY_GUI_SORT              ( 0x27A | 0xE400 )
#define KEY_GUI_SORT_ASCENDING    ( 0x27B | 0xE400 )
#define KEY_GUI_SORT_DESCENDING   ( 0x27C | 0xE400 )
#define KEY_GUI_FILTER            ( 0x27D | 0xE400 )
#define KEY_GUI_SET_CLOCK         ( 0x27E | 0xE400 )
#define KEY_GUI_VIEW_CLOCK        ( 0x27F | 0xE400 )
#define KEY_GUI_SELECT_TIME_ZONE  ( 0x280 | 0xE400 )
#define KEY_GUI_EDIT_TIME_ZONES   ( 0x281 | 0xE400 )
#define KEY_GUI_SET_ALARM         ( 0x282 | 0xE400 )
#define KEY_GUI_CLEAR_ALARM       ( 0x283 | 0xE400 )
#define KEY_GUI_SNOOZE_ALARM      ( 0x284 | 0xE400 )
#define KEY_GUI_RESET_ALARM       ( 0x285 | 0xE400 )
#define KEY_GUI_SYNCHRONIZE       ( 0x286 | 0xE400 )
#define KEY_GUI_SEND_RECEIVE      ( 0x287 | 0xE400 )
#define KEY_GUI_SEND_TO           ( 0x288 | 0xE400 )
#define KEY_GUI_REPLY             ( 0x289 | 0xE400 )
#define KEY_GUI_REPLY_ALL         ( 0x28A | 0xE400 )
#define KEY_GUI_FORWARD_MSG       ( 0x28B | 0xE400 )
#define KEY_GUI_SEND              ( 0x28C | 0xE400 )
#define KEY_GUI_ATTACH_FILE       ( 0x28D | 0xE400 )
#define KEY_GUI_UPLOAD            ( 0x28E | 0xE400 )
#define KEY_GUI_DOWNLOAD          ( 0x28F | 0xE400 )
#define KEY_GUI_SET_BORDERS       ( 0x290 | 0xE400 )
#define KEY_GUI_INSERT_ROW        ( 0x291 | 0xE400 )
#define KEY_GUI_INSERT_COLUMN     ( 0x292 | 0xE400 )
#define KEY_GUI_INSERT_FILE       ( 0x293 | 0xE400 )
#define KEY_GUI_INSERT_PICTURE    ( 0x294 | 0xE400 )
#define KEY_GUI_INSERT_OBJECT     ( 0x295 | 0xE400 )
#define KEY_GUI_INSERT_SYMBOL     ( 0x296 | 0xE400 )
#define KEY_GUI_SAVE_AND_CLOSE    ( 0x297 | 0xE400 )
#define KEY_GUI_RENAME            ( 0x298 | 0xE400 )
#define KEY_GUI_MERGE             ( 0x299 | 0xE400 )
#define KEY_GUI_SPLIT             ( 0x27A | 0xE400 )
#define KEY_GUI_DISTRIBUTE_HORIZONTALLY ( 0x29B | 0xE400 )
#define KEY_GUI_DISTRIBUTE_VERTICALLY   ( 0x29C | 0xE400 )



#define KEY_A                   (   4  | 0xF000 )
#define KEY_B                   (   5  | 0xF000 )
#define KEY_C                   (   6  | 0xF000 )
#define KEY_D                   (   7  | 0xF000 )
#define KEY_E                   (   8  | 0xF000 )
#define KEY_F                   (   9  | 0xF000 )
#define KEY_G                   (  10  | 0xF000 )
#define KEY_H                   (  11  | 0xF000 )
#define KEY_I                   (  12  | 0xF000 )
#define KEY_J                   (  13  | 0xF000 )
#define KEY_K                   (  14  | 0xF000 )
#define KEY_L                   (  15  | 0xF000 )
#define KEY_M                   (  16  | 0xF000 )
#define KEY_N                   (  17  | 0xF000 )
#define KEY_O                   (  18  | 0xF000 )
#define KEY_P                   (  19  | 0xF000 )
#define KEY_Q                   (  20  | 0xF000 )
#define KEY_R                   (  21  | 0xF000 )
#define KEY_S                   (  22  | 0xF000 )
#define KEY_T                   (  23  | 0xF000 )
#define KEY_U                   (  24  | 0xF000 )
#define KEY_V                   (  25  | 0xF000 )
#define KEY_W                   (  26  | 0xF000 )
#define KEY_X                   (  27  | 0xF000 )
#define KEY_Y                   (  28  | 0xF000 )
#define KEY_Z                   (  29  | 0xF000 )
#define KEY_1                   (  30  | 0xF000 )
#define KEY_2                   (  31  | 0xF000 )
#define KEY_3                   (  32  | 0xF000 )
#define KEY_4                   (  33  | 0xF000 )
#define KEY_5                   (  34  | 0xF000 )
#define KEY_6                   (  35  | 0xF000 )
#define KEY_7                   (  36  | 0xF000 )
#define KEY_8                   (  37  | 0xF000 )
#define KEY_9                   (  38  | 0xF000 )
#define KEY_0                   (  39  | 0xF000 )
#define KEY_ENTER               (  40  | 0xF000 )
#define KEY_ESC                 (  41  | 0xF000 )
#define KEY_BACKSPACE           (  42  | 0xF000 )
#define KEY_TAB                 (  43  | 0xF000 )
#define KEY_SPACE               (  44  | 0xF000 )
#define KEY_MINUS               (  45  | 0xF000 )
#define KEY_EQUAL               (  46  | 0xF000 )
#define KEY_LEFT_BRACE          (  47  | 0xF000 )
#define KEY_RIGHT_BRACE         (  48  | 0xF000 )
#define KEY_BACKSLASH           (  49  | 0xF000 )
#define KEY_NON_US_NUM          (  50  | 0xF000 )
#define KEY_SEMICOLON           (  51  | 0xF000 )
#define KEY_QUOTE               (  52  | 0xF000 )
#define KEY_TILDE               (  53  | 0xF000 )
#define KEY_COMMA               (  54  | 0xF000 )
#define KEY_PERIOD              (  55  | 0xF000 )
#define KEY_SLASH               (  56  | 0xF000 )
#define KEY_CAPS_LOCK           (  57  | 0xF000 )
#define KEY_F1                  (  58  | 0xF000 )
#define KEY_F2                  (  59  | 0xF000 )
#define KEY_F3                  (  60  | 0xF000 )
#define KEY_F4                  (  61  | 0xF000 )
#define KEY_F5                  (  62  | 0xF000 )
#define KEY_F6                  (  63  | 0xF000 )
#define KEY_F7                  (  64  | 0xF000 )
#define KEY_F8                  (  65  | 0xF000 )
#define KEY_F9                  (  66  | 0xF000 )
#define KEY_F10                 (  67  | 0xF000 )
#define KEY_F11                 (  68  | 0xF000 )
#define KEY_F12                 (  69  | 0xF000 )
#define KEY_PRINT_SCREEN        (  70  | 0xF000 )
#define KEY_SCROLL_LOCK         (  71  | 0xF000 )
#define KEY_PAUSE               (  72  | 0xF000 )
#define KEY_INSERT              (  73  | 0xF000 )
#define KEY_HOME                (  74  | 0xF000 )
#define KEY_PAGE_UP             (  75  | 0xF000 )
#define KEY_DELETE              (  76  | 0xF000 )
#define KEY_END                 (  77  | 0xF000 )
#define KEY_PAGE_DOWN           (  78  | 0xF000 )
#define KEY_RIGHT               (  79  | 0xF000 )
#define KEY_LEFT                (  80  | 0xF000 )
#define KEY_DOWN                (  81  | 0xF000 )
#define KEY_UP                  (  82  | 0xF000 )
#define KEY_NUM_LOCK            (  83  | 0xF000 )
#define KEYPAD_SLASH            (  84  | 0xF000 )
#define KEYPAD_ASTERIX          (  85  | 0xF000 )
#define KEYPAD_MINUS            (  86  | 0xF000 )
#define KEYPAD_PLUS             (  87  | 0xF000 )
#define KEYPAD_ENTER            (  88  | 0xF000 )
#define KEYPAD_1                (  89  | 0xF000 )
#define KEYPAD_2                (  90  | 0xF000 )
#define KEYPAD_3                (  91  | 0xF000 )
#define KEYPAD_4                (  92  | 0xF000 )
#define KEYPAD_5                (  93  | 0xF000 )
#define KEYPAD_6                (  94  | 0xF000 )
#define KEYPAD_7                (  95  | 0xF000 )
#define KEYPAD_8                (  96  | 0xF000 )
#define KEYPAD_9                (  97  | 0xF000 )
#define KEYPAD_0                (  98  | 0xF000 )
#define KEYPAD_PERIOD           (  99  | 0xF000 )
#define KEY_NON_US_BS           ( 100  | 0xF000 )
#define KEY_MENU              	( 101  | 0xF000 )
#define KEY_SYS_REQUEST         ( 0x9A | 0xF000 )
//used to determine if a keycode is a KEYPAD one: (keycode >= KEYPAD_FIRST_CODE && keycode <= KEYPAD_LAST_CODE)
#define KEYPAD_FIRST_CODE        KEYPAD_SLASH
#define KEYPAD_LAST_CODE         KEYPAD_PERIOD

//added upper 12 Fn-Keys
#define KEY_F13                 ( 104  | 0xF000 )
#define KEY_F14                 ( 105  | 0xF000 )
#define KEY_F15                 ( 106  | 0xF000 )
#define KEY_F16                 ( 107  | 0xF000 )
#define KEY_F17                 ( 108  | 0xF000 )
#define KEY_F18                 ( 109  | 0xF000 )
#define KEY_F19                 ( 110  | 0xF000 )
#define KEY_F20                 ( 111  | 0xF000 )
#define KEY_F21                 ( 112  | 0xF000 )
#define KEY_F22                 ( 113  | 0xF000 )
#define KEY_F23                 ( 114  | 0xF000 )
#define KEY_F24                 ( 115  | 0xF000 )
