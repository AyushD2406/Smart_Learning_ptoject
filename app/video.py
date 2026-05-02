import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser
import re
import threading
import yt_dlp

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


BG_DARK  = "#0d1b2a"
BG_PANEL = "#0f2233"
BG_CARD  = "#162535"
BG_INPUT = "#1e3448"
ACCENT   = "#0984e3"
ACCENT2  = "#6c5ce7"
TEXT     = "#e8f4f8"
MUTED    = "#5a7a94"
FONT     = "Segoe UI"


def open_videos_window(parent):

    win = tk.Toplevel(parent)
    win.title("Search Videos")
    win.state("zoomed")
    win.resizable(True, True)
    win.configure(bg=BG_DARK)

    win.transient(parent)
    win.grab_set()
    win.attributes("-topmost", True)

    def bring_to_front():
        if win.state() == "iconic":
            win.deiconify()
        win.lift()
        win.focus_set()

    win.after(100, bring_to_front)

    def close_window():
        win.grab_release()
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", close_window)

    saved_links = []

    tk.Frame(win, bg=ACCENT, height=5).pack(fill="x")
    tk.Frame(win, bg=ACCENT2, height=2).pack(fill="x")

    header = tk.Frame(win, bg=BG_PANEL)
    header.pack(fill="x")

    tk.Label(
        header,
        text="🎬  Search Topic Videos",
        font=(FONT, 20, "bold"),
        bg=BG_PANEL,
        fg=TEXT
    ).pack(pady=(18, 4))

    tk.Label(
        header,
        text="Type a topic or upload your notes / PDF to find relevant videos",
        font=(FONT, 11),
        bg=BG_PANEL,
        fg=MUTED
    ).pack(pady=(0, 16))

    card = tk.Frame(win, bg=BG_CARD)
    card.pack(fill="x", padx=60, pady=(18, 0))

    inner = tk.Frame(card, bg=BG_CARD)
    inner.pack(fill="x", padx=28, pady=20)

    tk.Label(
        inner,
        text="🔍  Enter Topic",
        font=(FONT, 10, "bold"),
        fg=MUTED,
        bg=BG_CARD,
        anchor="w"
    ).pack(fill="x", pady=(0, 4))

    search_row = tk.Frame(inner, bg=BG_CARD)
    search_row.pack(fill="x")

    query_var = tk.StringVar()

    entry = tk.Entry(
        search_row,
        textvariable=query_var,
        font=(FONT, 12),
        bg=BG_INPUT,
        fg=TEXT,
        insertbackground=ACCENT,
        relief="flat",
        bd=0
    )

    entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 12))

    search_btn = tk.Button(
        search_row,
        text="Search",
        font=(FONT, 11, "bold"),
        bg=ACCENT,
        fg="#ffffff",
        activebackground="#2d74c4",
        activeforeground="#ffffff",
        bd=0,
        relief="flat",
        cursor="hand2",
        command=lambda: search_videos()
    )

    search_btn.pack(side="left", ipadx=22, ipady=10)

    tk.Frame(inner, bg="#1e3448", height=1).pack(fill="x", pady=(4, 12))

    upload_btn = tk.Button(
        inner,
        text="📎   Upload Notes / PDF",
        font=(FONT, 11, "bold"),
        bg=BG_INPUT,
        fg="#74b9ff",
        activebackground="#253d55",
        activeforeground="#a29bfe",
        bd=0,
        relief="flat",
        cursor="hand2",
        anchor="w",
        command=lambda: upload_notes()
    )

    upload_btn.pack(fill="x", ipady=10)

    results_header = tk.Frame(win, bg=BG_DARK)
    results_header.pack(fill="x", padx=60, pady=(18, 0))

    results_title = tk.Label(
        results_header,
        text="",
        font=(FONT, 12, "bold"),
        bg=BG_DARK,
        fg=TEXT,
        anchor="w"
    )

    results_title.pack(fill="x")

    results_outer = tk.Frame(win, bg=BG_DARK)
    results_outer.pack(fill="both", expand=True, padx=60, pady=(8, 0))

    results_canvas = tk.Canvas(
        results_outer,
        bg=BG_DARK,
        highlightthickness=0
    )

    scrollbar = ttk.Scrollbar(
        results_outer,
        orient="vertical",
        command=results_canvas.yview
    )

    results_canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    results_canvas.pack(side="left", fill="both", expand=True)

    results_frame = tk.Frame(results_canvas, bg=BG_DARK)

    results_canvas.create_window(
        (0, 0),
        window=results_frame,
        anchor="nw"
    )

    results_frame.bind(
        "<Configure>",
        lambda e: results_canvas.configure(
            scrollregion=results_canvas.bbox("all")
        )
    )

    def save_links():

        if not saved_links:
            messagebox.showwarning(
                "No Links",
                "No links to save yet.",
                parent=win
            )
            bring_to_front()
            return

        file_path = filedialog.asksaveasfilename(
            parent=win,
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save Video Links"
        )

        bring_to_front()

        if not file_path:
            return

        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("Saved Learning Videos", styles["Title"]))
        story.append(Spacer(1, 20))

        for title, link in saved_links:
            clickable = f'<link href="{link}">{title}</link>'
            story.append(Paragraph(clickable, styles["Normal"]))
            story.append(Spacer(1, 10))

        pdf = SimpleDocTemplate(file_path)
        pdf.build(story)

        messagebox.showinfo(
            "Saved",
            "Clickable PDF saved successfully.",
            parent=win
        )
        bring_to_front()

    def get_video(query):

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:

                result = ydl.extract_info(f"ytsearch1:{query}", download=False)

                if not result:
                    return None, None

                entries = result.get("entries") or []

                if not entries:
                    return None, None

                video = entries[0]

                if not video:
                    return None, None

                title = video.get("title", "Untitled Video")
                url = video.get("webpage_url") or video.get("url")

                if not url:
                    return None, None

                return title, url

        except Exception:
            return None, None

    def show_results(query):

        bring_to_front()

        for widget in results_frame.winfo_children():
            widget.destroy()

        saved_links.clear()

        if not query:
            messagebox.showerror(
                "Error",
                "Please enter a topic or upload notes.",
                parent=win
            )
            bring_to_front()
            return

        results_title.config(text=f'Results for: "{query}"')
        win.update_idletasks()

        lesson_labels = [
            "Full Lecture",
            "Beginner Guide",
            "Quick Revision",
            "Solved Examples",
            "Concept Explanation",
        ]

        search_btn.config(state="disabled", text="Searching...")
        upload_btn.config(state="disabled")

        tk.Label(
            results_frame,
            text="Searching videos, please wait...",
            font=(FONT, 12),
            bg=BG_DARK,
            fg=MUTED
        ).pack(pady=20)

        bring_to_front()

        def search_worker():

            found_videos = []

            for i, label in enumerate(lesson_labels):

                search_term = f"{query} {label}"
                title, link = get_video(search_term)

                if link:
                    found_videos.append((i + 1, title, link))

            win.after(0, lambda: display_results(found_videos))

        def display_results(found_videos):

            for widget in results_frame.winfo_children():
                widget.destroy()

            saved_links.clear()

            search_btn.config(state="normal", text="Search")
            upload_btn.config(state="normal")

            if not found_videos:
                tk.Label(
                    results_frame,
                    text="No videos found. Try another topic.",
                    font=(FONT, 12),
                    bg=BG_DARK,
                    fg=MUTED
                ).pack(pady=20)

                bring_to_front()
                return

            for number, title, link in found_videos:

                saved_links.append((title, link))

                row = tk.Frame(results_frame, bg=BG_CARD)
                row.pack(fill="x", pady=5, ipady=2)

                tk.Label(
                    row,
                    text=f"  {number}  ",
                    font=(FONT, 11, "bold"),
                    bg=ACCENT,
                    fg="#ffffff"
                ).pack(
                    side="left",
                    ipadx=4,
                    ipady=10
                )

                link_lbl = tk.Label(
                    row,
                    text=f"▶   {title}",
                    font=(FONT, 11),
                    bg=BG_CARD,
                    fg="#74b9ff",
                    cursor="hand2",
                    anchor="w"
                )

                link_lbl.pack(
                    side="left",
                    fill="x",
                    expand=True,
                    padx=14,
                    ipady=10
                )

                link_lbl.bind(
                    "<Button-1>",
                    lambda e, url=link: webbrowser.open(url)
                )

                tk.Label(
                    row,
                    text="YouTube →",
                    font=(FONT, 9),
                    bg=BG_CARD,
                    fg=MUTED
                ).pack(
                    side="right",
                    padx=14
                )

            save_btn = tk.Button(
                results_frame,
                text="💾 Save All Links",
                font=(FONT, 11, "bold"),
                bg=ACCENT2,
                fg="white",
                relief="flat",
                cursor="hand2",
                command=save_links
            )

            save_btn.pack(pady=15, ipadx=15, ipady=8)

            bring_to_front()

        threading.Thread(target=search_worker, daemon=True).start()

    def search_videos(event=None):

        query = query_var.get().strip()
        show_results(query)

    def upload_notes():

        file_path = filedialog.askopenfilename(
            parent=win,
            title="Upload Notes or PDF",
            filetypes=[
                ("All Supported Files", "*.txt *.pdf *.docx *.doc *.rtf *.md *.csv"),
                ("Text files", "*.txt"),
                ("PDF files", "*.pdf"),
                ("Word Documents", "*.docx *.doc"),
                ("Rich Text", "*.rtf"),
                ("Markdown", "*.md"),
                ("CSV files", "*.csv"),
                ("All files", "*.*"),
            ]
        )

        bring_to_front()

        if not file_path:
            return

        try:

            content = ""

            if file_path.lower().endswith(".pdf"):

                try:
                    import pdfplumber

                    with pdfplumber.open(file_path) as pdf:
                        for page in pdf.pages:
                            text = page.extract_text()
                            if text:
                                content += text + "\n"

                except ImportError:
                    try:
                        import PyPDF2

                        with open(file_path, "rb") as f:
                            reader = PyPDF2.PdfReader(f)
                            for page in reader.pages:
                                extracted = page.extract_text()
                                if extracted:
                                    content += extracted + "\n"

                    except ImportError:
                        messagebox.showerror(
                            "Missing Library",
                            "Install pdfplumber for PDF support:\n  pip install pdfplumber",
                            parent=win
                        )
                        bring_to_front()
                        return

            elif file_path.lower().endswith((".txt", ".md", ".csv")):

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

            elif file_path.lower().endswith(".docx"):

                try:
                    import docx

                    doc = docx.Document(file_path)
                    content = "\n".join([para.text for para in doc.paragraphs])

                except ImportError:
                    messagebox.showerror(
                        "Missing Library",
                        "Install python-docx:\n  pip install python-docx",
                        parent=win
                    )
                    bring_to_front()
                    return

            elif file_path.lower().endswith(".rtf"):

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    raw = f.read()

                content = re.sub(r"\\[a-z]+\d*\s?|\{|\}", " ", raw)

            else:

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

            if not content.strip():
                messagebox.showerror(
                    "Error",
                    "No text could be extracted from this file.",
                    parent=win
                )
                bring_to_front()
                return

            stop_words = {
                "about", "above", "after", "again", "also", "another", "because",
                "before", "being", "between", "could", "during", "each", "every",
                "found", "from", "have", "having", "here", "however", "into",
                "itself", "just", "like", "more", "most", "much", "must", "never",
                "often", "only", "other", "over", "same", "should", "since",
                "some", "such", "than", "that", "their", "them", "then", "there",
                "these", "they", "this", "those", "through", "under", "until",
                "upon", "very", "was", "were", "what", "when", "where", "which",
                "while", "will", "with", "within", "without", "would", "your"
            }

            all_words = re.findall(r"\b[a-zA-Z]{5,}\b", content)
            seen = set()
            keywords = []

            for w in all_words:

                lower = w.lower()

                if lower not in stop_words and lower not in seen:
                    seen.add(lower)
                    keywords.append(lower)

                if len(keywords) >= 5:
                    break

            if not keywords:
                messagebox.showerror(
                    "Error",
                    "No meaningful keywords found in the file.",
                    parent=win
                )
                bring_to_front()
                return

            query = " ".join(keywords)
            query_var.set(query)
            show_results(query)

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Could not read file: {e}",
                parent=win
            )
            bring_to_front()

    entry.bind("<Return>", search_videos)

    tk.Label(
        win,
        text="Smart Learning  •  Video Search",
        font=(FONT, 9),
        bg=BG_DARK,
        fg="#2a4a63"
    ).pack(side="bottom", pady=8)

    entry.focus_set()
    bring_to_front()
