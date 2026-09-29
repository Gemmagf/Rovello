"""Genera les icones de la PWA a partir del logo del bolet (mateixa geometria
que RovelloLogo a src/components/Header.js). Ús: python3 scripts/make_icons.py

Si tens el logo original en PNG quadrat, posa'l a public/icons/icon-source.png i
executa amb --from-source per derivar-ne totes les mides.
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

GREEN, CREAM = (0x2E, 0x4B, 0x3A, 255), (0xF2, 0xEF, 0xE6, 255)
OUT = Path(__file__).resolve().parent.parent / "public" / "icons"
OUT.mkdir(parents=True, exist_ok=True)
SS = 4096  # supersampling


def draw_mushroom(img, scale=1.0):
    """Dibuixa el bolet centrat: cèrcol fi + làmines radials crema sobre el fons
    verd, i tija trapezoïdal. scale redueix el motiu (zona segura maskable)."""
    d = ImageDraw.Draw(img)
    W = img.width
    u = W / 100.0  # unitat del grid 100x100 (mateix que RovelloLogo al frontend)

    def P(x, y):
        return ((x - 50) * scale + 50) * u, ((y - 50) * scale + 50) * u

    cx, cy = 50, 59          # centre del barret (punt d'on surten les làmines)
    r_rim, r_gill = 36, 32.5  # radi del cèrcol i de les làmines
    rim_w = 2.4 * u * scale
    # Cèrcol (semicercle superior) com a arc gruixut
    x0, y0 = P(cx - r_rim, cy - r_rim); x1, y1 = P(cx + r_rim, cy + r_rim)
    d.arc([x0, y0, x1, y1], start=180, end=360, fill=CREAM, width=int(rim_w))
    # Làmines: 25 línies de 0..180° (cada 7,5°), del centre fins a prop del cèrcol
    lw = 1.9 * u * scale
    for i in range(25):
        a = math.radians(i * 7.5)
        ex, ey = cx + r_gill * math.cos(math.pi - a), cy - r_gill * math.sin(a)
        (sx, sy), (tx, ty) = P(cx, cy), P(ex, ey)
        d.line([(sx, sy), (tx, ty)], fill=CREAM, width=int(lw))
        d.ellipse([tx - lw / 2, ty - lw / 2, tx + lw / 2, ty + lw / 2], fill=CREAM)
    # Tija: trapezi arrodonit (més ample a la base), que tapa el nus central
    top_w, bot_w, top_y, bot_y = 11, 16, 55, 86
    pts = [P(cx - top_w / 2, top_y), P(cx + top_w / 2, top_y), P(cx + bot_w / 2, bot_y), P(cx - bot_w / 2, bot_y)]
    d.polygon(pts, fill=CREAM)
    return img


def render(size, mode):
    """mode: 'rounded' (cantonades transparents), 'full' (quadrat ple, iOS),
    'maskable' (quadrat ple + motiu al 72 % per a la zona segura d'Android)."""
    img = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if mode == "rounded":
        d.rounded_rectangle([0, 0, SS - 1, SS - 1], radius=int(SS * 0.20), fill=GREEN)
        draw_mushroom(img, 1.0)
    elif mode == "full":
        d.rectangle([0, 0, SS, SS], fill=GREEN)
        draw_mushroom(img, 0.92)
    else:
        d.rectangle([0, 0, SS, SS], fill=GREEN)
        draw_mushroom(img, 0.72)
    return img.resize((size, size), Image.LANCZOS)


def main():
    if "--from-source" in sys.argv:
        src = Image.open(OUT / "icon-source.png").convert("RGBA")
        def render_src(size, mode):
            base = src.resize((SS, SS), Image.LANCZOS)
            if mode == "maskable":
                canvas = Image.new("RGBA", (SS, SS), GREEN)
                inner = int(SS * 0.72); off = (SS - inner) // 2
                canvas.paste(base.resize((inner, inner), Image.LANCZOS), (off, off), base.resize((inner, inner), Image.LANCZOS))
                return canvas.resize((size, size), Image.LANCZOS)
            return base.resize((size, size), Image.LANCZOS)
        R = render_src
    else:
        R = render
    R(1024, "rounded").save(OUT / "icon-1024.png")
    R(512, "rounded").save(OUT / "icon-512.png")
    R(192, "rounded").save(OUT / "icon-192.png")
    R(512, "maskable").save(OUT / "icon-512-maskable.png")
    R(192, "maskable").save(OUT / "icon-192-maskable.png")
    R(180, "full").save(OUT / "apple-touch-icon.png")
    R(32, "rounded").save(OUT / "favicon-32.png")
    R(16, "rounded").save(OUT / "favicon-16.png")
    R(64, "rounded").save(OUT.parent / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    # Imatge per compartir (Open Graph) 1200x630
    og = Image.new("RGBA", (1200, 630), CREAM)
    logo = R(360, "rounded")
    og.paste(logo, (120, 135), logo)
    ImageDraw.Draw(og)  # (text opcional: es deixa net, el títol el posa la meta)
    og.convert("RGB").save(OUT / "og-image.png", optimize=True)
    print("icones generades a", OUT)


if __name__ == "__main__":
    main()
