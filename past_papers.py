import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import pandas as pd
import os

# ── File name — must be in same folder as this script ─────────
PAST_PAPERS_FILE = "Past_Papers_UPDATED.xlsx"

_df            = None
_link_column   = None
_has_class_deg = False

def _load_data():
    global _df, _link_column, _has_class_deg
    if _df is not None:
        return True

    if not os.path.exists(PAST_PAPERS_FILE):
        messagebox.showerror(
            "File Not Found",
            f"Cannot find '{PAST_PAPERS_FILE}'.\n\n"
            "Make sure Past_Papers_UPDATED.xlsx is in the SAME folder as this script."
        )
        return False

    try:
        df = pd.read_excel(PAST_PAPERS_FILE)
        df.columns = df.columns.str.strip()
    except Exception as e:
        messagebox.showerror("Load Error", f"Could not open the Excel file:\n{e}")
        return False

    # Year — keep as STRING so both "2023" and "2023-2024" work
    year_cols = [c for c in df.columns if "year" in c.lower()]
    if not year_cols:
        messagebox.showerror("Error", "No Year column found in the Excel file!")
        return False
    df["Year"] = df[year_cols[0]].astype(str).str.strip()
    for c in year_cols:
        if c != "Year":
            df.drop(columns=c, inplace=True, errors="ignore")

    # Remove blank year rows
    df = df[df["Year"].notna() & (df["Year"] != "") & (df["Year"].str.lower() != "nan")]

    # Link column
    link_cols = [c for c in df.columns if "link" in c.lower() or "url" in c.lower()]
    if not link_cols:
        messagebox.showerror("Error", "No Link/URL column found in the Excel file!")
        return False
    _link_column = link_cols[0]

    if "Subject" not in df.columns:
        messagebox.showerror("Error", "No 'Subject' column found!")
        return False
    if "Level" not in df.columns:
        messagebox.showerror("Error", "No 'Level' column found!")
        return False

    df = df.dropna(subset=["Level", "Subject", _link_column])
    df = df[df[_link_column].astype(str).str.strip() != ""]

    _has_class_deg = "Class/Degree" in df.columns
    _df = df
    return True


# ── Colours ───────────────────────────────────────────────────
BG_DARK    = "#0d1b2a"
BG_PANEL   = "#0f2233"
BG_CARD    = "#162535"
BG_INPUT   = "#1e3448"
ACCENT     = "#fd9644"
ACCENT_HOV = "#e07830"
ACCENT2    = "#0984e3"
TEXT       = "#e8f4f8"
MUTED      = "#5a7a94"
BORDER     = "#1e3448"
SUCCESS    = "#55efc4"
ERROR      = "#e17055"
FONT       = "Segoe UI"


