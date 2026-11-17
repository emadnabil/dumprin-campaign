"""Render the 4:30 carousels and the 8:15 story Reels locally.
python3 render.py carousels|reels [day ...]"""
import asyncio, json, os, subprocess, sys, html, re
from playwright.async_api import async_playwright

ROOT = "/home/claude/dumprin"
OUT = "/home/claude/dumprin-campaign"
IMG = json.load(open(f"{ROOT}/img/img.json"))
FONTS = f"file://{ROOT}/samples/node_modules/@fontsource"
SCRIPTS = json.loads(subprocess.check_output(["node", "-e", "console.log(JSON.stringify(require('./scripts.js')))"], cwd=f"{ROOT}/story"))
POSTS = json.loads(subprocess.check_output(["node", "-e", r'''
const fs=require("fs");const P_=[];function P(d,s,o){o.d=d;o.s=s;P_.push(o);}
for(const f of fs.readdirSync("../data").filter(f=>f.startsWith("d0")).sort()) eval(fs.readFileSync("../data/"+f,"utf8"));
console.log(JSON.stringify(P_));'''], cwd=f"{ROOT}/story"))
POSES = ["offer", "stand", "shy", "wink", "smirk", "cheer", "hug"]
CSS = f"""
@font-face{{font-family:Fredoka;font-weight:600;src:url({FONTS}/fredoka/files/fredoka-latin-600-normal.woff2)}}
@font-face{{font-family:Fredoka;font-weight:700;src:url({FONTS}/fredoka/files/fredoka-latin-700-normal.woff2)}}
@font-face{{font-family:Figtree;font-weight:600;src:url({FONTS}/figtree/files/figtree-latin-600-normal.woff2)}}
*{{margin:0;box-sizing:border-box}}
body{{background:#fff;color:#0B2F3F;font-family:Figtree;position:relative;overflow:hidden}}
.k{{font:600 26px/1 Figtree;letter-spacing:.1em;text-transform:uppercase;color:#8A5210}}
.brand{{position:absolute;font:700 34px Fredoka;color:#0B2F3F}} .brand span{{color:#FD7900}}
.dot{{display:inline-block;width:14px;height:14px;border-radius:50%;background:#F7A440;margin-right:10px;vertical-align:middle}}
"""
esc = lambda s: html.escape(s)


def carousel_pages(p):
    parts = p["v"].split(" | ")
    slides = [s for s in parts[1:]]
    pages, n = [], len(slides) + 1
    cover_pose = POSES[p["d"] % len(POSES)]
    pages.append(f"""<div style="position:absolute;inset:0;background:#FFF6E6"></div>
<div style="position:absolute;left:84px;top:96px;right:84px"><div class="k">{esc(p['k'])}</div>
<h1 style="font:700 {92 if len(p['t'])<40 else 78}px/1.04 Fredoka;margin-top:26px;letter-spacing:-.02em;text-wrap:balance">{esc(p['t'])}</h1></div>
<img src="{IMG[cover_pose]['src']}" style="position:absolute;right:40px;bottom:70px;height:600px">
<div style="position:absolute;left:84px;bottom:96px;font:600 30px Figtree;color:#5F6E78">Swipe <span style="color:#FD7900">→</span></div>
<div class="brand" style="left:84px;bottom:150px">Dumprin<span>.</span></div>""")
    for i, s in enumerate(slides):
        pose = POSES[(p["d"] + i + 1) % len(POSES)]
        size = 66 if len(s) < 70 else 56 if len(s) < 120 else 48
        pages.append(f"""<div style="position:absolute;left:84px;top:96px;font:600 26px Figtree;color:#8A5210;letter-spacing:.08em">{i+2} / {n}</div>
<div style="position:absolute;left:84px;right:84px;top:200px;bottom:470px;display:flex;align-items:center">
<p style="font:600 {size}px/1.18 Fredoka;text-wrap:balance">{esc(s)}</p></div>
<img src="{IMG[pose]['src']}" style="position:absolute;right:60px;bottom:60px;height:360px">
<div class="brand" style="left:84px;bottom:84px;font-size:30px">Dumprin<span>.</span> <span style="font:600 24px Figtree;color:#5F6E78;margin-left:10px">dumprin.com</span></div>""")
    return pages


BUB = {"k": ("Kid", "#EEF1F3", "left"), "p": ("Parent", "#E3ECF6", "left"), "d": ("Dumprin", "#FFE3B8", "right")}


