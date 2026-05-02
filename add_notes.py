import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import pandas as pd
import os

DATASET_PATH = "Complete_Study_Materials_FINAL.xlsx"
SAVE_FILE = "saved_links.txt"

BG_DARK  = "#0a0f1e"
BG_PANEL = "#0d1e36"
BG_CARD  = "#112236"
BG_INPUT = "#22384d"

ACCENT   = "#ff9f43"
ACCENT2  = "#0984e3"

TEXT  = "#dfe6e9"
MUTED = "#5a7a94"

FONT = "Segoe UI"

_dataset = None


# ================= LOAD DATASET =================

def load_dataset():
    global _dataset

    if _dataset is not None:
        return _dataset

    if not os.path.exists(DATASET_PATH):
        messagebox.showerror(
            "File Not Found",
            "Complete_Study_Materials_FINAL.xlsx not found"
        )
        return None

    try:
        df = pd.read_excel(DATASET_PATH)

        df.columns = [c.strip() for c in df.columns]

        for col in [
            "Level","Class/Degree","Stream",
            "Subject","Topic","Book_Name","Direct_PDF_Link"
        ]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        _dataset = df
        return df

    except Exception as e:
        messagebox.showerror("Error", str(e))
        return None


# ================= SAVE LINK =================

def save_link(link):

    try:
        with open(SAVE_FILE,"a",encoding="utf-8") as f:
            f.write(link+"\n")

        messagebox.showinfo("Saved","Link saved successfully!")

    except Exception as e:
        messagebox.showerror("Error",str(e))


# ================= OPEN PDF =================

def open_pdf(link):

    try:
        os.startfile(link)

    except:
        webbrowser.open(link)


# ================= MAIN WINDOW =================

def open_add_notes_window(parent):

    win = tk.Toplevel(parent)
    win.title("Textbook & Resource Finder")
    win.state("zoomed")
    win.configure(bg=BG_DARK)

    dataset = load_dataset()
    if dataset is None:
        return


    # ================= STYLE =================

    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Custom.TCombobox",
        fieldbackground=BG_INPUT,
        background=BG_INPUT,
        foreground=TEXT,
        bordercolor="#2d4b63",
        lightcolor="#2d4b63",
        darkcolor="#2d4b63",
        arrowcolor=ACCENT,
        padding=6,
        relief="flat"
    )

    style.map(
        "Custom.TCombobox",
        fieldbackground=[("readonly", BG_INPUT)],
        foreground=[("readonly", TEXT)]
    )


    # ================= CARD =================

    card = tk.Frame(win, bg=BG_CARD)
    card.place(relx=0.5, rely=0.5, anchor="center", width=520, height=520)

    inner = tk.Frame(card, bg=BG_CARD)
    inner.pack(fill="both", expand=True, padx=35, pady=30)


    # ================= LEVEL =================

    tk.Label(
        inner,
        text="🎓  Education Level",
        bg=BG_CARD,
        fg=MUTED,
        font=(FONT,10,"bold")
    ).pack(anchor="w")

    levels = sorted(dataset["Level"].dropna().unique())

    level_var = tk.StringVar(value=levels[0])

    level_cb = ttk.Combobox(
        inner,
        textvariable=level_var,
        values=levels,
        state="readonly",
        style="Custom.TCombobox"
    )

    level_cb.pack(fill="x", pady=5)


    # ================= CLASS =================

    tk.Label(
        inner,
        text="📋  Class / Degree",
        bg=BG_CARD,
        fg=MUTED,
        font=(FONT,10,"bold")
    ).pack(anchor="w", pady=(15,0))

    class_var = tk.StringVar()

    class_cb = ttk.Combobox(
        inner,
        textvariable=class_var,
        state="readonly",
        style="Custom.TCombobox"
    )

    class_cb.pack(fill="x", pady=5)


    def update_classes(event=None):

        lvl = level_var.get()

        classes = sorted(
            dataset[dataset["Level"] == lvl]["Class/Degree"]
            .dropna()
            .unique()
        )

        class_cb["values"] = classes

        if classes:
            class_var.set(classes[0])


    level_cb.bind("<<ComboboxSelected>>", update_classes)

    update_classes()


    # ================= SUBJECT =================

    tk.Label(
        inner,
        text="📚  Subject",
        bg=BG_CARD,
        fg=MUTED,
        font=(FONT,10,"bold")
    ).pack(anchor="w", pady=(15,0))


    subject_entry = tk.Entry(
        inner,
        bg=BG_INPUT,
        fg=TEXT,
        relief="flat",
        font=(FONT,11),
        insertbackground=ACCENT
    )

    subject_entry.pack(fill="x", ipady=8, pady=5)


    # ================= TOPIC =================

    tk.Label(
        inner,
        text="🔎  Topic",
        bg=BG_CARD,
        fg=MUTED,
        font=(FONT,10,"bold")
    ).pack(anchor="w", pady=(15,0))


    topic_entry = tk.Entry(
        inner,
        bg=BG_INPUT,
        fg=TEXT,
        relief="flat",
        font=(FONT,11),
        insertbackground=ACCENT
    )

    topic_entry.pack(fill="x", ipady=8, pady=5)


    # ================= SEARCH =================

    def search_resources():

        subject = subject_entry.get().strip()
        topic   = topic_entry.get().strip()

        level = level_var.get()
        class_deg = class_var.get()

        df = dataset.copy()

        if level:
            df = df[df["Level"].str.lower() == level.lower()]

        if class_deg:
            df = df[df["Class/Degree"].str.lower() == class_deg.lower()]

        if subject:
            df = df[
                df["Subject"].str.contains(subject,case=False,na=False)
            ]

        if topic:
            df = df[
                df["Topic"].str.contains(topic,case=False,na=False)
            ]

        if df.empty:

            messagebox.showinfo(
                "No Results",
                "No study resources found."
            )

        else:

            show_links(df.head(50),win)


    # ================= DIVIDER =================

    tk.Frame(inner,bg="#2d4b63",height=1).pack(fill="x",pady=20)

    tk.Label(
        inner,
        text="☝️  Start by selecting your Education Level above.",
        font=(FONT,9),
        fg=MUTED,
        bg=BG_CARD
    ).pack()


    # ================= SEARCH BUTTON =================

    search_btn = tk.Button(
        inner,
        text="🔎  Search & Open Resources",
        font=(FONT,12,"bold"),
        bg=ACCENT,
        fg="black",
        relief="flat",
        cursor="hand2",
        activebackground="#ff8c2a",
        command=search_resources
    )

    search_btn.pack(pady=25, ipadx=40, ipady=12)

    search_btn.bind(
        "<Enter>",
        lambda e: search_btn.config(bg="#ff8c2a")
    )

    search_btn.bind(
        "<Leave>",
        lambda e: search_btn.config(bg=ACCENT)
    )


