// Emulazione del firmware X210Ai rev 2.0 su rp2040js con il cablaggio della scheda-ponte.
// Un host USB minimo (USBCDC di rp2040js) enumera il dispositivo: si catturano la seriale
// e i report HID (tastiera, consumer, system, radio) e si verificano tasti, EC, swap, JIS, UF2.
//   node run_fw2.js <firmware.uf2> <cfg.json> <out.json>
const fs = require('fs');
const { Simulator, GPIOPinState, USBCDC } = require('rp2040js');

const [uf2Path, cfgPath, outPath] = process.argv.slice(2);
const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
const romTxt = fs.readFileSync(__dirname + '/dl/bootrom.ts', 'utf8');
const bootrom = new Uint32Array(romTxt.slice(romTxt.indexOf('[')).match(/0x[0-9a-f]+/gi).map((x) => parseInt(x, 16)));

const sim = new Simulator();
const clock = sim.clock;
const mcu = sim.rp2040;
// logger silenzioso (le periferiche non emulate producono milioni di avvisi)
const warnings = {};
mcu.logger = { debug() {}, info() {}, warn(c, m) { const k = c + ': ' + String(m).replace(/0x[0-9a-f]+|\d+/gi, 'N'); warnings[k] = (warnings[k] || 0) + 1; }, error(c, m) { const k = 'ERR ' + c + ': ' + m; warnings[k] = (warnings[k] || 0) + 1; } };
// il watchdog scatta solo con reset_usb_boot (riavvio in UF2): lo registriamo
let watchdog = null;
mcu.peripherals[0x40058].onWatchdogTrigger = () => { if (!watchdog) watchdog = { t_ms: +(clock.nanos / 1e6).toFixed(1), PC: '0x' + (mcu.core.PC >>> 0).toString(16) }; };
mcu.loadBootrom(bootrom);
const uf2 = fs.readFileSync(uf2Path);
for (let off = 0; off + 512 <= uf2.length; off += 512) {
  if (uf2.readUInt32LE(off) !== 0x0a324655) continue;
  const addr = uf2.readUInt32LE(off + 12), size = uf2.readUInt32LE(off + 16);
  if (addr >= 0x10000000 && addr < 0x10000000 + mcu.flash.length) mcu.flash.set(uf2.subarray(off + 32, off + 32 + size), addr - 0x10000000);
}
// EEPROM emulata gia' inizializzata (magic 0x5A, swap spento, nessun tasto JIS)
mcu.flash.set(Uint8Array.from(cfg.eeprom_preset), cfg.eeprom_flash_offset);
mcu.core.PC = 0x10000000;

// ------------------------------------------------------------------ host USB
// L'host si collega dopo Keyboard2::begin() (che scollega e ricollega l'USB per aggiungere l'HID):
// cosi' l'enumerazione vede subito il descrittore completo (CDC + HID).
let cdc = null;
let serial = '';
let usbConnected = false;
let hidIn = -1;
const hid = [];                      // [t_ms, reportId, ...bytes]
function attachHost() {
  cdc = new USBCDC(mcu.usbCtrl);
  cdc.onSerialData = (b) => { serial += Buffer.from(b).toString('latin1'); };
  cdc.onDeviceConnected = () => { usbConnected = true; };
  const cdcWrite = mcu.usbCtrl.onEndpointWrite;
  mcu.usbCtrl.onEndpointWrite = (ep, buf) => {
    if (hidIn < 0 && cdc.descriptorsSize && cdc.descriptors.length === cdc.descriptorsSize) hidIn = findHidIn(cdc.descriptors);
    if (ep === hidIn && ep > 0) hid.push([+(clock.nanos / 1e6).toFixed(3), ...buf]);
    cdcWrite(ep, buf);
  };
  // lettura OUT (host -> dispositivo) solo quando ci sono dati: evita la raffica di pacchetti vuoti
  mcu.usbCtrl.onEndpointRead = (ep, size) => {
    if (ep !== cdc.outEndpoint) return;
    pendingRead = size;
    flushRead();
  };
  mcu.usbCtrl.resetDevice();
}
let pendingRead = null;
function flushRead() {
  if (pendingRead === null || !cdc || cdc.txFIFO.itemCount === 0) return;
  const buf = new Uint8Array(Math.min(pendingRead, cdc.txFIFO.itemCount));
  for (let i = 0; i < buf.length; i++) buf[i] = cdc.txFIFO.pull();
  pendingRead = null;
  mcu.usbCtrl.endpointReadDone(cdc.outEndpoint, buf);
}
function findHidIn(d) {
  let i = 0, isHid = false;
  while (i < d.length) {
    const len = d[i], type = d[i + 1];
    if (len < 2) break;
    if (type === 4) isHid = d[i + 5] === 3;
    if (type === 5 && isHid && (d[i + 2] & 0x80) && (d[i + 3] & 3) === 3) return d[i + 2] & 0x0f;
    i += len;
  }
  return -2;
}
function sendSerial(s) { for (const ch of s) cdc.sendSerialByte(ch.charCodeAt(0)); flushRead(); }

