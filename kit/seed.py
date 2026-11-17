import asyncio, json
from rlib import CSS, IMG, shoot, esc
P=lambda k:IMG[k]['src']
pages=[
# 1 Hi
f"""<div style="position:absolute;inset:0;background:#FFF6E6"></div>
<div style="position:absolute;left:84px;top:110px;right:84px"><div class="k">Coming Monday</div>
<h1 style="font:700 140px/0.95 Fredoka;margin-top:30px;letter-spacing:-.03em">Hi.<br>I'm<br>Dumprin.</h1></div>
<img src="{P('cheer')}" style="position:absolute;right:30px;bottom:60px;height:720px">
<div style="position:absolute;left:84px;bottom:100px;font:600 34px/1.3 Figtree;color:#5F6E78;width:420px">An AI tutor for kids 5–15.<br>He won't give the answer.<br>He'll help them find it.</div>""",
# 2 Math reading science
f"""<div style="position:absolute;left:84px;top:110px;right:84px"><div class="k">The whole list</div>
<div style="font:700 118px/1.02 Fredoka;margin-top:30px;letter-spacing:-.02em"><span style="color:#FD7900">Math.</span><br><span style="color:#118078">Reading.</span><br><span style="color:#8A5210">Science.</span></div>
<p style="font:600 40px/1.25 Fredoka;margin-top:40px;width:520px">Video games, scary stories, what's for dinner? Not his department.</p></div>
<img src="{P('smirk')}" style="position:absolute;right:50px;bottom:70px;height:560px">
<div class="brand" style="left:84px;bottom:90px">Dumprin<span>.</span></div>""",
# 3 meet the curl
f"""<div style="position:absolute;left:84px;top:96px;right:84px;text-align:center"><div class="k">Meet the curl</div>
<h1 style="font:700 76px/1.05 Fredoka;margin-top:20px">It does the thinking<br>out loud.</h1></div>
<div style="position:absolute;left:40px;right:40px;top:400px;display:grid;grid-template-columns:repeat(3,1fr);gap:10px;text-align:center;font:600 28px Figtree;color:#5F6E78">
{''.join(f'<div><img src="{P(k)}" style="height:330px"><div>{t}</div></div>' for k,t in [('offer','Here to help'),('shy','Waiting for you'),('wink','Nice try'),('smirk','Not my department'),('cheer','OH!'),('hug','Good night')])}</div>""",
# 4 45 days start Monday
f"""<div style="position:absolute;inset:0;background:#0B2F3F"></div>
<div style="position:absolute;left:84px;top:110px;right:84px;color:#fff"><div class="k" style="color:#F7A440">Starts Monday, Nov 23</div>
<h1 style="font:700 112px/1 Fredoka;margin-top:30px;letter-spacing:-.02em">45 days.<br>One jar.<br>Every <span style="color:#F7A440">OH!</span></h1>
<p style="font:600 36px/1.35 Figtree;margin-top:40px;color:#C9D6DC;width:560px">Every time a kid gets it, a marble goes in. Follow along and watch it fill.</p></div>
<img src="{P('hug')}" style="position:absolute;right:40px;bottom:60px;height:560px">""",
]
asyncio.run(shoot(pages,1080,1350,"/home/claude/dumprin-campaign/seed/seed"))
