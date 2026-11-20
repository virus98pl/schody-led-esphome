"""Symulacja efektu „Schody auto” 1:1 z lambdą w schody-sterownik.yaml.
Rysuje docs/animacja.png (jasność stopni w czasie) i docs/animacja.gif."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

N, OPOZ, FADE, SWIEC = 16, 120, 400, 3.0          # stopnie, ms, ms, s (w symulacji krócej niż domyślne 25 s)
POS, DT = 0.08, 20

def symuluj(zdarzenia, czas_ms):
    faza, kier, t_start, t_kon, t_gas = 0, 1, 0, 0, 0
    poz = np.zeros(N); hist = []
    sekw = (N - 1) * OPOZ
    for t in range(0, czas_ms, DT):
        for (tz, skad) in zdarzenia:
            if tz == t:
                if faza == 0: kier, t_start = skad, t
                elif faza == 2: kier, t_start = skad, t - sekw
                elif t - t_start >= sekw: kier = skad
                faza = 1; t_kon = t + sekw + int(SWIEC * 1000)
        if t % 100 == 0:
            if faza == 1 and t >= t_kon: faza, t_gas = 2, t
            elif faza == 2 and t - t_gas > sekw + FADE * 4 + 500: faza = 0
        alfa = 1.0 if FADE <= 20 else 20 / FADE
        for k in range(N):
            kol = k if kier == 1 else N - 1 - k
            sp = POS if k in (0, N - 1) else 0.0
            cel = sp
            if faza == 1: cel = 1.0 if t - t_start >= kol * OPOZ else sp
            elif faza == 2: cel = sp if t - t_gas >= kol * OPOZ else 1.0
            poz[k] += (cel - poz[k]) * alfa
        hist.append(poz.copy())
    return np.array(hist)

H = symuluj([(200, 1), (7000, -1)], 13000)
t = np.arange(len(H)) * DT / 1000
fig, ax = plt.subplots(figsize=(10, 3.6))
ax.imshow(H.T, aspect="auto", origin="lower", cmap="magma", extent=[0, t[-1], 0.5, N + 0.5], vmin=0, vmax=1)
ax.set_xlabel("czas [s]"); ax.set_ylabel("stopień (1 = dół)")
ax.set_title("Wejście od dołu (0,2 s) i zejście od góry (7 s); czas świecenia 3 s, opóźnienie 120 ms, płynność 400 ms")
ax.set_yticks([1, 4, 8, 12, 16])
fig.tight_layout(); fig.savefig("docs/animacja.png", dpi=110)

# GIF: schody z boku
klatki = []
for i in range(0, 380, 2):
    im = Image.new("RGB", (360, 300), (22, 22, 28)); d = ImageDraw.Draw(im)
    for k in range(N):
        x0, y0 = 20 + k * 20, 280 - k * 16
        d.rectangle((x0, y0 - 16, x0 + 20, y0), outline=(70, 70, 80))
        v = H[i, k]; c = (int(40 + 215 * v), int(40 + 200 * v), int(40 + 150 * v))
        d.line((x0 + 1, y0 - 15, x0 + 19, y0 - 15), fill=c, width=3)
    d.text((10, 8), f"t = {i * DT / 1000:4.1f} s", fill=(200, 200, 200))
    klatki.append(im)
klatki[0].save("docs/animacja.gif", save_all=True, append_images=klatki[1:], duration=40, loop=0)
print("ok", H.shape)
