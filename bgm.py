import numpy as np, wave, sys

SR = 44100
DUR = 12.5
BPM = 96
beat = 60 / BPM
N = int(SR * DUR)
out = np.zeros(N)

def note(f, start, length, amp, kind="ep"):
    s = int(start * SR); n = int(length * SR)
    if s >= N: return
    n = min(n, N - s)
    t = np.arange(n) / SR
    if kind == "ep":      # soft electric piano
        w = np.sin(2*np.pi*f*t) + 0.35*np.sin(2*np.pi*2*f*t) + 0.12*np.sin(2*np.pi*3*f*t)
        env = np.exp(-t*2.2) * np.minimum(1, t/0.01)
    elif kind == "pluck":  # bright pluck
        w = np.sin(2*np.pi*f*t) + 0.5*np.sin(2*np.pi*2*f*t)*np.exp(-t*8)
        env = np.exp(-t*6) * np.minimum(1, t/0.004)
    elif kind == "bass":
        w = np.sin(2*np.pi*f*t)
        env = np.exp(-t*1.5) * np.minimum(1, t/0.01)
    elif kind == "bell":
        w = np.sin(2*np.pi*f*t) + 0.4*np.sin(2*np.pi*2.76*f*t)
        env = np.exp(-t*3)
    out[s:s+n] += amp * w * env

def hz(m): return 440 * 2 ** ((m - 69) / 12)

# C - Am - F - G - C (one bar each = 4 beats = 2.5s)
chords = [[60,64,67,72], [57,60,64,69], [53,57,60,65], [55,59,62,67], [60,64,67,72]]
bass   = [36, 33, 29, 31, 36]
mel = [  # 8th-note arpeggio pattern per bar (indices into chord)
    [3,2,1,2,3,2,1,0],
]
rng = np.random.default_rng(7)
for b, ch in enumerate(chords):
    t0 = b * 4 * beat
    for m in ch: note(hz(m), t0, 4*beat, 0.07, "ep")
    note(hz(bass[b]), t0, 2*beat, 0.22, "bass")
    note(hz(bass[b]), t0 + 2*beat, 2*beat, 0.16, "bass")
    for i, idx in enumerate(mel[0]):
        note(hz(ch[idx] + 12), t0 + i*beat/2, beat/2, 0.05, "pluck")
    for k in range(4):  # kick on every beat, softer on 2 and 4
        s = int((t0 + k*beat) * SR); n = int(0.18*SR)
        if s + n <= N:
            t = np.arange(n)/SR
            out[s:s+n] += (0.35 if k % 2 == 0 else 0.18) * np.sin(2*np.pi*(55 + 90*np.exp(-t*30))*t) * np.exp(-t*18)
    for k in range(8):  # shaker on offbeats
        if k % 2 == 1:
            s = int((t0 + k*beat/2) * SR); n = int(0.05*SR)
            if s + n <= N:
                noise = rng.standard_normal(n); noise = np.diff(noise, prepend=0)
                out[s:s+n] += 0.03 * noise * np.exp(-np.arange(n)/SR*60)

# sparkle when the score finishes counting (~7.3s)
for i, m in enumerate([84, 88, 91, 96]):
    note(hz(m), 7.25 + i*0.06, 1.2, 0.07, "bell")

# fade in/out, normalize
fade = int(0.3*SR); out[:fade] *= np.linspace(0, 1, fade)
fo = int(0.8*SR); out[-fo:] *= np.linspace(1, 0, fo)
out = out / np.max(np.abs(out)) * 0.6
pcm = (np.stack([out, out], 1) * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("ok")