# ================= SHOW RESULTS =================

def show_links(matches,parent):

    win = tk.Toplevel(parent)
    win.title("Resources Found")
    win.geometry("820x550")
    win.configure(bg=BG_DARK)

    container = tk.Frame(win,bg=BG_DARK)
    container.pack(fill="both",expand=True,padx=20,pady=20)

    canvas = tk.Canvas(container,bg=BG_DARK,highlightthickness=0)

    scrollbar = ttk.Scrollbar(
        container,
        orient="vertical",
        command=canvas.yview
    )

    frame = tk.Frame(canvas,bg=BG_DARK)

    frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0,0),window=frame,anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left",fill="both",expand=True)

    scrollbar.pack(side="right",fill="y")


    for _,row in matches.iterrows():

        link = str(row["Direct_PDF_Link"])

        item = tk.Frame(frame,bg=BG_CARD)
        item.pack(fill="x",pady=6)

        title = f"{row['Subject']}  •  {row.get('Topic','')}"

        tk.Label(
            item,
            text=title,
            font=(FONT,11,"bold"),
            bg=BG_CARD,
            fg="#74b9ff"
        ).pack(anchor="w",padx=10,pady=(8,2))

        tk.Label(
            item,
            text=row["Book_Name"],
            font=(FONT,9),
            bg=BG_CARD,
            fg=MUTED
        ).pack(anchor="w",padx=10)


        btn_frame = tk.Frame(item,bg=BG_CARD)
        btn_frame.pack(anchor="w",padx=10,pady=8)


        open_btn = tk.Button(
            btn_frame,
            text="📖 Open PDF",
            bg="#55efc4",
            relief="flat",
            command=lambda l=link: open_pdf(l)
        )

        open_btn.pack(side="left",padx=5)


        save_btn = tk.Button(
            btn_frame,
            text="💾 Save Link",
            bg="#74b9ff",
            relief="flat",
            command=lambda l=link: save_link(l)
        )

        save_btn.pack(side="left",padx=5)