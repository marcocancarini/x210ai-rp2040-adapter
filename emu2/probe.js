const fs = require('fs');
const { Simulator, USBCDC } = require('rp2040js');
const [uf2Path, cfgPath] = process.argv.slice(2);
const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
const romTxt = fs.readFileSync(__dirname + '/dl/bootrom.ts', 'utf8');
const bootrom = new Uint32Array(romTxt.slice(romTxt.indexOf('[')).match(/0x[0-9a-f]+/gi).map((x) => parseInt(x, 16)));
const sim = new Simulator(); const clock = sim.clock; const mcu = sim.rp2040;
const quiet = { debug() {}, info() {}, warn(c, m) { if (!/Unimplemented|invalid memory/.test(m)) console.log('W', c, m); }, error(c, m) { console.log('E', c, m); } };
mcu.logger = quiet;
let wd = 0; mcu.peripherals[0x40058].onWatchdogTrigger = () => { if (wd++ < 3) console.log('WATCHDOG at', (clock.nanos/1e6).toFixed(1), 'ms PC', (mcu.core.PC>>>0).toString(16)); };
mcu.loadBootrom(bootrom);
const uf2 = fs.readFileSync(uf2Path);
for (let off = 0; off + 512 <= uf2.length; off += 512) { if (uf2.readUInt32LE(off) !== 0x0a324655) continue; const a = uf2.readUInt32LE(off + 12), s = uf2.readUInt32LE(off + 16); mcu.flash.set(uf2.subarray(off + 32, off + 32 + s), a - 0x10000000); }
mcu.flash.set(Uint8Array.from(cfg.eeprom_preset), cfg.eeprom_flash_offset);
mcu.core.PC = 0x10000000;
const cdc = new USBCDC(mcu.usbCtrl);
let serial = ''; cdc.onSerialData = (b) => { serial += Buffer.from(b).toString('latin1'); };
const w = mcu.usbCtrl.onEndpointWrite; const eps = {};
mcu.usbCtrl.onEndpointWrite = (ep, buf) => { eps[ep] = (eps[ep] || 0) + 1; w(ep, buf); };
const CYCLE_NS = 1e9 / 125e6;
function runFor(ms) { const end = clock.nanos + ms * 1e6; while (clock.nanos < end) { if (mcu.core.waiting) { const n = clock.nanosToNextAlarm; clock.tick(Number.isFinite(n) && n > 0 ? Math.min(n, end - clock.nanos + 1) : 1000); } else clock.tick(mcu.core.executeInstruction() * CYCLE_NS); } }
for (const g of [cfg.fn, ...cfg.cols, cfg.tp_clk, cfg.tp_data, cfg.tp_rst]) mcu.gpio[g].setInputValue(true);
const t0 = Date.now();
runFor(4000);
console.log('wall', (Date.now()-t0)/1000, 's; descr', cdc.descriptorsSize, cdc.descriptors.length);
console.log(JSON.stringify(cdc.descriptors));
console.log('eps', JSON.stringify(eps));
console.log('serial', JSON.stringify(serial.slice(0, 400)));