def reel_frames(d, sc, title, kicker):
    lines = sc["l"]
    frames = []
    for i in range(len(lines)):
        shown = lines[max(0, i - 3): i + 1]
        items = ""
        for j, (who, txt) in enumerate(shown):
            last = j == len(shown) - 1
            op = "1" if last else ".55"
            if who == "t":
                size = 60 if len(txt) < 45 else 50
                items += f'<div style="opacity:{op};text-align:center;font:700 {size}px/1.15 Fredoka;padding:10px 20px;text-wrap:balance">{esc(txt)}</div>'
            else:
                lab, bg, side = BUB[who]
                al = "flex-end" if side == "right" else "flex-start"
                items += f'''<div style="opacity:{op};display:flex;flex-direction:column;align-items:{al}">
<div style="font:600 24px Figtree;letter-spacing:.08em;text-transform:uppercase;color:#5F6E78;margin:0 18px 8px">{lab}</div>
<div style="background:{bg};border-radius:44px;{'border-bottom-right-radius:12px' if side=='right' else 'border-bottom-left-radius:12px'};padding:30px 40px;max-width:860px;font:600 50px/1.2 Fredoka">{esc(txt)}</div></div>'''
        speaking = lines[i][0] == "d"
        frames.append(f"""<div style="position:absolute;left:80px;right:80px;top:120px"><div class="k">{esc(kicker)}</div>
<div style="font:700 48px/1.1 Fredoka;margin-top:14px">{esc(title)}</div></div>
<div style="position:absolute;left:70px;right:70px;top:330px;bottom:520px;display:flex;flex-direction:column;justify-content:flex-end;gap:34px">{items}</div>
<img src="{IMG[sc['pose']]['src']}" style="position:absolute;left:50%;bottom:{70 if speaking else 50}px;height:{440 if speaking else 400}px;transform:translateX(-50%)">""")
    return frames


async def shoot(pages, w, h, prefix):
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await b.new_page(viewport={"width": w, "height": h})
        paths = []
        for i, body in enumerate(pages):
            open("/tmp/_s.html", "w").write(f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{CSS}body{{width:{w}px;height:{h}px}}</style></head><body>{body}</body></html>")
            await pg.goto("file:///tmp/_s.html"); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(120)
            path = f"{prefix}_{i+1:02d}.jpg"; await pg.screenshot(path=path, type="jpeg", quality=90); paths.append(path)
        await b.close(); return paths


def hold(txt):
    return min(4.2, max(1.8, 1.0 + len(txt) * 0.045))


def build_reel(d, frames, sc, out):
    durs = [hold(t) for _, t in sc["l"]]
    end = f"{ROOT}/reels/end.png"
    inputs, fc, X = [], [], 0.3
    for i, f in enumerate(frames):
        inputs += ["-loop", "1", "-t", f"{durs[i]+X:.2f}", "-i", f]
    inputs += ["-loop", "1", "-t", "2.4", "-i", end]
    n = len(frames) + 1
    for i in range(n):
        fc.append(f"[{i}:v]scale=1080:1920,fps=30,format=yuv420p,setsar=1,settb=1/30[v{i}]")
    cur, t = "v0", durs[0]
    for i in range(1, n):
        fc.append(f"[{cur}][v{i}]xfade=transition=fade:duration={X}:offset={t:.2f}[x{i}]"); cur = f"x{i}"
        if i < len(frames): t += durs[i]
    total = t + 2.4
    # sound: quiet room tone + a soft pop at each new line + chime at the end card
    pops, at = [], 0.15
    for i in range(len(frames)):
        pops.append(at); at += durs[i]
    afc = [f"anoisesrc=color=brown:amplitude=0.010:d={total:.2f}[bed]"]
    for i, ptime in enumerate(pops):
        ms = int(ptime * 1000)
        afc.append(f"sine=frequency={660 if sc['l'][i][0]=='d' else 520}:duration=0.07,afade=t=out:st=0:d=0.07,volume=0.12,adelay={ms}|{ms}[p{i}]")
    cm = int((t + 0.1) * 1000)
    afc.append(f"sine=frequency=1318:duration=1.2,afade=t=out:st=0:d=1.2,volume=0.16,adelay={cm}|{cm}[ch]")
    mix = "[bed]" + "".join(f"[p{i}]" for i in range(len(pops))) + "[ch]"
    afc.append(f"{mix}amix=inputs={len(pops)+2}:normalize=0,lowpass=f=3500[a]")
    fcs = ";".join(fc) + ";" + ";".join(afc)
    cmd = ["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", fcs, "-map", f"[{cur}]", "-map", "[a]",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
           "-ac", "2", "-t", f"{total:.2f}", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)


async def main():
    mode, days = sys.argv[1], [int(x) for x in sys.argv[2:]]
    os.makedirs(f"{OUT}/carousels", exist_ok=True); os.makedirs(f"{OUT}/story", exist_ok=True); os.makedirs("/tmp/fr", exist_ok=True)
    if mode == "carousels":
        SKIP = {7, 33, 39, 45}
        for p in [p for p in POSTS if p["s"] == 3 and p["d"] not in SKIP and (not days or p["d"] in days)]:
            await shoot(carousel_pages(p), 1080, 1350, f"{OUT}/carousels/d{p['d']:02d}")
            print("carousel", p["d"], flush=True)
    else:
        for d, sc in SCRIPTS.items():
            d = int(d)
            if days and d not in days: continue
            p = next(x for x in POSTS if x["s"] == 4 and x["d"] == d)
            fr = await shoot(reel_frames(d, sc, p["t"], p["k"]), 1080, 1920, f"/tmp/fr/d{d:02d}")
            build_reel(d, fr, sc, f"{OUT}/story/story_d{d:02d}_2015.mp4")
            print("reel", d, flush=True)

asyncio.run(main())
