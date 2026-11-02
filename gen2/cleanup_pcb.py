# -*- coding: utf-8 -*-
"""Pulizia dopo l'import dello sbroglio: tratti di pista con un'estremita' libera e via doppie.

Il pre-instradamento lascia piste che Freerouting a volte collega a meta' percorso: il resto del tratto resta
con un'estremita' libera (track_dangling nel DRC). Si tolgono i tratti finche' non ne restano, poi le via
sovrapposte della stessa net e le via collegate su un solo strato.

uso: python cleanup_pcb.py in.kicad_pcb out.kicad_pcb
"""
import sys

import pcbnew


def dangling(board, tracks):
    """piste con un'estremita' non collegata, secondo la connettivita' di KiCad"""
    board.BuildConnectivity()
    c = board.GetConnectivity()
    return [t for t in tracks if t.GetClass() in ("PCB_TRACK", "PCB_VIA") and c.TestTrackEndpointDangling(t, False)]


def one_pass(src, dst):
    """una passata: ritorna (tratti tolti, via doppie tolte)"""
    board = pcbnew.LoadBoard(src)
    tracks = list(board.GetTracks())     # una sola lettura: dopo BuildConnectivity pcbnew non la ripete
    seen, extra = [], []                 # via doppie, prima di BuildConnectivity (dopo le posizioni non si leggono)
    for v in [t for t in tracks if t.GetClass() == "PCB_VIA"]:
        pos = v.GetStart()               # KiCad 10: GetPosition() del via letto da GetTracks() non e' un VECTOR2I
        k = (v.GetNetCode(), pos.x, pos.y)
        if any(c == k[0] and abs(x - k[1]) < 1000 and abs(y - k[2]) < 1000 for c, x, y in seen):
            extra.append(v)        # entro 1 micron da un'altra via della stessa net: e' la stessa via
        else:
            seen.append(k)
    d = [t for t in dangling(board, tracks) if not any(t is e for e in extra)]
    for t in d + extra:
        board.Remove(t)
    pcbnew.SaveBoard(dst, board)
    return len(d), len(extra)


def main():
    # una passata per processo: pcbnew (KiCad 10) non regge LoadBoard ripetuti nello stesso processo
    import json
    import subprocess
    src, dst = sys.argv[1:3]
    if "--una" in sys.argv:
        print(json.dumps(one_pass(src, dst)))
        return
    n = dup = 0
    for _ in range(10):
        out = subprocess.run([sys.executable, __file__, src, dst, "--una"], capture_output=True, text=True)
        last = [ln for ln in out.stdout.splitlines() if ln.startswith("[")]
        if out.returncode or not last:
            sys.stderr.write(out.stderr[-2000:])
            raise SystemExit("pulizia fallita")
        d, e = json.loads(last[-1])
        n, dup, src = n + d, dup + e, dst
        if not d and not e:
            break
    print(f"pulizia: {n} tratti con un'estremita' libera, {dup} via doppie")


if __name__ == "__main__":
    main()