// ------------------------------------------------------------------ cablaggio
const ROWS = cfg.rows, COLS = cfg.cols;
const SG = cfg.signal_gpio;
const pressed = new Set();           // "gpioRiga,gpioColonna"
let fnPressed = false;
function updateInputs() {
  for (const c of COLS) {
    let low = false;
    for (const r of ROWS) if (pressed.has(r + ',' + c) && mcu.gpio[r].value === GPIOPinState.Low) low = true;
    mcu.gpio[c].setInputValue(!low);
  }
  mcu.gpio[cfg.fn].setInputValue(!fnPressed);
  for (const r of ROWS) mcu.gpio[r].setInputValue(mcu.gpio[r].value !== GPIOPinState.Low);
  for (const p of [cfg.tp_clk, cfg.tp_data, cfg.tp_rst]) mcu.gpio[p].setInputValue(mcu.gpio[p].value !== GPIOPinState.Low);
}
const ecEvents = [];
const ecLast = { EC_FN: 0, EC_PGUP: 0 };
for (let g = 0; g < 30; g++) {
  mcu.gpio[g].addListener((state) => {
    if (g === cfg.ec_fn || g === cfg.ec_pgup) {
      const name = g === cfg.ec_fn ? 'EC_FN' : 'EC_PGUP', v = state === GPIOPinState.High ? 1 : 0;
      if (ecLast[name] !== v) ecEvents.push([+(clock.nanos / 1e6).toFixed(3), name, v]);
      ecLast[name] = v;
    }
    updateInputs();
  });
}
updateInputs();

// ------------------------------------------------------------------ esecuzione
const CYCLE_NS = 1e9 / 125e6;
function runFor(ms) {
  const end = clock.nanos + ms * 1e6;
  while (clock.nanos < end && !watchdog && !serial.includes('Rebooting to UF2')) {   // dopo il riavvio in UF2 ci si ferma
    if (mcu.core.waiting) {
      const n = clock.nanosToNextAlarm;
      clock.tick(Number.isFinite(n) && n > 0 ? Math.min(n, end - clock.nanos + 1) : 1000);
    } else {
      clock.tick(mcu.core.executeInstruction() * CYCLE_NS);
    }
  }
}
const now = () => clock.nanos / 1e6;
const rd8 = (a) => (mcu.readUint32(a & ~3) >>> (8 * (a & 3))) & 0xff;
const SYM = cfg.symbols;
const oldKey = (r, c) => rd8(SYM.old_key + r * 8 + c);
const gpioOf = (rowPin, colPin) => [SG['KB_R' + rowPin], SG['KB_C' + colPin]];
function press(rowPin, colPin) { const [r, c] = gpioOf(rowPin, colPin); pressed.add(r + ',' + c); updateInputs(); }
function release(rowPin, colPin) { const [r, c] = gpioOf(rowPin, colPin); pressed.delete(r + ',' + c); updateInputs(); }
function setFn(v) { fnPressed = v; updateInputs(); }
const hidSince = (t) => hid.filter((h) => h[0] >= t);
const ecSince = (t) => ecEvents.filter((e) => e[0] >= t);

function expectHid(code, reports) {
  // ritorna [okPremuto, descrizione]
  const kb = reports.filter((h) => h[1] === 1), cons = reports.filter((h) => h[1] === 2), sys = reports.filter((h) => h[1] === 3);
  if (code >= 0xf000) { const k = code & 0xff; return [kb.some((h) => h.slice(4, 10).includes(k)), 'tasto 0x' + k.toString(16)]; }
  if (code >= 0xe400 && code < 0xf000) { const u = code - 0xe400; return [cons.some((h) => (h[2] | (h[3] << 8)) === u), 'consumer 0x' + u.toString(16)]; }
  if (code >= 0xe200 && code < 0xe400) { const u = code - 0xe200 - 0x80; return [sys.some((h) => h[2] === u), 'system 0x' + u.toString(16)]; }
  if (code >= 0xe000 && code < 0xe100) { const m = code & 0xff; return [kb.some((h) => (h[2] & m) === m), 'modificatore 0x' + m.toString(16)]; }
  return [reports.length === 0, 'nessun report (riservato)'];
}

