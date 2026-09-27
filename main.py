import json
import math
import os
import random
import struct
import wave
import tkinter as tk
from tkinter import messagebox

# File paths
SAVE_FILE = "startup_v9_save.json"
SOUND_DIR = "startup_v9_sounds"

# UI Color Palette
BG = "#07111f"
PANEL = "#0d1b2a"
CARD = "#14283d"
CARD2 = "#1b3550"
TEXT = "#f8fafc"
MUTED = "#8fa6bc"
ACCENT = "#38bdf8"
GREEN = "#22c55e"
RED = "#ef4444"
YELLOW = "#facc15"
PURPLE = "#a78bfa"
ORANGE = "#fb923c"
PINK = "#f472b6"
CYAN = "#22d3ee"

# Business Types
BUSINESSES = {
    "Technology": "💻",
    "Sustainability": "🌱",
    "Food & Delivery": "🍔",
    "Gaming": "🎮"
}

# Windows sound setup
try:
    import winsound
    WINDOWS_SOUND = True
except Exception:
    WINDOWS_SOUND = False


def make_tone(path, notes, duration=0.09, volume=0.22):
    """Generates audio files using math and wave modules."""
    try:
        rate = 44100
        frames = []
        for freq in notes:
            n = int(rate * duration)
            for i in range(n):
                t = i / rate
                fade = min(1, i / (rate * 0.01), (n - i) / (rate * 0.015))
                sample = math.sin(2 * math.pi * freq * t) * volume * max(0, fade)
                frames.append(struct.pack("<h", int(sample * 32767)))
                
        with wave.open(path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(b"".join(frames))
    except Exception:
        pass


def prepare_sounds():
    """Pre-generates all sound effect files."""
    os.makedirs(SOUND_DIR, exist_ok=True)
    make_tone(os.path.join(SOUND_DIR, "click.wav"), [520], 0.06)
    make_tone(os.path.join(SOUND_DIR, "choice.wav"), [440, 660, 880], 0.07)
    make_tone(os.path.join(SOUND_DIR, "success.wav"), [523, 659, 784, 1047], 0.11)
    make_tone(os.path.join(SOUND_DIR, "bad.wav"), [330, 247, 196], 0.13)
    make_tone(os.path.join(SOUND_DIR, "event.wav"), [392, 523, 659], 0.10)
    make_tone(os.path.join(SOUND_DIR, "victory.wav"), [523, 659, 784, 1047, 1319], 0.12)


def sound(kind="click"):
    """Plays audio file if on Windows."""
    if not WINDOWS_SOUND:
        return
    p = os.path.join(SOUND_DIR, kind + ".wav")
    try:
        winsound.PlaySound(p, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception:
        pass


prepare_sounds()

# Game Events
EVENTS = [
    {
        "id": "pitch",
        "title": "🤝 Investor Pitch",
        "story": "An angel investor offers ₹40,000, but wants 15% equity. Your runway is comfortable for now.",
        "tags": ["investor"],
        "choices": [
            ("Accept the deal", "Take the funding and give away equity.", {"money": 40000, "funding": 40000, "reputation": 2}, "Investor expects fast growth.", 2),
            ("Negotiate", "Ask for ₹55,000 for the same equity.", {"money": 55000, "funding": 55000}, "The investor may respect your confidence.", 1),
            ("Walk away", "Keep full ownership and grow slowly.", {"reputation": 3}, "You keep control of the startup.", 1)
        ]
    },
    {
        "id": "pricing",
        "title": "💰 Pricing Crisis",
        "story": "Customers like the product, but many say the current price is too high.",
        "tags": ["money"],
        "choices": [
            ("Cut the price", "Make the product accessible.", {"customers": 12, "money": -5000, "reputation": 4}, "More people try the product.", 2),
            ("Keep premium pricing", "Protect your margins.", {"money": 6000, "reputation": -1}, "Revenue improves, but some customers leave.", 1),
            ("Launch a basic plan", "Create a cheaper version without changing the main plan.", {"customers": 7, "product": 1}, "A new customer segment appears.", 2)
        ]
    },
    {
        "id": "bug",
        "title": "🐛 Critical Bug",
        "story": "A serious bug is affecting a portion of your users. Social media has started noticing.",
        "tags": ["technology"],
        "choices": [
            ("Fix immediately", "Pause new development and focus on stability.", {"money": -7000, "reputation": 7}, "Users appreciate the quick response.", 2),
            ("Release a temporary patch", "Fix the worst part and keep shipping.", {"money": -2500, "reputation": 2, "product": 1}, "The situation is contained.", 1),
            ("Ignore it", "Hope users do not notice.", {"reputation": -12, "customers": -8}, "Complaints begin spreading.", 3)
        ]
    },
    {
        "id": "competitor",
        "title": "⚔️ Competitor Attack",
        "story": "A rival startup launches a very similar product with aggressive advertising.",
        "tags": ["competition"],
        "choices": [
            ("Improve your product", "Invest in differentiation.", {"money": -7000, "product": 2, "reputation": 3}, "Your product becomes harder to copy.", 2),
            ("Start a marketing war", "Spend heavily to defend your market.", {"money": -9000, "customers": 15}, "You gain attention but burn cash.", 2),
            ("Focus on a niche", "Own a smaller but loyal market.", {"customers": 8, "reputation": 8}, "Your niche audience becomes loyal.", 2)
        ]
    },
    {
        "id": "hire",
        "title": "👩‍💻 First Big Hire",
        "story": "You found a talented developer who could accelerate the product, but salary will hurt your runway.",
        "tags": ["team"],
        "choices": [
            ("Hire them", "Build a stronger technical team.", {"employees": 1, "money": -8000, "product": 2}, "Development speed increases.", 2),
            ("Part-time contract", "Use them only for the critical feature.", {"money": -3500, "product": 1}, "Lower risk, slower progress.", 1),
            ("Do it yourself", "Save money and keep control.", {"product": 0, "reputation": -1}, "You save cash but take on more work.", 2)
        ]
    },
    {
        "id": "viral",
        "title": "📱 Unexpected Viral Post",
        "story": "A customer posted a video about your startup. It suddenly gets thousands of views.",
        "tags": ["marketing"],
        "choices": [
            ("Boost the post", "Spend money while attention is high.", {"money": -4000, "customers": 30, "reputation": 5}, "The campaign takes off.", 2),
            ("Engage naturally", "Reply, repost and talk to users.", {"customers": 18, "reputation": 8}, "The community feels heard.", 2),
            ("Ignore the hype", "Stay focused on the product.", {"product": 1, "customers": 4}, "You convert fewer visitors but improve the product.", 1)
        ]
    },
    {
        "id": "supplier",
        "title": "📦 Supplier Failure",
        "story": "Your main supplier says it cannot deliver this week. Your operations are at risk.",
        "tags": ["food", "supply"],
        "choices": [
            ("Find an emergency supplier", "Pay more to avoid disruption.", {"money": -6000, "reputation": 4}, "Orders continue normally.", 2),
            ("Delay orders honestly", "Tell customers the truth and offer compensation.", {"money": -2500, "reputation": 7, "customers": -2}, "Trust remains strong.", 2),
            ("Pretend everything is fine", "Keep taking orders.", {"reputation": -10, "customers": -8}, "The delay becomes a public complaint.", 3)
        ]
    },
    {
        "id": "eco",
        "title": "🌱 Green Partnership",
        "story": "An environmental organization offers to promote your sustainability startup if you meet stricter standards.",
        "tags": ["sustainability"],
        "choices": [
            ("Accept the standards", "Spend now to become more sustainable.", {"money": -6000, "reputation": 12, "customers": 15}, "The partnership increases trust.", 2),
            ("Negotiate the requirements", "Ask for a gradual transition.", {"money": -2500, "reputation": 6, "customers": 7}, "You find a middle ground.", 1),
            ("Decline", "Avoid the extra cost.", {"money": 3000, "reputation": -4}, "You keep short-term cash.", 1)
        ]
    },
    {
        "id": "foodtrend",
        "title": "🍔 Food Trend",
        "story": "A new food trend is exploding in your city. Your kitchen can adapt, but ingredients will cost more.",
        "tags": ["food"],
        "choices": [
            ("Launch it quickly", "Ride the trend before competitors.", {"money": -4500, "customers": 25, "revenue": 4000}, "Your menu gets attention.", 2),
            ("Test it first", "Run a small experiment.", {"money": -1800, "customers": 9, "product": 1}, "You learn what customers actually want.", 2),
            ("Skip it", "Stay with your current menu.", {"reputation": 2, "money": 2500}, "Your operations stay stable.", 1)
        ]
    },
    {
        "id": "streamer",
        "title": "🎮 Streamer Challenge",
        "story": "A popular streamer wants to play your game live, but asks for a custom feature first.",
        "tags": ["gaming"],
        "choices": [
            ("Build the feature", "Spend development time to impress the streamer.", {"money": -6000, "product": 2, "customers": 35}, "The stream brings a huge audience.", 3),
            ("Offer early access", "Give the streamer the current build.", {"customers": 22, "reputation": 5}, "The audience becomes curious.", 2),
            ("Decline", "Protect your roadmap.", {"product": 1}, "You keep control of development.", 1)
        ]
    },
    {
        "id": "complaint",
        "title": "📣 Customer Complaint Storm",
        "story": "Several customers complain that support is too slow. One complaint is gaining traction.",
        "tags": ["customers"],
        "choices": [
            ("Hire support", "Invest in customer experience.", {"employees": 1, "money": -5000, "reputation": 10, "customers": 5}, "Response times improve.", 2),
            ("Personally respond", "Talk directly to the affected users.", {"reputation": 8, "customers": 3}, "Customers appreciate the founder's attention.", 1),
            ("Ignore the complaints", "Focus on growth instead.", {"reputation": -15, "customers": -10}, "The complaints spread.", 3)
        ]
    },
    {
        "id": "feature",
        "title": "🧪 Product Feature Vote",
        "story": "Users are split between two features. You can only build one this week.",
        "tags": ["product"],
        "choices": [
            ("Build the popular feature", "Follow the majority.", {"product": 2, "customers": 10, "money": -5000}, "Most users are happy.", 2),
            ("Build the risky feature", "Choose the idea with bigger upside.", {"product": 3, "money": -7000}, "It could become your differentiator.", 3),
            ("Run a paid experiment", "Test both with a small group.", {"money": -2500, "product": 1, "reputation": 3}, "You get useful data.", 2)
        ]
    },
    {
        "id": "burnout",
        "title": "🧠 Founder Burnout",
        "story": "You have been doing product, hiring, support and marketing yourself. Your team notices the pressure.",
        "tags": ["team"],
        "choices": [
            ("Delegate", "Give responsibility to the team.", {"reputation": 6, "employees": 1, "money": -3000}, "The company becomes less dependent on you.", 2),
            ("Push harder", "Work through the week.", {"product": 1, "customers": 5, "reputation": -5}, "Short-term output rises.", 2),
            ("Take a reset day", "Slow down and reorganize.", {"reputation": 5, "money": -1500}, "The team returns with clearer priorities.", 1)
        ]
    },
    {
        "id": "cash",
        "title": "🚨 Cash Runway Warning",
        "story": "Your finance sheet shows only a few weeks of comfortable runway.",
        "tags": ["money"],
        "choices": [
            ("Cut unnecessary spending", "Protect cash immediately.", {"money": 7000, "reputation": -1}, "Runway improves.", 2),
            ("Increase marketing", "Bet on faster growth.", {"money": -5000, "customers": 25}, "Growth accelerates if the bet works.", 2),
            ("Seek funding", "Start investor conversations.", {"funding": 15000, "money": 15000, "reputation": 2}, "You buy more runway.", 2)
        ]
    },
    {
        "id": "data",
        "title": "📊 Data Mystery",
        "story": "Your dashboard shows traffic rising but purchases falling. Something in the funnel is broken.",
        "tags": ["analytics"],
        "choices": [
            ("Analyze the funnel", "Find the exact drop-off point.", {"money": -1500, "reputation": 5, "customers": 12}, "You discover a conversion problem.", 2),
            ("Run a discount", "Try to recover purchases quickly.", {"money": -3500, "customers": 18}, "Sales return, but margins shrink.", 1),
            ("Ignore the numbers", "Trust your instincts.", {"reputation": -6, "customers": -6}, "The problem gets worse.", 2)
        ]
    },
    {
        "id": "media",
        "title": "📰 Media Interview",
        "story": "A local tech publication wants to interview you about your startup journey.",
        "tags": ["reputation"],
        "choices": [
            ("Do the interview", "Tell your story honestly.", {"reputation": 10, "customers": 12}, "People discover your startup.", 2),
            ("Talk only about the product", "Keep the interview focused.", {"reputation": 5, "customers": 6, "product": 1}, "The product gets attention.", 1),
            ("Decline", "Avoid public exposure.", {"reputation": 1}, "You remain private.", 1)
        ]
    },
    {
        "id": "security",
        "title": "🔐 Security Alert",
        "story": "You discover suspicious login attempts. No data is confirmed stolen, but users are asking questions.",
        "tags": ["technology"],
        "choices": [
            ("Invest in security", "Fix the weakness before anything happens.", {"money": -7000, "reputation": 12, "product": 1}, "Trust in the platform rises.", 2),
            ("Force password resets", "Take a quick defensive step.", {"money": -2500, "reputation": 5}, "Risk is reduced.", 1),
            ("Say nothing", "Avoid alarming users.", {"reputation": -14, "customers": -7}, "Rumors become worse than the original issue.", 3)
        ]
    },
    {
        "id": "festival",
        "title": "🎉 Local Startup Festival",
        "story": "A major startup festival offers you a small booth. It costs money, but hundreds of potential customers will attend.",
        "tags": ["marketing"],
        "choices": [
            ("Book the booth", "Meet customers face-to-face.", {"money": -4500, "customers": 28, "reputation": 7}, "Your brand becomes more visible.", 2),
            ("Partner with another startup", "Split the cost.", {"money": -2200, "customers": 16, "reputation": 5}, "You build a useful connection.", 2),
            ("Skip it", "Save the cash.", {"money": 2500}, "Your runway improves.", 1)
        ]
    },
    {
        "id": "employeeconflict",
        "title": "⚡ Team Conflict",
        "story": "Two employees disagree about the product direction. Productivity is falling.",
        "tags": ["team"],
        "choices": [
            ("Mediate", "Hear both sides and set clear ownership.", {"reputation": 7, "product": 1}, "The team becomes more aligned.", 2),
            ("Choose one side", "Make a fast decision.", {"product": 2, "reputation": -4}, "Progress is faster but someone feels ignored.", 2),
            ("Ignore it", "Let them solve it themselves.", {"reputation": -10, "product": -1}, "The conflict grows.", 3)
        ]
    },
    {
        "id": "refund",
        "title": "💳 Refund Request",
        "story": "A group of customers requests refunds after misunderstanding a feature description.",
        "tags": ["customers"],
        "choices": [
            ("Refund everyone", "Protect long-term trust.", {"money": -5000, "reputation": 12, "customers": 2}, "Your transparency earns respect.", 2),
            ("Refund case-by-case", "Investigate each complaint.", {"money": -2200, "reputation": 6}, "You balance fairness and cost.", 1),
            ("Reject refunds", "Stick strictly to the policy.", {"reputation": -10, "customers": -7}, "Some customers leave.", 2)
        ]
    },
    {
        "id": "expansion",
        "title": "🌍 Expansion Opportunity",
        "story": "Customers from another city are asking when you will launch there.",
        "tags": ["growth"],
        "choices": [
            ("Expand now", "Move quickly into the new market.", {"money": -9000, "customers": 35, "reputation": 3}, "The new market responds well.", 3),
            ("Pilot the city", "Start with a small launch.", {"money": -3500, "customers": 16, "product": 1}, "You learn before scaling.", 2),
            ("Stay focused", "Perfect the current market first.", {"product": 2, "reputation": 4}, "Your core market gets stronger.", 2)
        ]
    },
    {
        "id": "ethics",
        "title": "⚖️ Growth vs Trust",
        "story": "A marketing agency offers a campaign using exaggerated claims that could bring many clicks.",
        "tags": ["reputation"],
        "choices": [
            ("Use honest marketing", "Grow more slowly with accurate claims.", {"customers": 10, "reputation": 10}, "Trust compounds over time.", 2),
            ("Use the aggressive campaign", "Prioritize short-term traffic.", {"customers": 30, "reputation": -12, "money": 5000}, "Traffic rises, but trust falls.", 2),
            ("Walk away", "Keep your brand standards.", {"reputation": 7, "money": -1000}, "You protect the brand.", 1)
        ]
    },
    {
        "id": "award",
        "title": "🏆 Startup Award Nomination",
        "story": "Your startup has been nominated for a young founder award. You can spend money preparing a strong presentation.",
        "tags": ["reputation"],
        "choices": [
            ("Prepare seriously", "Invest in the presentation.", {"money": -2500, "reputation": 12, "customers": 8}, "Your story gets noticed.", 2),
            ("Submit a simple entry", "Spend almost nothing.", {"reputation": 5}, "You participate without losing focus.", 1),
            ("Skip it", "Stay focused on operations.", {"product": 1, "money": 1500}, "The product gets your attention.", 1)
        ]
    },
    {
        "id": "late",
        "title": "🌙 Late-Night Emergency",
        "story": "An important service goes down at midnight. Customers are waiting for an update.",
        "tags": ["crisis"],
        "choices": [
            ("Fix it personally", "Take control immediately.", {"reputation": 8, "money": -3000}, "The service returns quickly.", 2),
            ("Call the team", "Distribute the problem among specialists.", {"employees": 1, "reputation": 6, "money": -2000}, "The team handles it together.", 2),
            ("Wait until morning", "Avoid disturbing the team.", {"reputation": -14, "customers": -9}, "Users lose patience.", 3)
        ]
    }
]


class StoryEngine:
    def generate(self, g):
        bt = g["business_type"]
        recent = set(g.get("recent_events", []))
        candidates = []
        
        for e in EVENTS:
            if e["id"] in recent:
                continue
            ok = True
            tags = e["tags"]
            
            if "technology" in tags and bt != "Technology":
                ok = False
            if "sustainability" in tags and bt != "Sustainability":
                ok = False
            if "food" in tags and bt != "Food & Delivery":
                ok = False
            if "gaming" in tags and bt != "Gaming":
                ok = False
                
            if ok:
                candidates.append(e)
                
        if not candidates:
            candidates = EVENTS[:]
            
        weighted = []
        for e in candidates:
            w = 1
            if g["money"] < 15000 and "money" in e["tags"]:
                w += 5
            if g["reputation"] < 35 and "reputation" in e["tags"]:
                w += 4
            if g["customers"] > 50 and "growth" in e["tags"]:
                w += 3
            if len(g["employees"]) >= 2 and "team" in e["tags"]:
                w += 3
            weighted += [e] * w
            
        return random.choice(weighted)


def apply_effects(g, effects):
    for k, v in effects.items():
        if k == "employees":
            for _ in range(max(0, v)):
                role = random.choice(["Developer", "Designer", "Marketing", "Analyst"])
                g["employees"].append(role)
        elif k == "revenue":
            g["revenue"] += v
        elif k == "funding":
            g["funding"] += v
        elif k in g and isinstance(g[k], (int, float)):
            g[k] += v
            
    g["money"] = max(-999999, g["money"])
    g["customers"] = max(0, g["customers"])
    g["reputation"] = max(0, min(100, g["reputation"]))
    g["product"] = max(1, min(10, g["product"]))


class Game:
    def __init__(self, root):
        self.root = root
        self.game = None
        self.event = None
        self.history = []
        self.root.title("EQUITY & CHAOS — V9")
        self.root.geometry("1100x720")
        self.root.minsize(900, 650)
        self.root.configure(bg=BG)
        self.show_home()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def label(self, parent, text, size=12, color=TEXT, **kw):
        return tk.Label(parent, text=text, bg=parent.cget("bg"), fg=color,
                        font=("Segoe UI", size), **kw)

    def button(self, parent, text, command, bg=CARD2, width=20):
        b = tk.Button(parent, text=text, command=command, bg=bg, fg=TEXT,
                      activebackground=ACCENT, activeforeground="#001018",
                      font=("Segoe UI", 11, "bold"), relief="flat", bd=0,
                      padx=10, pady=10, width=width, cursor="hand2")
        b.bind("<Enter>", lambda e: b.config(bg=ACCENT, fg="#001018"))
        b.bind("<Leave>", lambda e: b.config(bg=bg, fg=TEXT))
        return b

    def card(self, parent, bg=PANEL, **kw):
        return tk.Frame(parent, bg=bg, bd=0, **kw)

    def show_home(self):
        self.clear()
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=55, pady=45)

        self.label(main, "EQUITY & CHAOS", 34, ACCENT).pack(pady=(25, 3))
        self.label(main, "STARTUP DECISION SIMULATOR", 13, MUTED).pack()
        self.label(main, "Build your startup. Make hard choices. Survive 10 days.", 12, TEXT).pack(pady=15)

        box = self.card(main, CARD, padx=35, pady=25)
        box.pack(pady=10)
        for text, cmd, color in [
            ("🚀  NEW GAME", self.new_game, ACCENT),
            ("▶  CONTINUE", self.load_game, CARD2),
            ("🏆  ACHIEVEMENTS", self.achievements, CARD2),
            ("❓  HOW TO PLAY", self.how, CARD2),
            ("✕  EXIT", self.root.destroy, RED)
        ]:
            self.button(box, text, cmd, color, 25).pack(fill="x", pady=5)

        self.label(main, "V9  •  Every decision changes your startup.", 10, MUTED).pack(side="bottom")

    def new_game(self):
        self.clear()
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=70, pady=40)
        self.label(main, "CREATE YOUR STARTUP", 28, ACCENT).pack(pady=(5, 4))
        self.label(main, "Enter your details and choose a business type.", 11, MUTED).pack(pady=(0, 20))

        form = self.card(main, PANEL, padx=35, pady=25)
        form.pack()

        self.label(form, "Founder name", 10, MUTED).pack(anchor="w")
        name = tk.Entry(form, font=("Segoe UI", 13), bg=CARD, fg=TEXT,
                        insertbackground=TEXT, relief="flat", width=34)
        name.pack(pady=(5, 15), ipady=7)

        self.label(form, "Startup name", 10, MUTED).pack(anchor="w")
        startup = tk.Entry(form, font=("Segoe UI", 13), bg=CARD, fg=TEXT,
                           insertbackground=TEXT, relief="flat", width=34)
        startup.pack(pady=(5, 15), ipady=7)

        self.label(form, "Choose your business", 10, MUTED).pack(anchor="w")
        typ = tk.StringVar(value="Technology")
        choices = tk.Frame(form, bg=PANEL)
        choices.pack(pady=8)

        for i, (name_type, icon) in enumerate(BUSINESSES.items()):
            tk.Radiobutton(choices, text=f"{icon}\n{name_type}", variable=typ,
                           value=name_type, indicatoron=False, width=16, height=3,
                           bg=CARD, fg=TEXT, selectcolor=ACCENT,
                           activebackground=ACCENT, activeforeground="#001018",
                           font=("Segoe UI", 10, "bold"), relief="flat").grid(
                               row=i // 2, column=i % 2, padx=5, pady=5)

        def start():
            if not name.get().strip() or not startup.get().strip():
                messagebox.showwarning("Missing details", "Enter both names.")
                return
            self.game = {
                "founder": name.get().strip(), "startup": startup.get().strip(),
                "business_type": typ.get(), "day": 1, "money": 50000,
                "customers": 10, "revenue": 0, "reputation": 50, "product": 1,
                "employees": [], "funding": 0, "decisions": [], "recent_events": [],
                "achievements": [], "score": 0
            }
            self.history = []
            self.event = None
            self.next_event()

        self.button(main, "START SIMULATION 🚀", start, ACCENT, 28).pack(pady=18)
        self.button(main, "BACK", self.show_home, CARD2, 15).pack()

    def stat_card(self, parent, title, value, color):
        c = self.card(parent, CARD, padx=12, pady=10)
        c.pack(side="left", fill="x", expand=True, padx=4)
        self.label(c, title, 9, MUTED).pack()
        self.label(c, value, 14, color).pack(pady=(4, 0))

    def header(self):
        top = tk.Frame(self.root, bg=PANEL)
        top.pack(fill="x", padx=0, pady=0)
        g = self.game
        tk.Frame(top, bg=ACCENT, height=3).pack(fill="x")
        row = tk.Frame(top, bg=PANEL)
        row.pack(fill="x", padx=22, pady=10)
        self.label(row, f"{BUSINESSES[g['business_type']]}  {g['startup']}", 17, ACCENT).pack(side="left")
        self.label(row, f"DAY {g['day']} / 10", 12, YELLOW).pack(side="right")

        stats = tk.Frame(top, bg=PANEL)
        stats.pack(fill="x", padx=18, pady=(0, 10))
        self.stat_card(stats, "💰 MONEY", f"₹{g['money']:,}", GREEN if g['money'] >= 0 else RED)
        self.stat_card(stats, "👥 CUSTOMERS", str(g['customers']), ACCENT)
        self.stat_card(stats, "⭐ REPUTATION", f"{g['reputation']}/100", YELLOW)
        self.stat_card(stats, "🧪 PRODUCT", f"Lv.{g['product']}", PURPLE)
        self.stat_card(stats, "👩‍💻 TEAM", str(len(g['employees'])), ORANGE)

    def progress(self, parent):
        bar = tk.Frame(parent, bg=CARD, height=8)
        bar.pack(fill="x", pady=(0, 18))
        fill = tk.Frame(bar, bg=ACCENT, height=8)
        fill.place(relwidth=min(self.game['day'] / 10, 1), relheight=1)

    def next_event(self):
        if self.game["day"] > 10:
            return self.final()
        self.event = StoryEngine().generate(self.game)
        self.game["recent_events"].append(self.event["id"])
        self.game["recent_events"] = self.game["recent_events"][-7:]
        self.show_event()

    def show_event(self):
        self.clear()
        self.header()
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=45, pady=20)
        self.progress(body)

        self.label(body, "TODAY'S BUSINESS CHALLENGE", 10, MUTED).pack(anchor="w")
        self.label(body, self.event["title"], 25, TEXT).pack(anchor="w", pady=(3, 12))

        story = self.card(body, PANEL, padx=25, pady=20)
        story.pack(fill="x")
        self.label(story, self.event["story"], 13, TEXT, wraplength=900,
                   justify="left").pack(anchor="w")

        self.label(body, "WHAT WILL YOU DO?", 11, ACCENT).pack(anchor="w", pady=(18, 8))
        for i, ch in enumerate(self.event["choices"]):
            title, desc, effects, result, days = ch
            b = self.button(body, f"{i + 1}. {title}   —   {desc}",
                            lambda c=ch: self.choose(c), CARD2, 20)
            b.pack(fill="x", pady=4)

        bar = tk.Frame(self.root, bg=PANEL)
        bar.pack(fill="x", side="bottom")
        self.button(bar, "💾 SAVE", self.save_game, CARD2, 10).pack(side="left", padx=7, pady=7)
        self.button(bar, "📜 HISTORY", self.show_history, CARD2, 12).pack(side="left", padx=7, pady=7)
        self.button(bar, "📊 STATS", self.show_stats, CARD2, 10).pack(side="right", padx=7, pady=7)
        self.button(bar, "🏆", self.achievements, CARD2, 5).pack(side="right", padx=7, pady=7)
        sound("event")

    def choose(self, choice):
        title, desc, effects, result, days = choice
        before = self.game["money"]
        apply_effects(self.game, effects)
        self.game["decisions"].append({"day": self.game["day"], "event": self.event["title"], "choice": title})
        self.history.append(f"Day {self.game['day']}: {title}")
        self.check_achievements()
        delta = self.game["money"] - before
        sound("success" if delta >= 0 else "bad")
        self.show_result(title, result, effects)

    def show_result(self, choice, result, effects):
        self.clear()
        self.header()
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=80, pady=35)
        self.label(body, "DECISION MADE", 11, ACCENT).pack()
        self.label(body, choice, 26, TEXT).pack(pady=(6, 18))

        card = self.card(body, PANEL, padx=30, pady=25)
        card.pack(fill="x")
        self.label(card, result, 14, TEXT, wraplength=820, justify="left").pack(anchor="w")

        self.label(card, "STAT CHANGES", 10, MUTED).pack(anchor="w", pady=(18, 7))
        for key, value in effects.items():
            if value:
                color = GREEN if value > 0 else RED
                self.label(card, f"{key.title()}: {'+' if value > 0 else ''}{value}", 11, color).pack(anchor="w")

        self.button(body, "CONTINUE →", self.advance, ACCENT, 25).pack(pady=28)

    def advance(self):
        self.game["day"] += 1
        self.next_event()

    def check_achievements(self):
        g, a = self.game, self.game["achievements"]
        checks = [
            ("First Growth", g["customers"] >= 20),
            ("Great Reputation", g["reputation"] >= 80),
            ("Team Builder", len(g["employees"]) >= 2),
            ("Product Machine", g["product"] >= 5),
            ("Rich Founder", g["money"] >= 80000),
            ("Market Leader", g["customers"] >= 100)
        ]
        for name, ok in checks:
            if ok and name not in a:
                a.append(name)

    def calculate_score(self):
        g = self.game
        score = (g["customers"] * 2 + g["reputation"] * 2 + g["product"] * 20 +
                 len(g["employees"]) * 20 + g["funding"] // 1000 +
                 len(g["achievements"]) * 25 + max(0, g["money"] - 50000) // 500)
        return min(850, score)

    def final(self):
        self.game["score"] = self.calculate_score()
        s = self.game["score"]
        if self.game["money"] <= 0 and self.game["reputation"] < 20:
            ending = "💀 STARTUP COLLAPSE"
        elif s >= 650:
            ending = "🚀 STARTUP EMPIRE"
        elif s >= 450:
            ending = "📈 SCALE-UP SUCCESS"
        elif s >= 250:
            ending = "🧩 THE SURVIVOR"
        else:
            ending = "🌱 EARLY STAGE STARTUP"

        sound("victory" if s >= 250 else "bad")
        self.clear()
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=80, pady=35)
        self.label(main, "DAY 10 COMPLETE", 12, ACCENT).pack(pady=(5, 5))
        self.label(main, ending, 30, TEXT).pack()
        self.label(main, f"STARTUP SCORE  {s}", 19, YELLOW).pack(pady=12)

        g = self.game
        card = self.card(main, PANEL, padx=30, pady=22)
        card.pack(fill="x", pady=5)
        stats = (f"💰 Money: ₹{g['money']:,}     👥 Customers: {g['customers']}\n"
                 f"⭐ Reputation: {g['reputation']}     🧪 Product: Lv.{g['product']}\n"
                 f"👩‍💻 Employees: {len(g['employees'])}     🏆 Achievements: {len(g['achievements'])}")
        self.label(card, stats, 12, TEXT, justify="center").pack()

        self.button(main, "💾 SAVE FINAL REPORT", self.save_game, ACCENT, 24).pack(pady=12)
        self.button(main, "🏆 ACHIEVEMENTS", self.achievements, CARD2, 24).pack(pady=4)
        self.button(main, "🔄 PLAY AGAIN", self.new_game, PURPLE, 24).pack(pady=4)
        self.button(main, "HOME", self.show_home, CARD2, 24).pack(pady=4)

    def save_game(self):
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.game, f, indent=2)
            messagebox.showinfo("Saved", "Your startup has been saved.")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def load_game(self):
        if not os.path.exists(SAVE_FILE):
            messagebox.showinfo("No Save", "No saved game found.")
            return
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                self.game = json.load(f)
            self.event = None
            self.history = [f"Day {d['day']}: {d['choice']}" for d in self.game.get("decisions", [])]
            self.next_event()
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def show_history(self):
        self.clear()
        self.header()
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=45, pady=25)
        self.label(body, "📜 DECISION HISTORY", 24, ACCENT).pack(anchor="w", pady=(0, 12))
        box = tk.Text(body, bg=PANEL, fg=TEXT, font=("Consolas", 11), relief="flat",
                      padx=15, pady=15)
        box.pack(fill="both", expand=True)
        box.insert("end", "\n".join(self.history) or "No decisions yet.")
        box.config(state="disabled")
        self.button(body, "← BACK", self.show_event, CARD2, 15).pack(pady=12)

    def show_stats(self):
        self.clear()
        self.header()
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=70, pady=30)
        self.label(body, "📊 STARTUP ANALYTICS", 25, ACCENT).pack(anchor="w", pady=10)
        g = self.game
        data = (f"Startup Score: {self.calculate_score()}\n\n"
                f"💰 Cash: ₹{g['money']:,}\n👥 Customers: {g['customers']}\n"
                f"💵 Revenue: ₹{g['revenue']:,}\n⭐ Reputation: {g['reputation']}/100\n"
                f"🧪 Product Level: {g['product']}\n👩‍💻 Employees: {len(g['employees'])}\n"
                f"💼 Funding: ₹{g['funding']:,}\n\n"
                f"Decisions made: {len(g['decisions'])}")
        card = self.card(body, PANEL, padx=30, pady=25)
        card.pack(fill="x", pady=10)
        self.label(card, data, 14, TEXT, justify="left").pack(anchor="w")
        self.button(body, "← BACK", self.show_event, CARD2, 15).pack(pady=10)

    def achievements(self):
        self.clear()
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=70, pady=45)
        self.label(body, "🏆 ACHIEVEMENTS", 28, YELLOW).pack(pady=(5, 20))
        names = ["First Growth", "Great Reputation", "Team Builder", "Product Machine", "Rich Founder", "Market Leader"]
        got = self.game["achievements"] if self.game else []
        for name in names:
            unlocked = name in got
            c = self.card(body, CARD if unlocked else PANEL, padx=18, pady=10)
            c.pack(fill="x", pady=4)
            self.label(c, ("✅ " if unlocked else "🔒 ") + name,
                       12, GREEN if unlocked else MUTED).pack(anchor="w")
        back = self.show_event if self.game and self.event else self.show_home
        self.button(body, "← BACK", back, CARD2, 15).pack(pady=20)

    def how(self):
        self.clear()
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=80, pady=55)
        self.label(body, "❓ HOW TO PLAY", 28, ACCENT).pack()
        text = ("You are the founder of a new startup.\n\n"
                "Each day gives you a different business situation.\n"
                "Choose one of three options and watch your startup stats change.\n\n"
                "Manage money, customers, reputation and product level.\n"
                "Survive 10 days and try to build the strongest startup possible.\n\n"
                "Tip: There is no perfect choice. Every decision has a trade-off!")
        card = self.card(body, PANEL, padx=30, pady=25)
        card.pack(pady=20, fill="x")
        self.label(card, text, 13, TEXT, wraplength=800, justify="left").pack()
        self.button(body, "← BACK", self.show_home, CARD2, 15).pack()


if __name__ == "__main__":
    root = tk.Tk()
    Game(root)
    root.mainloop()
