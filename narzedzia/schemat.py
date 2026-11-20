"""Rysuje docs/schemat_polaczen.png – schemat zasilania i danych schodów."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

R, D, G, P = "#d62728", "#1f77b4", "#222222", "#2ca02c"
fig, ax = plt.subplots(figsize=(13, 7.2)); ax.set_xlim(0, 130); ax.set_ylim(0, 72); ax.axis("off")

def box(x, y, w, h, t, fc="#f4f4f4", fs=8.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4", fc=fc, ec="#555"))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs)

def line(pts, c, lw=2, ls="-"):
    xs, ys = zip(*pts); ax.plot(xs, ys, color=c, lw=lw, ls=ls, solid_capstyle="round")

box(2, 54, 22, 12, "Zasilacz 24 V\n480 W\n(np. Mean Well LRS-450-24)", "#fff3e0")
box(2, 34, 22, 14, "Bezpieczniki 2 A\nna każdy stopień\n(listwa z oprawkami)", "#fff3e0")
box(2, 10, 22, 16, "Sterownik ESP32\n+ konwerter poziomów\n(74AHCT125)\nschody-sterownik", "#e3f2fd")
box(30, 10, 10, 6, "220–470 Ω", "#eee", 8)
line([(13, 54), (13, 48)], R, 3); ax.text(14, 51, "+24 V / GND", fontsize=8, color=R)
line([(13, 34), (13, 26)], R, 1.5); ax.text(14, 30, "24 V", fontsize=8, color=R)
line([(24, 13), (30, 13)], D, 2); line([(40, 13), (50, 13), (50, 17)], D, 2)

# stopnie
xs = [50 + i * 3.5 for i in range(16)]
for i, x in enumerate(xs):
    y = 17 + i * 2.3
    ax.add_patch(plt.Rectangle((x, y), 3.5, 2.3, fc="#fafafa", ec="#999"))
    ax.plot([x + 0.3, x + 3.2], [y + 2.05, y + 2.05], color="#f5b700", lw=3)
    if i % 2 == 0:
        ax.annotate("", xy=(x + 3.2, y + 1.2), xytext=(x + 0.4, y + 1.2), arrowprops=dict(arrowstyle="->", color=D, lw=0.9))
    else:
        ax.annotate("", xy=(x + 0.4, y + 1.2), xytext=(x + 3.2, y + 1.2), arrowprops=dict(arrowstyle="->", color=D, lw=0.9))
    line([(24, 41), (x + 2.3, 41 if y < 41 else 41), (x + 2.3, y)], R, 0.6, ":") if False else None
ax.text(xs[0] - 1, 14, "stopień 1", fontsize=8); ax.text(xs[-1] - 9, 17 + 15 * 2.3 + 0.6, "stopień 16", fontsize=8)
ax.text(30, 66, "Taśma WS2814 RGBW 24 V, 15 odcinków × 71,4 mm = 107,1 cm na stopień\n"
        "Dane: DO stopnia → DI następnego, zworka 2 × 0,35 mm² (DATA + GND), układ „wężykiem”\n"
        "Zasilanie: każdy stopień własnym kablem 2 × 0,75 mm² od listwy bezpieczników", fontsize=8.5, va="top")
line([(24, 41), (46, 41)], R, 2); ax.text(26, 42, "16 × kabel 2-żyłowy do stopni", fontsize=8, color=R)

box(108, 4, 20, 13, "Czujnik DÓŁ\nESP32-C3 + VL53L5CX\nschody-dol\n(podstopnica stopnia 1)", "#e8f5e9", 8)
box(108, 50, 20, 13, "Czujnik GÓRA\nESP32-C3 + VL53L5CX\nschody-gora\n(ostatni stopień / podest)", "#e8f5e9", 8)
box(62, 1, 30, 6, "przetwornica 24→5 V + bezpiecznik 0,5 A\nprzy każdym czujniku", "#e8f5e9", 7.5)
line([(108, 10), (96, 10)], P, 1.5, "--"); line([(108, 56), (100, 56)], P, 1.5, "--")
ax.text(95, 11, "Wi-Fi / UDP", fontsize=8, color=P); ax.text(99, 57, "Wi-Fi / UDP", fontsize=8, color=P)
ax.text(2, 70, "Schody LED – schemat połączeń (bez skali)", fontsize=12, weight="bold")
ax.text(2, 4, "Wspólna masa: GND zasilacza, sterownika i wszystkich taśm połączone.\nCzujniki mają tylko zasilanie – dane idą przez Wi-Fi.", fontsize=7.5)
fig.tight_layout(); fig.savefig("docs/schemat_polaczen.png", dpi=110)