const log = { tests: [], keys: [] };
const t0 = Date.now();
function check(name, ok, detail) { log.tests.push({ name, ok: !!ok, detail }); console.log((ok ? 'OK  ' : 'FAIL') + ' ' + name + (detail ? ' - ' + JSON.stringify(detail) : '')); }

runFor(1700);
attachHost();
runFor(2800);
check('avvio: USB enumerata con HID, seriale attiva', usbConnected && hidIn > 0, { usbConnected, hidIn, descrittore: cdc.descriptorsSize, serial: serial.slice(0, 160) });
check('avvio: nessun impulso verso EC', ecEvents.filter((e) => e[2] === 1).length === 0, ecEvents.slice(0, 4));
check('avvio: nessun riavvio', !watchdog, watchdog);

// ---- 1) tutti i 94 tasti
let okKeys = 0;
for (const k of cfg.keys) {
  const ts = now();
  press(k.rowPin, k.colPin);
  runFor(45);
  const hit = oldKey(k.r, k.c) === 0;
  const repPress = hidSince(ts);
  const [okPress, what] = expectHid(k.value, repPress);
  const tr = now();
  release(k.rowPin, k.colPin);
  runFor(45);
  const back = oldKey(k.r, k.c) === 1;
  const ok = hit && okPress && back;
  if (ok) okKeys++;
  log.keys.push({ name: k.name, pins: [k.rowPin, k.colPin], gpio: gpioOf(k.rowPin, k.colPin), matrix: [k.r, k.c], code: k.code, hid: what, matrix_hit: hit, hid_ok: okPress, released: back });
}
check('94 tasti: posizione in matrice e report HID corretti', okKeys === cfg.keys.length, { ok: okKeys, totale: cfg.keys.length, falliti: log.keys.filter((x) => !(x.matrix_hit && x.hid_ok && x.released)).map((x) => x.name) });

const SP = cfg.special;
function ecSequence(ev) {
  // cerca FN su, PGUP su, PGUP giu, FN giu e misura i tempi
  const seqs = [];
  for (let i = 0; i + 3 < ev.length; i++) {
    const [a, b, c, d] = ev.slice(i, i + 4);
    if (a[1] === 'EC_FN' && a[2] === 1 && b[1] === 'EC_PGUP' && b[2] === 1 && c[1] === 'EC_PGUP' && c[2] === 0 && d[1] === 'EC_FN' && d[2] === 0) {
      seqs.push({ fn_lead_ms: +(b[0] - a[0]).toFixed(1), pgup_ms: +(c[0] - b[0]).toFixed(1), fn_tail_ms: +(d[0] - c[0]).toFixed(1), t_ms: a[0] });
      i += 3;
    }
  }
  return seqs;
}

// ---- 2) Fn+PgUp -> sequenza verso l'EC, nessun PgUp verso il PC
let ts = now();
setFn(true); runFor(30); press(...SP.pgup); runFor(60); release(...SP.pgup); runFor(20); setFn(false); runFor(600);
let seq = ecSequence(ecSince(ts));
let pgupSent = hidSince(ts).some((h) => h[1] === 1 && h.slice(4, 10).includes(0x4b));
check('Fn+PgUp: un comando ThinkLight verso EC (Fn 40 ms, PgUp 100 ms, Fn 40 ms)', seq.length === 1 && Math.abs(seq[0].fn_lead_ms - 40) <= 15 && Math.abs(seq[0].pgup_ms - 100) <= 15 && Math.abs(seq[0].fn_tail_ms - 40) <= 15 && !pgupSent, { seq, pgupSent });

// ---- 3) PgUp da solo -> nessun evento EC, PgUp verso il PC
ts = now();
press(...SP.pgup); runFor(60); release(...SP.pgup); runFor(300);
pgupSent = hidSince(ts).some((h) => h[1] === 1 && h.slice(4, 10).includes(0x4b));
check('PgUp da solo: report HID PageUp, nessun evento EC', pgupSent && ecSince(ts).length === 0, { pgupSent, ec: ecSince(ts) });

// ---- 4) Fn+F5 -> tasto radio (report ID 4)
ts = now();
setFn(true); runFor(30); press(...SP.f5); runFor(60); release(...SP.f5); runFor(40); setFn(false); runFor(60);
const radio = hidSince(ts).filter((h) => h[1] === 4).map((h) => h[2]);
check('Fn+F5: report radio 1 poi 0 (modalita\' aereo)', radio.length >= 2 && radio[0] === 1 && radio[radio.length - 1] === 0, { radio });

