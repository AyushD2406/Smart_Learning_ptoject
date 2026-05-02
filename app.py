import tkinter as tk
from tkinter import ttk
from notes_dashboard import open_dashboard
from schedule import open_schedule

root = tk.Tk()
root.title("Smart Learning")
root.geometry("720x440")
root.state("zoomed")
root.configure(bg="#0d1b2a")

# ─── STYLE ─────────────────────────────────────────────
style = ttk.Style()
style.theme_use('clam')

# ─── LEFT PANEL (gradient canvas) ──────────────────────
left_width = 420
left_frame = tk.Canvas(root, width=left_width, highlightthickness=0, bg="#0d1b2a")
left_frame.pack(side="left", fill="y")

screen_height = root.winfo_screenheight()

for i in range(screen_height):
    r1, g1, b1 = (13,  27,  42)
    r2, g2, b2 = (26,  60,  90)
    r = int(r1 + (r2 - r1) * i / screen_height)
    g = int(g1 + (g2 - g1) * i / screen_height)
    b = int(b1 + (b2 - b1) * i / screen_height)
    left_frame.create_line(0, i, left_width, i, fill=f"#{r:02x}{g:02x}{b:02x}")

# Accent stripe on left edge
left_frame.create_rectangle(0, 0, 5, screen_height, fill="#1abc9c", outline="")

# Brand container
brand_frame = tk.Frame(left_frame, bg="#0f2233")
brand_frame.place(relx=0.5, rely=0.5, anchor="center")

# ✅ ONLY THIS TEXT CHANGED
tk.Label(brand_frame,
         text="Smart",
         font=("Segoe Script", 58, "bold"),
         fg="#1abc9c",
         bg="#0f2233").pack()

tk.Label(brand_frame,
         text="Learning",
         font=("Segoe Script", 44, "bold"),
         fg="#ffffff",
         bg="#0f2233").pack()

tk.Frame(brand_frame, bg="#1abc9c", height=3, width=220).pack(pady=14)

tk.Label(brand_frame,
         text="Make studying simple.\nMake studying smart.\nMake studying enjoyable.",
         font=("Segoe UI", 13),
         fg="#a8d8ea",
         bg="#0f2233",
         justify="center").pack(pady=6)

badge = tk.Frame(brand_frame, bg="#1abc9c")
badge.pack(pady=(16, 0))
tk.Label(badge, text="  v1.0  •  All-in-One Study App  ",
         font=("Segoe UI", 9, "bold"),
         fg="#0d1b2a", bg="#1abc9c").pack(padx=4, pady=3)

# ─── ACCENT DIVIDER ────────────────────────────────────
tk.Frame(root, bg="#1abc9c", width=3).pack(side="left", fill="y")

# ─── RIGHT PANEL ───────────────────────────────────────
right_frame = tk.Frame(root, bg="#0d1b2a")
right_frame.pack(side="right", fill="both", expand=True)

shadow = tk.Frame(right_frame, bg="#0a1520")
shadow.place(relx=0.5, rely=0.5, anchor="center", width=468, height=418)

card = tk.Frame(right_frame, bg="#162535")
card.place(relx=0.5, rely=0.5, anchor="center", width=462, height=412)

tk.Frame(card, bg="#1abc9c", height=4).pack(fill="x")

tk.Label(card,
         text="Welcome 👋",
         font=("Segoe UI", 36, "bold"),
         bg="#162535",
         fg="#ffffff").pack(pady=(28, 6))

tk.Label(card,
         text="What would you like to do today?",
         font=("Segoe UI", 13),
         bg="#162535",
         fg="#7a9bbf").pack(pady=(0, 28))

def create_option_button(parent, text, emoji, command):
    outer = tk.Frame(parent, bg="#1e3448", padx=2, pady=2)
    outer.pack(pady=10, padx=55, fill="x")

    btn = tk.Button(outer,
                    text=f"{emoji}   {text}",
                    command=command,
                    font=("Segoe UI", 13, "bold"),
                    bg="#1e3448",
                    fg="#e8f4f8",
                    activebackground="#1abc9c",
                    activeforeground="#0d1b2a",
                    bd=0,
                    relief="flat",
                    cursor="hand2",
                    anchor="w",
                    padx=20)
    btn.pack(fill="x", ipady=13)

    def on_enter(e):
        btn.configure(bg="#1abc9c", fg="#0d1b2a")
        outer.configure(bg="#1abc9c")
    def on_leave(e):
        btn.configure(bg="#1e3448", fg="#e8f4f8")
        outer.configure(bg="#1e3448")

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    outer.bind("<Enter>", on_enter)
    outer.bind("<Leave>", on_leave)

create_option_button(card, "Notes & Resources", "📘", lambda: open_dashboard(root))
create_option_button(card, "Study Schedule",    "📅", lambda: open_schedule(root))

tk.Label(card,
         text="Simple  •  Smart  •  Fun Learning",
         font=("Segoe UI", 9),
         bg="#162535",
         fg="#3d5a73").pack(side="bottom", pady=14)

root.mainloop() 