def _pill(parent, text, command, w=300, h=52, bg=ACCENT, fg="#0d1b2a", fs=13, r=12):
    cvs = tk.Canvas(parent, width=w, height=h,
                    bg=parent["bg"], highlightthickness=0, cursor="hand2")

    def draw(fill):
        cvs.delete("all")
        x1, y1, x2, y2 = 2, 2, w - 2, h - 2
        for sx, sy, st, ext in [
            (x1,      y1,       90, 90),
            (x2-2*r,  y1,        0, 90),
            (x1,      y2-2*r,  180, 90),
            (x2-2*r,  y2-2*r,  270, 90),
        ]:
            cvs.create_arc(sx, sy, sx+2*r, sy+2*r,
                           start=st, extent=ext, fill=fill, outline=fill)
        cvs.create_rectangle(x1+r, y1,   x2-r, y2,   fill=fill, outline=fill)
        cvs.create_rectangle(x1,   y1+r, x2,   y2-r, fill=fill, outline=fill)
        cvs.create_text(w//2, h//2, text=text, font=(FONT, fs, "bold"), fill=fg)

    draw(bg)
    hover = ACCENT_HOV if bg == ACCENT else "#2d74c4"
    cvs.bind("<Enter>",    lambda e: draw(hover))
    cvs.bind("<Leave>",    lambda e: draw(bg))
    cvs.bind("<Button-1>", lambda e: command())
    return cvs


def open_past_papers(parent):
    if not _load_data():
        return
    df = _df

    win = tk.Toplevel(parent)
    win.title("Past Papers Finder")
    win.state("zoomed")
    win.resizable(True, True)
    win.configure(bg=BG_DARK)

    # ── TTK style ─────────────────────────────────────────────
    sty = ttk.Style(win)
    sty.theme_use("clam")
    sty.configure("PP.TCombobox",
                  fieldbackground=BG_INPUT, background=BG_INPUT,
                  foreground=TEXT, selectbackground=ACCENT2,
                  selectforeground=TEXT, bordercolor=BORDER,
                  arrowcolor=ACCENT, relief="flat",
                  padding=(10, 7), font=(FONT, 11))
    sty.map("PP.TCombobox",
            fieldbackground=[("readonly", BG_INPUT), ("focus", BG_INPUT)],
            bordercolor=[("focus", ACCENT2)],
            arrowcolor=[("hover", ACCENT_HOV)])

    # ── Top bars ──────────────────────────────────────────────
    tk.Frame(win, bg=ACCENT2, height=5).pack(fill="x")
    tk.Frame(win, bg=ACCENT,  height=2).pack(fill="x")

    # ── Header ────────────────────────────────────────────────
    banner = tk.Frame(win, bg=BG_PANEL, height=90)
    banner.pack(fill="x")
    banner.pack_propagate(False)
    tk.Label(banner, text="📄",
             font=("Segoe UI Emoji", 26), bg=BG_PANEL, fg=ACCENT
             ).place(x=28, rely=0.5, anchor="w")
    tk.Label(banner, text="Past Papers Finder",
             font=(FONT, 22, "bold"), bg=BG_PANEL, fg=TEXT
             ).place(x=76, y=14)
    tk.Label(banner,
             text="Pick your level → class → subject → year, then click Open.",
             font=(FONT, 10), bg=BG_PANEL, fg=MUTED
             ).place(x=76, y=54)

    # ── Scrollable body ───────────────────────────────────────
    scroll_outer = tk.Frame(win, bg=BG_DARK)
    scroll_outer.pack(fill="both", expand=True)

    canvas = tk.Canvas(scroll_outer, bg=BG_DARK, highlightthickness=0)
    vscroll = ttk.Scrollbar(scroll_outer, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vscroll.set)
    vscroll.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    page = tk.Frame(canvas, bg=BG_DARK)
    win_id = canvas.create_window((0, 0), window=page, anchor="nw")

    def on_canvas_resize(e):
        canvas.itemconfig(win_id, width=e.width)
    def on_frame_resize(e):
        canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.bind("<Configure>", on_canvas_resize)
    page.bind("<Configure>",   on_frame_resize)

    def on_mousewheel(e):
        canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", on_mousewheel)

    # ── Centred card ──────────────────────────────────────────
    card_wrap = tk.Frame(page, bg=BG_DARK)
    card_wrap.pack(expand=True, fill="both")

    shadow = tk.Frame(card_wrap, bg="#07111d")
    shadow.place(relx=0.5, rely=0.5, anchor="center", width=608, height=570)

    card = tk.Frame(card_wrap, bg=BG_CARD)
    card.place(relx=0.5, rely=0.5, anchor="center", width=602, height=564)

    # force card_wrap to be tall enough for place() to work
    card_wrap.configure(height=620)

    tk.Frame(card, bg=ACCENT2, height=3).pack(fill="x")
    tk.Frame(card, bg=ACCENT,  height=2).pack(fill="x")

    inner = tk.Frame(card, bg=BG_CARD)
    inner.pack(fill="both", expand=True, padx=40, pady=26)
    inner.columnconfigure(0, weight=1)

    level_var   = tk.StringVar()
    class_var   = tk.StringVar()
    subject_var = tk.StringVar()
    year_var    = tk.StringVar()

    # ── Field helpers ─────────────────────────────────────────
    def field_lbl(text, row):
        tk.Label(inner, text=text,
                 font=(FONT, 10, "bold"), fg=MUTED, bg=BG_CARD, anchor="w"
                 ).grid(row=row, column=0, sticky="w", pady=(14, 3))

    def combo(var, row, readonly=True):
        cb = ttk.Combobox(inner, textvariable=var,
                          state="readonly" if readonly else "normal",
                          style="PP.TCombobox", font=(FONT, 11))
        cb.grid(row=row, column=0, sticky="ew", ipady=6)
        return cb

    field_lbl("🎓  Education Level", 0);  level_cb   = combo(level_var,   1)
    field_lbl("📋  Class / Degree",  2);  class_cb   = combo(class_var,   3)
    field_lbl("📖  Subject",         4);  subject_cb = combo(subject_var, 5, readonly=False)
    field_lbl("📅  Year",            6);  year_cb    = combo(year_var,    7)

    tk.Frame(inner, bg=BORDER, height=1).grid(row=8, column=0, sticky="ew", pady=(20, 0))

    status_var = tk.StringVar(value="👆  Start by selecting your Education Level above.")
    status_lbl = tk.Label(inner, textvariable=status_var,
                          font=(FONT, 10), fg=MUTED,
                          bg=BG_CARD, wraplength=500, justify="left")
    status_lbl.grid(row=9, column=0, sticky="w", pady=(10, 0))

    # ── Open paper ────────────────────────────────────────────
    def open_link():
        level   = level_var.get().strip()
        cls     = class_var.get().strip()
        subject = subject_var.get().strip()
        year    = year_var.get().strip()

        # Validate all fields filled
        missing = []
        if not level:   missing.append("Education Level")
        if not cls:     missing.append("Class / Degree")
        if not subject: missing.append("Subject")
        if not year:    missing.append("Year")

        if missing:
            status_var.set(f"⚠️  Please select: {', '.join(missing)}")
            status_lbl.config(fg=ERROR)
            return

        mask = (
            (df["Level"]   == level)   &
            (df["Subject"] == subject) &
            (df["Year"]    == year)
        )
        if _has_class_deg and cls:
            mask &= df["Class/Degree"].astype(str) == cls

        result = df[mask]

        if result.empty:
            status_var.set(
                f"❌  No match found.\n"
                f"    Level: {level}  |  Class: {cls}  |  Subject: {subject}  |  Year: {year}\n"
                f"    Try selecting from the dropdowns instead of typing."
            )
            status_lbl.config(fg=ERROR)
            return

        link = str(result.iloc[0][_link_column])
        webbrowser.open(link)
        status_var.set(
            f"✅  Google search opened in your browser!\n"
            f"    {subject}  ·  Class {cls}  ·  {level}  ·  {year}\n"
            f"    Click any result to download the paper PDF."
        )
        status_lbl.config(fg=SUCCESS)

    # ── Button ────────────────────────────────────────────────
    btn_frame = tk.Frame(inner, bg=BG_CARD)
    btn_frame.grid(row=10, column=0, pady=(22, 6))
    _pill(btn_frame, "🔍  Search & Open Past Paper", open_link,
          w=300, h=52, bg=ACCENT, fg="#0d1b2a", fs=13).pack()

    # ── Hint label ────────────────────────────────────────────
    tk.Label(inner,
             text="💡  Links open Google Search — click any result to get the actual paper PDF",
             font=(FONT, 9), fg="#2a4a63", bg=BG_CARD, anchor="w"
             ).grid(row=11, column=0, sticky="w", pady=(4, 0))

    # ── Cascade logic ─────────────────────────────────────────
    def sort_classes(classes):
        def key(x):
            try:    return (0, int(x))
            except: return (1, x)
        return sorted(classes, key=key)

    # Populate level dropdown
    level_cb["values"] = sorted(df["Level"].unique().tolist())

    def update_classes(event=None):
        class_var.set(""); subject_var.set(""); year_var.set("")
        class_cb["values"] = []; subject_cb["values"] = []; year_cb["values"] = []
        status_var.set("👆  Now select your Class / Degree.")
        status_lbl.config(fg=MUTED)
        level = level_var.get()
        if level and _has_class_deg:
            classes = df[df["Level"] == level]["Class/Degree"].dropna().astype(str).unique()
            class_cb["values"] = sort_classes(classes)

    def update_subjects(event=None):
        subject_var.set(""); year_var.set("")
        subject_cb["values"] = []; year_cb["values"] = []
        status_var.set("👆  Now select your Subject.")
        status_lbl.config(fg=MUTED)
        level = level_var.get()
        cls   = class_var.get()
        if level:
            mask = df["Level"] == level
            if _has_class_deg and cls:
                mask &= df["Class/Degree"].astype(str) == cls
            subs = sorted(df[mask]["Subject"].dropna().unique().tolist())
            subject_cb["values"] = subs

    def filter_subjects(event):
        typed = subject_var.get().lower()
        level = level_var.get()
        cls   = class_var.get()
        if level:
            mask = df["Level"] == level
            if _has_class_deg and cls:
                mask &= df["Class/Degree"].astype(str) == cls
            subs = df[mask]["Subject"].dropna().unique()
            subject_cb["values"] = sorted(s for s in subs if typed in s.lower())

    def update_years(event=None):
        year_var.set("")
        year_cb["values"] = []
        status_var.set("👆  Now select the Year.")
        status_lbl.config(fg=MUTED)
        level   = level_var.get()
        cls     = class_var.get()
        subject = subject_var.get()
        if level and subject:
            mask = (df["Level"] == level) & (df["Subject"] == subject)
            if _has_class_deg and cls:
                mask &= df["Class/Degree"].astype(str) == cls
            years = sorted(df[mask]["Year"].dropna().unique().tolist(), reverse=True)
            year_cb["values"] = years

    level_cb.bind("<<ComboboxSelected>>",   update_classes)
    class_cb.bind("<<ComboboxSelected>>",   update_subjects)
    subject_cb.bind("<KeyRelease>",         filter_subjects)
    subject_cb.bind("<<ComboboxSelected>>", update_years)

    # ── Footer ────────────────────────────────────────────────
    footer = tk.Frame(win, bg="#07111d", height=32)
    footer.pack(fill="x", side="bottom")
    footer.pack_propagate(False)
    tk.Label(footer,
             text="Smart Learning  •  Past Papers Finder  •  Opens Google Search — no more Forbidden errors",
             font=(FONT, 9), fg="#2a4a63", bg="#07111d").pack(expand=True)