// ---- 5) scambio Fn/Ctrl tenendo Fn+Ctrl 2,5 s
ts = now();
setFn(true); press(...SP.lctrl); runFor(2500); release(...SP.lctrl); setFn(false); runFor(1600);
const swapOn = rd8(SYM.SWAP_FN_CTRL);
seq = ecSequence(ecSince(ts));
check('Fn+Ctrl 2 s: scambio attivo, salvato, ThinkLight lampeggia (4 comandi EC)', swapOn === 1 && seq.length === 4 && serial.includes('ATTIVO'), { swapOn, comandi_ec: seq.length });
ts = now();
setFn(true); runFor(60);
const ctrlRep = hidSince(ts).filter((h) => h[1] === 1);
setFn(false); runFor(60);
check('scambio attivo: il Fn fisico manda Ctrl sinistro', ctrlRep.some((h) => (h[2] & 0x01) === 0x01), { reports: ctrlRep.slice(0, 2) });
ts = now();
press(...SP.lctrl); runFor(30); press(...SP.pgup); runFor(60); release(...SP.pgup); runFor(20); release(...SP.lctrl); runFor(600);
seq = ecSequence(ecSince(ts));
pgupSent = hidSince(ts).some((h) => h[1] === 1 && h.slice(4, 10).includes(0x4b));
const ctrlSent = hidSince(ts).some((h) => h[1] === 1 && (h[2] & 1));
check('scambio attivo: Ctrl fisico + PgUp = ThinkLight (il Ctrl fa da Fn)', seq.length === 1 && !pgupSent && !ctrlSent, { seq, pgupSent, ctrlSent });
ts = now();
sendSerial('SWAP\r'); runFor(300);
check('comando seriale SWAP: scambio spento', rd8(SYM.SWAP_FN_CTRL) === 0 && serial.includes('spento'), { swap: rd8(SYM.SWAP_FN_CTRL) });
runFor(1500);

// ---- 6) apprendimento JIS: comando seriale, posizione vuota, poi International1
const [er, ec] = cfg.empty_positions[0];
const FWR = [32, 28, 20, 16, 12, 8, 4, 22, 26, 30, 18, 14, 10, 6, 2, 24], FWC = [5, 9, 13, 17, 15, 11, 7, 3];
const emptyPins = [FWR[er], FWC[ec]];
sendSerial('JIS\r'); runFor(200);
press(...emptyPins); runFor(60); release(...emptyPins); runFor(60);
for (let i = 0; i < 4; i++) { press(...SP.esc); runFor(60); release(...SP.esc); runFor(60); }
runFor(200);
const jr = rd8(SYM.jis_pos), jc = rd8(SYM.jis_pos + 1), learnState = rd8(SYM.jis_learn);
ts = now();
press(...emptyPins); runFor(60);
const intl = hidSince(ts).some((h) => h[1] === 1 && h.slice(4, 10).includes(0x87));
release(...emptyPins); runFor(60);
check('JIS: posizione vuota appresa come International1 e inviata come 0x87', jr === er && jc === ec && learnState === 0 && intl && serial.includes('Tasti JIS salvati'), { posizione: [er, ec], appresa: [jr, jc], intl });

// ---- 7) Fn+ThinkVantage: 1 s non riavvia, 3,6 s riavvia in UF2
setFn(true); runFor(30); press(...SP.thinkvantage); runFor(1000); release(...SP.thinkvantage); runFor(30); setFn(false); runFor(200);
const pc1 = mcu.core.PC >>> 0;
check('Fn+ThinkVantage 1 s: nessun riavvio', !serial.includes('Rebooting to UF2') && !watchdog, { PC: '0x' + pc1.toString(16) });
const tTv = now();
setFn(true); runFor(30); press(...SP.thinkvantage); runFor(3600);
const pc2 = mcu.core.PC >>> 0;
const tReboot = now() - tTv;
check('Fn+ThinkVantage tenuto: riavvio nel bootloader UF2 dopo circa 3 s', serial.includes('Rebooting to UF2') && tReboot > 3000 && tReboot < 3400, { dopo_ms: +tReboot.toFixed(0), PC: '0x' + pc2.toString(16) });

log.ec_events = ecEvents;
log.warnings = warnings;
log.watchdog = watchdog;
log.hid_count = hid.length;
log.serial_tail = serial.slice(-3000);
log.wall_seconds = (Date.now() - t0) / 1000;
log.sim_ms = now();
log.passed = log.tests.filter((t) => t.ok).length;
log.total = log.tests.length;
fs.writeFileSync(outPath, JSON.stringify(log, null, 1));
console.log(`${log.passed}/${log.total} prove superate in ${log.wall_seconds}s (simulati ${log.sim_ms.toFixed(0)} ms)`);
