#!/usr/bin/env python3
"""Dumprin post builder.

Usage:  python3 compose.py manifest.json SRC_DIR OUT_DIR

For every entry in manifest.json whose "src" file exists in SRC_DIR it writes:
  - kind "image": a 1080x1350 JPEG feed post (photo framed on white, kicker + headline below)
  - kind "reel":  a 1080x1920 MP4 Reel (slow push-in on the still, headline pill at the top,
                  2.2 s Dumprin end card, quiet sound bed)
Needs: Pillow, ffmpeg. Fonts, end card and sound bed sit next to this script.
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
FRED = os.path.join(HERE, "fonts", "Fredoka-SemiBold.ttf")
FIG = os.path.join(HERE, "fonts", "Figtree-SemiBold.ttf")
INK = (11, 47, 63)
GOLD_INK = (138, 82, 16)


def wrap(draw, text, font, width):
    lines = []
    for para in text.split("\n"):
        words, cur = para.split(), ""
        for w in words:
            t = (cur + " " + w).strip()
            if draw.textlength(t, font=font) <= width or not cur:
                cur = t
            else:
                lines.append(cur); cur = w
        lines.append(cur)
    return lines


def fit(draw, text, maxw, maxh, hi, lo, lead=1.12):
    for size in range(hi, lo - 1, -2):
        f = ImageFont.truetype(FRED, size)
        lines = wrap(draw, text, f, maxw)
        h = int(len(lines) * size * lead)
        if h <= maxh:
            return f, lines, size
    f = ImageFont.truetype(FRED, lo)
    return f, wrap(draw, text, f, maxw), lo


def rounded(im, r):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1], r, fill=255)
    return m


def image_post(src, out, kicker, headline, zoom=1.0):
    W, H = 1080, 1350
    canvas = Image.new("RGB", (W, H), "white")
    ph = Image.open(src).convert("RGB")
    fw, fh = 888, 1110
    if zoom > 1:
        w, h = ph.size
        cw, ch = int(w / zoom), int(h / zoom)
        ph = ph.crop(((w - cw) // 2, (h - ch) // 2, (w - cw) // 2 + cw, (h - ch) // 2 + ch))
    ph = ImageOps.fit(ph, (fw, fh), Image.LANCZOS)
    canvas.paste(ph, (96, 40), rounded(ph, 48))
    d = ImageDraw.Draw(canvas)
    kf = ImageFont.truetype(FIG, 21)
    k = kicker.upper()
    x = 100
    for ch_ in k:  # letter-spaced kicker
        d.text((x, 1172), ch_, font=kf, fill=GOLD_INK)
        x += d.textlength(ch_, font=kf) + 2
    f, lines, size = fit(d, headline, 880, 1340 - 1206, 52, 30)
    y = 1204
    for ln in lines:
        d.text((100, y), ln, font=f, fill=INK)
        y += int(size * 1.12)
    canvas.save(out, "JPEG", quality=92)


def headline_png(text, path):
    W = 1080
    tmp = Image.new("RGBA", (W, 600), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    f, lines, size = fit(d, text, 900 - 88, 260, 64, 44)
    lh = int(size * 1.12)
    tw = max(d.textlength(l, font=f) for l in lines)
    bw, bh = int(tw + 88), len(lines) * lh + 52
    bx, by = (W - bw) // 2, 170
    img = Image.new("RGBA", (W, 1920), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, 1920), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([bx, by + 10, bx + bw, by + bh + 10], 36, fill=(0, 0, 0, 40))
    img = Image.alpha_composite(img, sh)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([bx, by, bx + bw, by + bh], 36, fill=(255, 255, 255, 240))
    y = by + 22
    for ln in lines:
        lw = d.textlength(ln, font=f)
        d.text(((W - lw) / 2, y), ln, font=f, fill=INK)
        y += lh
    img.save(path)


def reel(src, out, headline, seconds=8.0):
    with tempfile.TemporaryDirectory() as t:
        still = os.path.join(t, "still.png")
        ImageOps.fit(Image.open(src).convert("RGB"), (1080, 1920), Image.LANCZOS).save(still)
        head = os.path.join(t, "head.png")
        headline_png(headline, head)
        frames = int(seconds * 30)
        end = os.path.join(HERE, "endcard.png")
        bed = os.path.join(HERE, "bed.m4a")
        off = seconds - 0.4
        fc = (
            f"[0:v]scale=4320:7680,zoompan=z='1+0.06*on/{frames}':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,"
            f"format=yuv420p,setsar=1[bg];"
            f"[bg][2:v]overlay=0:0:enable='gte(t,0.3)',settb=1/30,fps=30[a];"
            f"[1:v]scale=1080:1920,fps=30,format=yuv420p,setsar=1,settb=1/30[e];"
            f"[a][e]xfade=transition=fade:duration=0.4:offset={off}[v]"
        )
        cmd = ["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", str(seconds), "-i", still,
               "-loop", "1", "-t", "2.2", "-framerate", "30", "-i", end, "-i", head, "-i", bed,
               "-filter_complex", fc, "-map", "[v]", "-map", "3:a", "-c:v", "libx264", "-preset", "veryfast",
               "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest",
               "-movflags", "+faststart", out]
        subprocess.run(cmd, check=True)


def main():
    man, srcdir, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    items = json.load(open(man, encoding="utf-8"))
    done, missing = [], []
    for it in items:
        src = os.path.join(srcdir, it["src"])
        if not os.path.exists(src):
            missing.append(it["src"]); continue
        out = os.path.join(outdir, it["out"])
        if it["kind"] == "image":
            image_post(src, out, it["kicker"], it["headline"], it.get("zoom", 1.0))
        else:
            reel(src, out, it["headline"])
        done.append(it["out"]); print("made", it["out"], flush=True)
    print(f"done {len(done)}, skipped {len(missing)} (source not in this folder)")


if __name__ == "__main__":
    main()
