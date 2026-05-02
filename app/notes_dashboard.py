import tkinter as tk
from add_notes import open_add_notes_window
from video import open_videos_window
from past_papers import open_past_papers

BG_DARK  = "#0a0f1e"
BG_PANEL = "#0d1e36"
BG_CARD  = "#112236"
FONT     = "Segoe UI"
TEXT     = "#dfe6e9"
MUTED    = "#5a7a94"


def open_dashboard(parent):
    dash = tk.Toplevel(parent)
    dash.title("Notes Dashboard")
    dash.state("zoomed")
    dash.resizable(True, True)
    dash.configure(bg=BG_DARK)

    bg_canvas = tk.Canvas(dash, highlightthickness=0, bg=BG_DARK)
    bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

    def draw_gradient(event=None):
        w = dash.winfo_width()
        h = dash.winfo_height()
        bg_canvas.delete("grad")
        for i in range(h):
            t = i / max(h, 1)
            if t < 0.5:
                t2 = t / 0.5
                r = int(10 + (13-10)*t2); g = int(15 + (30-15)*t2); b = int(30 + (54-30)*t2)
            else:
                t2 = (t-0.5)/0.5
                r = int(13 + (8-13)*t2); g = int(30 + (20-30)*t2); b = int(54 + (38-54)*t2)
            bg_canvas.create_line(0, i, w, i, fill=f"#{r:02x}{g:02x}{b:02x}", tags="grad")
        bg_canvas.lower("grad")

    dash.bind("<Configure>", draw_gradient)
    dash.after(30, draw_gradient)

    tk.Frame(dash, bg="#0984e3", height=5).place(x=0, y=0, relwidth=1)
    tk.Frame(dash, bg="#6c5ce7", height=2).place(x=0, y=5, relwidth=1)

    header = tk.Frame(dash, bg=BG_PANEL)
    header.pack(fill="x", pady=(7, 0))
    tk.Label(header, text="📚  Notes Dashboard",
             font=(FONT, 22, "bold"), bg=BG_PANEL, fg=TEXT).pack(pady=(22, 5))
    tk.Label(header, text="Choose what you'd like to access",
             font=(FONT, 12), bg=BG_PANEL, fg=MUTED).pack(pady=(0, 18))

    cards_container = tk.Frame(dash, bg=BG_DARK)
    cards_container.pack(fill="both", expand=True)

    card_w = 210; card_h = 270; gap = 30
    total_w = card_w * 3 + gap * 2

    holder = tk.Frame(cards_container, bg=BG_DARK)
    holder.place(relx=0.5, rely=0.5, anchor="center", width=total_w+6, height=card_h+6)

    cards_info = [
        ("🎬", "Videos",      "Watch lecture videos\n& tutorials",   lambda: open_videos_window(dash),    "#0984e3"),
        ("✍️",  "Notes",       "Browse textbooks\n& study PDFs",      lambda: open_add_notes_window(dash), "#6c5ce7"),
        ("📄", "Past Papers", "Find & open past\nexam papers",        lambda: open_past_papers(dash),      "#fd9644"),
    ]

    for col, (emoji, title, subtitle, cmd, accent) in enumerate(cards_info):
        xp = col * (card_w + gap)

        shadow = tk.Frame(holder, bg="#040a12", width=card_w, height=card_h)
        shadow.place(x=xp+3, y=3)

        card = tk.Frame(holder, bg=BG_CARD, width=card_w, height=card_h)
        card.place(x=xp, y=0)
        card.pack_propagate(False)

        top_bar    = tk.Frame(card, bg=accent, height=5); top_bar.pack(fill="x")
        emoji_lbl  = tk.Label(card, text=emoji, font=("Segoe UI Emoji",36), bg=BG_CARD, fg=accent); emoji_lbl.pack(pady=(22,4))
        title_lbl  = tk.Label(card, text=title, font=(FONT,14,"bold"), bg=BG_CARD, fg=TEXT); title_lbl.pack()
        sub_lbl    = tk.Label(card, text=subtitle, font=(FONT,10), bg=BG_CARD, fg=MUTED, justify="center"); sub_lbl.pack(pady=(6,18))
        btn        = tk.Button(card, text="Open →", font=(FONT,10,"bold"),
                               bg=accent, fg="#ffffff", activebackground="#ffffff", activeforeground=BG_DARK,
                               bd=0, relief="flat", cursor="hand2", command=cmd)
        btn.pack(ipadx=22, ipady=8)

        all_w = [card, top_bar, emoji_lbl, title_lbl, sub_lbl]

        def make_hover(widgets, shd, ac, button):
            def on_enter(e):
                shd.configure(bg=ac)
                for w in widgets:
                    try: w.configure(bg="#1a3450")
                    except: pass
                widgets[1].configure(bg=ac)
            def on_leave(e):
                shd.configure(bg="#040a12")
                for w in widgets:
                    try: w.configure(bg=BG_CARD)
                    except: pass
                widgets[1].configure(bg=ac)
            for w in widgets:
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)
                w.bind("<Button-1>", lambda e, b=button: b.invoke())

        make_hover(all_w, shadow, accent, btn)

    tk.Label(dash, text="Smart Learning  •  Notes Dashboard",
             font=(FONT,9), bg=BG_DARK, fg="#1e3448").pack(side="bottom", pady=10)
