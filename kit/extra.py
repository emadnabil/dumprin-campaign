import asyncio, json, sys
sys.argv=["x","none"]
import rlib as R
X={
6:{"pose":"offer","l":[["t","How it works: Talk mode"],["k","I don't get dividing."],["d","Okay. If you had 12 cookies and 3 plates, how many on each?"],["k","Four!"],["t","They talk. He listens. Then he teaches."]]},
7:{"pose":"hug","l":[["t","A note from our founder"],["t","\"I'm a dad.\""],["t","\"Every AI tool I tried gave my son the answer.\""],["t","\"He finished faster and learned less.\""],["t","\"So we built the opposite.\""],["t","Dumprin asks, shows and waits."]]},
13:{"pose":"wink","l":[["t","How it works: Dumprin's Board"],["t","12 cookies. 3 plates. 12 ÷ 3."],["k","What's this part?"],["d","That's one plate. Let's count what's on it."],["k","And the ÷ sign?"],["d","It means share equally."],["t","Tap the part you don't get."]]},
18:{"pose":"shy","l":[["t","How it works: after a session"],["d","Time's up. Nice work!"],["t","Then grown-ups get a note:"],["t","What was practised. Where help was needed. What to try next."],["t","You were in the other room. You still know exactly what happened."]]},
35:{"pose":"hug","l":[["t","The thank-you note, in four sentences"],["d","1. Say what the gift was."],["d","2. Say how you'll use it."],["d","3. Say something about them."],["d","4. Say thank you again."],["k","Dear Grandma… OH."],["t","Writing with a real reader."]]},
37:{"pose":"stand","l":[["t","How it works: Type mode"],["k","why do you flip the second fraction when dividing"],["d","Good question. How many halves fit in 3?"],["k","…six?"],["d","So 3 ÷ ½ = 3 × 2. That's the flip."],["t","For 11 to 15: a calmer screen, the same patience."]]},
42:{"pose":"cheer","l":[["t","How it works: setting up"],["t","One parent account."],["t","Add a child. Pick their age."],["t","Set a time limit and a PIN."],["d","Hi! I'm Dumprin."],["t","A profile for each child."]]},
}
CAR={
7:{"k":"Founder Note","t":"Why I built a tutor that refuses to give answers","v":["\"I'm a dad.\" — Emad Masoud, founder","Every AI tool I tried gave my son the answer. He finished faster and learned less.","So we built the opposite.","Dumprin asks, shows and waits.","Made in Toronto. A company of eSora Labs."]},
39:{"k":"Studio","t":"How Dumprin was made","v":["Finding the shape: a drop, a seed, a question mark.","The curl: the one detail that never changes.","The expression sheet: many moods, one character.","Why gold: warm, not loud.","Made by a small team in Toronto and around the world."]},
45:{"k":"Start Here","t":"45 days of OH!: thank you","v":["45 days. 180 posts. One very full jar.","Every marble was a kid going from stuck to OH!","You told us what you want more of. We're listening.","What's next: you choose. Comment a topic.","Thank you. dumprin.com"]},
}
async def main():
    R.SCRIPTS.update({str(k):v for k,v in X.items()})
    for d,c in CAR.items():
        p={"d":d,"k":c["k"],"t":c["t"],"v":" | ".join(["Cover"]+c["v"])}
        await R.shoot(R.carousel_pages(p),1080,1350,f"{R.OUT}/carousels/d{d:02d}")
        print("car",d)
    titles={6:"Talk mode, in 20 seconds",7:"I'm a dad first",13:"Dumprin's Board",18:"What a parent sees after a session",35:"Thank-you notes, the easy way",37:"Type mode, for the older ones",42:"Setting up a child's profile"}
    kick={6:"How It Works",7:"Founder Note",13:"How It Works",18:"How It Works",35:"Writing",37:"How It Works",42:"How It Works"}
    for d,sc in X.items():
        fr=await R.shoot(R.reel_frames(d,sc,titles[d],kick[d]),1080,1920,f"/tmp/fr/x{d:02d}")
        R.build_reel(d,fr,sc,f"{R.OUT}/story/story_d{d:02d}_2015.mp4"); print("reel",d)
asyncio.run(main())
