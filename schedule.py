import tkinter as tk
from tkinter import messagebox, ttk
import json
from datetime import datetime, timedelta
import random
import os

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

BG_DARK = "#0a0f1e"
BG_PANEL = "#0d1e36"
BG_CARD = "#112236"
BG_INPUT = "#1a3045"
ACCENT = "#0984e3"
ACCENT2 = "#fd9644"
ACCENT3 = "#6c5ce7"
TEXT = "#dfe6e9"
MUTED = "#5a7a94"
FONT = "Segoe UI"

SCHEDULE_FILE = "schedule.json"
TIMER_STATE_FILE = "timer_state.json"


class StudyTimer:
    def __init__(self):
        self._after_id = None
        self.remaining = 0
        self.running = False
        self.paused = False
        self.display_var = None
        self.session_var = None
        self._root = None
        self._on_complete = None
        self._on_freeze = None
        self._on_unfreeze = None
        self.active_session_label = None

    def _tick(self):
        if not self.running:
            return

        if self.remaining <= 0:
            self.running = False
            self.paused = False
            self.active_session_label = None
            clear_saved_timer_state()

            if self.display_var:
                self.display_var.set("00:00")
            if self.session_var:
                self.session_var.set("No active session")
            if self._on_unfreeze:
                self._on_unfreeze()
            if self._on_complete:
                self._on_complete()
            return

        self.remaining -= 1
        self._update_display()
        self._after_id = self._root.after(1000, self._tick)

    def _update_display(self):
        if self.display_var:
            mins, secs = divmod(self.remaining, 60)
            self.display_var.set(f"{mins:02d}:{secs:02d}")

    def start(
        self,
        root,
        duration_seconds,
        display_var,
        session_var,
        on_complete=None,
        on_freeze=None,
        on_unfreeze=None,
        session_label=None,
    ):
        self.stop()
        self._root = root
        self.display_var = display_var
        self.session_var = session_var
        self._on_complete = on_complete
        self._on_freeze = on_freeze
        self._on_unfreeze = on_unfreeze
        self.remaining = duration_seconds
        self.running = True
        self.paused = False
        self.active_session_label = session_label
        self._update_display()

        if self._on_freeze:
            self._on_freeze()

        self._after_id = root.after(1000, self._tick)

    def pause(self):
        if self.running:
            self.running = False
            self.paused = True

            if self._after_id:
                self._root.after_cancel(self._after_id)
                self._after_id = None

            if self._on_unfreeze:
                self._on_unfreeze()

            save_timer_state(self.remaining, self.active_session_label)

    def resume(self):
        if not self.running and self.paused and self.remaining > 0 and self._root:
            self.running = True
            self.paused = False

            if self._on_freeze:
                self._on_freeze()

            self._after_id = self._root.after(1000, self._tick)

    def reset(self):
        self.stop()
        self.remaining = 0
        self.paused = False
        self.active_session_label = None
        clear_saved_timer_state()

        if self.display_var:
            self.display_var.set("00:00")
        if self.session_var:
            self.session_var.set("No active session")
        if self._on_unfreeze:
            self._on_unfreeze()

    def stop(self):
        self.running = False
        if self._after_id and self._root:
            try:
                self._root.after_cancel(self._after_id)
            except Exception:
                pass
        self._after_id = None

    def is_active(self):
        return self.running


timer = StudyTimer()


def save_timer_state(remaining_seconds, session_label):
    try:
        with open(TIMER_STATE_FILE, "w") as f:
            json.dump(
                {
                    "remaining": remaining_seconds,
                    "session_label": session_label or "",
                },
                f,
            )
    except Exception:
        pass


def load_saved_timer_state():
    try:
        with open(TIMER_STATE_FILE, "r") as f:
            data = json.load(f)

        remaining = int(data.get("remaining", 0))
        label = data.get("session_label", "")

        if remaining > 0:
            return remaining, label
    except Exception:
        pass

    return None


def clear_saved_timer_state():
    try:
        os.remove(TIMER_STATE_FILE)
    except Exception:
        pass


def styled_button(parent, text, bg, command, fg="#ffffff"):
    hover_map = {
        ACCENT: "#2d74c4",
        ACCENT2: "#e07830",
        ACCENT3: "#5a4bd1",
        BG_INPUT: "#253d55",
    }
    hover = hover_map.get(bg, "#2d74c4")

    btn = tk.Button(
        parent,
        text=text,
        font=(FONT, 11, "bold"),
        bg=bg,
        fg=fg,
        activebackground=hover,
        activeforeground=fg,
        bd=0,
        relief="flat",
        cursor="hand2",
        command=command,
    )
    btn.bind("<Enter>", lambda e: btn.configure(bg=hover))
    btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
    return btn


def field_label(parent, text):
    tk.Label(
        parent,
        text=text,
        font=(FONT, 10, "bold"),
        fg=MUTED,
        bg=BG_DARK,
        anchor="w",
    ).pack(fill="x", pady=(14, 3))


def input_box(parent):
    entry = tk.Entry(
        parent,
        font=(FONT, 11),
        bg=BG_INPUT,
        fg=TEXT,
        insertbackground=ACCENT,
        relief="flat",
        bd=0,
    )
    entry.pack(fill="x", ipady=9)
    tk.Frame(parent, bg="#1e3448", height=1).pack(fill="x")
    return entry
def build_timer_panel(parent_frame):
    panel = tk.Frame(parent_frame, bg=BG_CARD, highlightthickness=1, highlightbackground="#1e3448")
    panel.pack(fill="x", padx=24, pady=(0, 10))

    left = tk.Frame(panel, bg=BG_CARD)
    left.pack(side="left", padx=(14, 6), pady=8)

    tk.Label(left, text="Study Timer", font=(FONT, 10, "bold"), bg=BG_CARD, fg=MUTED).pack(anchor="w")

    time_var = tk.StringVar(value="00:00")
    tk.Label(left, textvariable=time_var, font=(FONT, 22, "bold"), bg=BG_CARD, fg=ACCENT2).pack(anchor="w")

    session_var = tk.StringVar(value="No active session")
    tk.Label(left, textvariable=session_var, font=(FONT, 9), bg=BG_CARD, fg=MUTED).pack(anchor="w")

    right = tk.Frame(panel, bg=BG_CARD)
    right.pack(side="right", padx=14, pady=8)

    btn_cfg = {
        "font": (FONT, 9, "bold"),
        "bd": 0,
        "relief": "flat",
        "cursor": "hand2",
        "fg": "#ffffff",
    }

    pause_btn = tk.Button(right, text="Pause", bg=BG_INPUT, activebackground="#253d55", command=timer.pause, **btn_cfg)
    pause_btn.pack(side="left", ipadx=10, ipady=6, padx=(0, 4))

    resume_btn = tk.Button(right, text="Resume", bg=ACCENT, activebackground="#2d74c4", command=timer.resume, **btn_cfg)
    resume_btn.pack(side="left", ipadx=10, ipady=6, padx=(0, 4))

    reset_btn = tk.Button(right, text="Reset", bg=ACCENT3, activebackground="#5a4bd1", command=timer.reset, **btn_cfg)
    reset_btn.pack(side="left", ipadx=10, ipady=6)

    return time_var, session_var


def create_time_slots(start_time, end_time):
    time_slots = []
    slot_types = []
    current = start_time
    study_count = 0

    while current < end_time:
        slot_end = current + timedelta(minutes=60)
        if slot_end > end_time:
            break

        time_slots.append(f"{current.strftime('%H:%M')} - {slot_end.strftime('%H:%M')}")
        slot_types.append("Study")
        current = slot_end
        study_count += 1

        if study_count == 2:
            break_end = current + timedelta(minutes=15)
            if break_end < end_time:
                time_slots.append(f"{current.strftime('%H:%M')} - {break_end.strftime('%H:%M')}")
                slot_types.append("Short Break")
                current = break_end

        elif study_count == 4:
            break_end = current + timedelta(minutes=30)
            if break_end < end_time:
                time_slots.append(f"{current.strftime('%H:%M')} - {break_end.strftime('%H:%M')}")
                slot_types.append("Long Break")
                current = break_end

    return time_slots, slot_types


def parse_subject_list(text):
    parts = text.replace(";", ",").split(",")
    return [part.strip() for part in parts if part.strip()]


def format_subject_list(subjects):
    return ", ".join(subjects) if subjects else "Not selected"


def build_weekly_schedule(subjects, weak_subjects, time_slots, slot_types):
    if isinstance(weak_subjects, str):
        weak_subjects = [weak_subjects] if weak_subjects else []

    study_indices = [i for i, slot_type in enumerate(slot_types) if slot_type == "Study"]

    consecutive_pairs = []
    for k in range(len(study_indices) - 1):
        a = study_indices[k]
        b = study_indices[k + 1]
        if b == a + 1:
            consecutive_pairs.append((a, b))

    weak_pair_sequence = []
    if weak_subjects and consecutive_pairs:
        shuffled_pairs = consecutive_pairs.copy()
        random.shuffle(shuffled_pairs)

        while len(shuffled_pairs) < len(DAYS):
            extra = consecutive_pairs.copy()
            random.shuffle(extra)
            shuffled_pairs += extra

        weak_pair_sequence = shuffled_pairs[:len(DAYS)]

    weekly_schedule = {}

    for day in DAYS:
        day_slots = []

        for slot_type in slot_types:
            if slot_type == "Short Break":
                day_slots.append("Short Break")
            elif slot_type == "Long Break":
                day_slots.append("Long Break")
            else:
                day_slots.append("")

        weekly_schedule[day] = day_slots

    if weak_subjects and weak_pair_sequence:
        weak_subject_pool = []
        base_count = len(DAYS) // len(weak_subjects)
        extra_count = len(DAYS) % len(weak_subjects)

        shuffled_weak_subjects = weak_subjects.copy()
        random.shuffle(shuffled_weak_subjects)

        for subject in shuffled_weak_subjects:
            weak_subject_pool.extend([subject] * base_count)

        for i in range(extra_count):
            weak_subject_pool.append(shuffled_weak_subjects[i])

        random.shuffle(weak_subject_pool)

        for day_index, day in enumerate(DAYS):
            slot_a, slot_b = weak_pair_sequence[day_index]
            label = f"{weak_subject_pool[day_index]} (Extra Focus)"
            weekly_schedule[day][slot_a] = label
            weekly_schedule[day][slot_b] = label

    revision_positions = []

    for day in DAYS:
        study_slot_counter = 0

        for i, slot_type in enumerate(slot_types):
            if slot_type != "Study":
                continue

            if study_slot_counter > 0 and study_slot_counter % 3 == 0:
                if weekly_schedule[day][i] == "":
                    revision_positions.append((day, i))

            study_slot_counter += 1

    revision_subject_pool = []

    if subjects and revision_positions:
        total_revision_slots = len(revision_positions)
        base_count = total_revision_slots // len(subjects)
        extra_count = total_revision_slots % len(subjects)

        shuffled_subjects = subjects.copy()
        random.shuffle(shuffled_subjects)

        for subject in shuffled_subjects:
            revision_subject_pool.extend([subject] * base_count)

        for i in range(extra_count):
            revision_subject_pool.append(shuffled_subjects[i])

        random.shuffle(revision_subject_pool)

    for index, (day, slot_index) in enumerate(revision_positions):
        subject = revision_subject_pool[index]
        weekly_schedule[day][slot_index] = f"Revision - {subject}"

        # Add normal lectures in the most balanced way possible.
    # Weak subjects are excluded from normal lectures because they already get Extra Focus.
    normal_positions = []

    for day in DAYS:
        for i, slot_type in enumerate(slot_types):
            if slot_type == "Study" and weekly_schedule[day][i] == "":
                normal_positions.append((day, i))

    normal_subject_pool = []

    # Only non-weak subjects get normal lecture slots.
    normal_subjects = [
        subject for subject in subjects
        if subject not in weak_subjects
    ]

    # Safety fallback: if all subjects are weak, then normal slots use all subjects.
    if not normal_subjects:
        normal_subjects = subjects.copy()

    if normal_subjects and normal_positions:
        total_normal_slots = len(normal_positions)
        base_count = total_normal_slots // len(normal_subjects)
        extra_count = total_normal_slots % len(normal_subjects)

        shuffled_subjects = normal_subjects.copy()
        random.shuffle(shuffled_subjects)

        for subject in shuffled_subjects:
            normal_subject_pool.extend([subject] * base_count)

        for i in range(extra_count):
            normal_subject_pool.append(shuffled_subjects[i])

        random.shuffle(normal_subject_pool)

    for index, (day, slot_index) in enumerate(normal_positions):
        subject = normal_subject_pool[index]
        weekly_schedule[day][slot_index] = subject


    return weekly_schedule
def analyze_schedule_data(data):
    times = data.get("times", [])
    slot_types = data.get("slot_types", [])
    schedule = data.get("schedule", {})
    subjects = data.get("subjects", [])

    weak_subjects = data.get("weak_subjects")
    strong_subjects = data.get("strong_subjects")

    if weak_subjects is None:
        weak_subjects = parse_subject_list(data.get("weak_subject", ""))
    if strong_subjects is None:
        strong_subjects = parse_subject_list(data.get("strong_subject", ""))

    subject_report = {}

    for subject in subjects:
        subject_report[subject] = {
            "normal": 0,
            "revision": 0,
            "extra_focus": 0,
            "total": 0,
        }

    total_study_slots = 0
    total_break_slots = 0
    short_break_slots = 0
    long_break_slots = 0
    normal_slots = 0
    revision_slots = 0
    extra_focus_slots = 0

    for day in DAYS:
        day_schedule = schedule.get(day, [])

        for i, label in enumerate(day_schedule):
            slot_type = slot_types[i] if i < len(slot_types) else ""

            if slot_type == "Short Break":
                total_break_slots += 1
                short_break_slots += 1
                continue

            if slot_type == "Long Break":
                total_break_slots += 1
                long_break_slots += 1
                continue

            if slot_type != "Study":
                continue

            total_study_slots += 1

            if "Extra Focus" in label:
                extra_focus_slots += 1
                subject_name = label.replace("(Extra Focus)", "").strip()
                key = "extra_focus"
            elif label.startswith("Revision -"):
                revision_slots += 1
                subject_name = label.replace("Revision -", "").strip()
                key = "revision"
            else:
                normal_slots += 1
                subject_name = label.strip()
                key = "normal"

            if subject_name not in subject_report:
                subject_report[subject_name] = {
                    "normal": 0,
                    "revision": 0,
                    "extra_focus": 0,
                    "total": 0,
                }

            subject_report[subject_name][key] += 1
            subject_report[subject_name]["total"] += 1

    study_slots_per_day = sum(1 for slot_type in slot_types if slot_type == "Study")

    planned_revision_per_day = 0
    for study_index in range(study_slots_per_day):
        if study_index > 0 and study_index % 3 == 0:
            planned_revision_per_day += 1

    planned_revision_slots = planned_revision_per_day * len(DAYS)
    overwritten_revision_slots = planned_revision_slots - revision_slots

    report = ""
    report += "TIMETABLE ANALYSIS REPORT\n"
    report += "=" * 50 + "\n\n"

    report += "BASIC DETAILS\n"
    report += "-" * 50 + "\n"
    report += f"Total subjects: {len(subjects)}\n"
    report += f"Subjects: {', '.join(subjects)}\n"
    report += f"Weak subjects: {format_subject_list(weak_subjects)}\n"
    report += f"Confident subjects: {format_subject_list(strong_subjects)}\n"
    report += f"Start time: {data.get('start_time', 'Not saved')}\n"
    report += f"End time: {data.get('end_time', 'Not saved')}\n"
    report += f"Study slots per day: {study_slots_per_day}\n"
    report += f"Total days: {len(DAYS)}\n\n"

    report += "SLOT SUMMARY\n"
    report += "-" * 50 + "\n"
    report += f"Total study slots: {total_study_slots}\n"
    report += f"Normal lecture slots: {normal_slots}\n"
    report += f"Visible revision slots: {revision_slots}\n"
    report += f"Extra focus slots: {extra_focus_slots}\n"
    report += f"Total break slots: {total_break_slots}\n"
    report += f"Short break slots: {short_break_slots}\n"
    report += f"Long break slots: {long_break_slots}\n\n"

    report += "REVISION EXPLANATION\n"
    report += "-" * 50 + "\n"
    report += f"Planned revision slots: {planned_revision_slots}\n"
    report += f"Visible revision slots: {revision_slots}\n"
    report += f"Revision slots overwritten by Extra Focus: {overwritten_revision_slots}\n\n"

    report += "SUBJECT-WISE SLOT REPORT\n"
    report += "-" * 50 + "\n"

    for subject, counts in subject_report.items():
        report += f"\n{subject}\n"
        report += f"  Normal lectures: {counts['normal']}\n"
        report += f"  Revision slots: {counts['revision']}\n"
        report += f"  Extra focus slots: {counts['extra_focus']}\n"
        report += f"  Total slots: {counts['total']}\n"

    report += "\nHOW THIS CODE ASSIGNS SLOTS\n"
    report += "-" * 50 + "\n"
    report += "1. It creates 1-hour study slots between your start and end time.\n"
    report += "2. After 2 study slots, it adds a 15-minute short break.\n"
    report += "3. After 4 study slots, it adds a 30-minute long break.\n"
    report += "4. Normal lecture slots are balanced across all subjects.\n"
    report += "5. Every 4th study slot becomes a revision slot when it is not Extra Focus.\n"
    report += "6. Revision slots include all subjects, including weak subjects.\n"
    report += "7. Weak subjects share the shuffled Extra Focus slots fairly.\n"
    report += "8. Extra Focus does not get overwritten by revision or normal lectures.\n"
    report += "9. Confident subjects are saved for the report, but they do not reduce scheduling yet.\n"

    return report


def analyze_schedule_report(parent):
    try:
        with open(SCHEDULE_FILE, "r") as f:
            data = json.load(f)
    except Exception:
        messagebox.showerror("Error", "No schedule found. Please create one first.")
        return

    report = analyze_schedule_data(data)

    report_window = tk.Toplevel(parent)
    report_window.title("Timetable Analysis Report")
    report_window.state("zoomed")
    report_window.configure(bg=BG_DARK)

    tk.Frame(report_window, bg=ACCENT, height=5).pack(fill="x")
    tk.Frame(report_window, bg=ACCENT2, height=2).pack(fill="x")

    header = tk.Frame(report_window, bg=BG_PANEL)
    header.pack(fill="x")

    tk.Label(
        header,
        text="Timetable Analysis Report",
        font=(FONT, 22, "bold"),
        bg=BG_PANEL,
        fg=TEXT,
    ).pack(pady=(20, 5))

    tk.Label(
        header,
        text="Subject-wise slot count, revision count, and lecture distribution",
        font=(FONT, 11),
        bg=BG_PANEL,
        fg=MUTED,
    ).pack(pady=(0, 15))

    text_frame = tk.Frame(report_window, bg=BG_DARK)
    text_frame.pack(fill="both", expand=True, padx=30, pady=20)

    scrollbar = ttk.Scrollbar(text_frame)
    scrollbar.pack(side="right", fill="y")

    report_box = tk.Text(
        text_frame,
        font=("Consolas", 12),
        bg=BG_CARD,
        fg=TEXT,
        insertbackground=ACCENT,
        relief="flat",
        bd=0,
        wrap="word",
        yscrollcommand=scrollbar.set,
    )
    report_box.pack(fill="both", expand=True)
    scrollbar.config(command=report_box.yview)

    report_box.insert("1.0", report)
    report_box.config(state="disabled")
def open_schedule(parent):
    menu = tk.Toplevel(parent)
    menu.title("Study Schedule")
    menu.state("zoomed")
    menu.resizable(True, True)
    menu.configure(bg=BG_DARK)

    tk.Frame(menu, bg=ACCENT, height=5).pack(fill="x")
    tk.Frame(menu, bg=ACCENT3, height=2).pack(fill="x")

    header = tk.Frame(menu, bg=BG_PANEL)
    header.pack(fill="x")

    tk.Label(header, text="Study Schedule", font=(FONT, 22, "bold"), bg=BG_PANEL, fg=TEXT).pack(pady=(20, 4))

    tk.Label(
        header,
        text="Create, view, or analyze your weekly timetable",
        font=(FONT, 11),
        bg=BG_PANEL,
        fg=MUTED,
    ).pack(pady=(0, 18))

    center = tk.Frame(menu, bg=BG_DARK)
    center.place(relx=0.5, rely=0.5, anchor="center", width=420)

    btn1 = styled_button(center, "Create New Schedule", ACCENT, lambda: [menu.destroy(), create_schedule(parent)])
    btn1.pack(fill="x", ipady=18, pady=10)

    btn2 = styled_button(center, "View Existing Schedule", ACCENT3, lambda: [menu.destroy(), view_schedule(parent)])
    btn2.pack(fill="x", ipady=18, pady=10)

    btn3 = styled_button(center, "Analyze Timetable", ACCENT2, lambda: analyze_schedule_report(menu), fg="#0a0f1e")
    btn3.pack(fill="x", ipady=18, pady=10)

    tk.Label(
        menu,
        text="Smart Learning  -  Schedule",
        font=(FONT, 9),
        bg=BG_DARK,
        fg="#1e3448"
    ).pack(side="bottom", pady=10)


def create_schedule(parent):
    form = tk.Toplevel(parent)
    form.title("Create Schedule")
    form.state("zoomed")
    form.resizable(True, True)
    form.configure(bg=BG_DARK)

    tk.Frame(form, bg=ACCENT, height=5).pack(fill="x")
    tk.Frame(form, bg=ACCENT2, height=2).pack(fill="x")

    header = tk.Frame(form, bg=BG_PANEL)
    header.pack(fill="x")

    tk.Label(
        header,
        text="Create Study Schedule",
        font=(FONT, 20, "bold"),
        bg=BG_PANEL,
        fg=TEXT
    ).pack(pady=(18, 4))

    tk.Label(
        header,
        text="Fill in your subjects and available time",
        font=(FONT, 11),
        bg=BG_PANEL,
        fg=MUTED,
    ).pack(pady=(0, 14))

    scroll_container = tk.Frame(form, bg=BG_DARK)
    scroll_container.pack(fill="both", expand=True)

    canvas = tk.Canvas(scroll_container, bg=BG_DARK, highlightthickness=0)
    vscroll = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vscroll.set)

    vscroll.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    form_frame = tk.Frame(canvas, bg=BG_DARK)
    canvas_window = canvas.create_window((0, 0), window=form_frame, anchor="nw")

    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    canvas.bind("<Configure>", on_canvas_configure)
    form_frame.bind("<Configure>", on_frame_configure)

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    content = tk.Frame(form_frame, bg=BG_DARK, width=500)
    content.pack(pady=20, anchor="center")

    subject_entries = []

    field_label(content, "How many subjects do you have?")
    subs_entry = input_box(content)

    subjects_frame = tk.Frame(content, bg=BG_DARK)
    subjects_frame.pack(fill="x")

    def generate_subject_fields():
        for widget in subjects_frame.winfo_children():
            widget.destroy()

        subject_entries.clear()

        try:
            count = int(subs_entry.get())
        except Exception:
            messagebox.showerror("Error", "Enter a valid number of subjects.")
            return

        if count <= 0:
            messagebox.showerror("Error", "Enter at least one subject.")
            return

        for i in range(count):
            tk.Label(
                subjects_frame,
                text=f"Subject {i + 1}:",
                font=(FONT, 10),
                fg=MUTED,
                bg=BG_DARK,
                anchor="w",
            ).pack(fill="x", pady=(10, 2))

            entry = tk.Entry(
                subjects_frame,
                font=(FONT, 11),
                bg=BG_INPUT,
                fg=TEXT,
                insertbackground=ACCENT,
                relief="flat",
                bd=0,
            )
            entry.pack(fill="x", ipady=8)
            tk.Frame(subjects_frame, bg="#1e3448", height=1).pack(fill="x")
            subject_entries.append(entry)

        form.after(100, lambda: canvas.yview_moveto(1.0))

    add_btn = styled_button(
        content,
        "Add Subject Fields",
        BG_INPUT,
        generate_subject_fields,
        fg="#74b9ff"
    )
    add_btn.pack(fill="x", ipady=9, pady=(8, 0))

    field_label(content, "Which subjects are you weak in?  Separate multiple subjects with commas")
    weak_entry = input_box(content)

    field_label(content, "Which subjects are you confident in?  Separate multiple subjects with commas")
    confident_entry = input_box(content)

    field_label(content, "Start Time  (HH:MM)  e.g. 07:00")
    start_entry = input_box(content)

    field_label(content, "End Time  (HH:MM)  e.g. 15:00")
    end_entry = input_box(content)

    def submit():
        try:
            subjects = [entry.get().strip() for entry in subject_entries if entry.get().strip()]
            weak_subjects = parse_subject_list(weak_entry.get().strip())
            strong_subjects = parse_subject_list(confident_entry.get().strip())
            start_time = datetime.strptime(start_entry.get().strip(), "%H:%M")
            end_time = datetime.strptime(end_entry.get().strip(), "%H:%M")
        except Exception:
            messagebox.showerror("Error", "Please fill all fields correctly. Use HH:MM for time.")
            return

        if not subjects:
            messagebox.showerror("Error", "Please add at least one subject.")
            return

        if len(set(subjects)) != len(subjects):
            messagebox.showerror("Error", "Subject names should not repeat.")
            return

        invalid_weak_subjects = [subject for subject in weak_subjects if subject not in subjects]

        if invalid_weak_subjects:
            messagebox.showerror(
                "Error",
                "Weak subjects must match your subject names exactly.\nInvalid: "
                + ", ".join(invalid_weak_subjects),
            )
            return

        invalid_strong_subjects = [subject for subject in strong_subjects if subject not in subjects]

        if invalid_strong_subjects:
            messagebox.showerror(
                "Error",
                "Confident subjects must match your subject names exactly.\nInvalid: "
                + ", ".join(invalid_strong_subjects),
            )
            return

        if end_time <= start_time:
            messagebox.showerror("Error", "End time must be later than start time.")
            return

        time_slots, slot_types = create_time_slots(start_time, end_time)

        if not any(slot_type == "Study" for slot_type in slot_types):
            messagebox.showerror("Error", "Your time range is too short for a 1-hour study slot.")
            return

        weekly_schedule = build_weekly_schedule(subjects, weak_subjects, time_slots, slot_types)
        completion = {day: [False] * len(time_slots) for day in DAYS}

        save_payload = {
            "times": time_slots,
            "slot_types": slot_types,
            "schedule": weekly_schedule,
            "completion": completion,
            "subject_count": len(subjects),
            "subjects": subjects,
            "weak_subject": ", ".join(weak_subjects),
            "strong_subject": ", ".join(strong_subjects),
            "weak_subjects": weak_subjects,
            "strong_subjects": strong_subjects,
            "start_time": start_time.strftime("%H:%M"),
            "end_time": end_time.strftime("%H:%M"),
        }

        with open(SCHEDULE_FILE, "w") as f:
            json.dump(save_payload, f, indent=2)

        form.destroy()
        view_schedule(parent)

    generate_btn = styled_button(
        content,
        "Generate My Schedule",
        ACCENT2,
        submit,
        fg="#0a0f1e"
    )
    generate_btn.pack(fill="x", ipady=15, pady=(20, 30))

    tk.Label(
        form,
        text="Smart Learning  -  Schedule Creator",
        font=(FONT, 9),
        bg=BG_DARK,
        fg="#1e3448"
    ).pack(side="bottom", pady=8)
def view_schedule(parent):
    try:
        with open(SCHEDULE_FILE, "r") as f:
            data = json.load(f)
    except Exception:
        messagebox.showerror("Error", "No schedule found. Please create one first.")
        return

    window = tk.Toplevel(parent)
    window.title("Weekly Timetable")
    window.state("zoomed")
    window.resizable(True, True)
    window.configure(bg=BG_DARK)

    times = data["times"]
    slot_types = data["slot_types"]
    schedule = data["schedule"]
    completion = data.get("completion", {day: [False] * len(times) for day in DAYS})

    total_study = sum(1 for slot_type in slot_types if slot_type == "Study") * len(DAYS)
    progress_var = tk.StringVar()

    all_cell_frames = []
    nav_buttons = []

    def recalc_progress():
        done = 0

        for day in DAYS:
            for i, slot_type in enumerate(slot_types):
                if slot_type == "Study" and i < len(completion.get(day, [])) and completion[day][i]:
                    done += 1

        pct = (done / total_study * 100) if total_study > 0 else 0
        progress_var.set(f"Progress: {pct:.1f}%")

    recalc_progress()

    def block_close_running():
        messagebox.showwarning("Timer Running", "Please pause the timer before closing.")

    def close_while_paused():
        timer.stop()
        window.destroy()

    def close_normal():
        timer.stop()
        clear_saved_timer_state()
        window.destroy()

    def on_session_complete():
        messagebox.showinfo("Session Completed", "Great work! Session completed.")

    def freeze_ui():
        for frame, _, _ in all_cell_frames:
            frame.unbind("<Button-1>")
            frame.unbind("<Double-Button-1>")

            for child in frame.winfo_children():
                child.unbind("<Button-1>")
                child.unbind("<Double-Button-1>")

        for btn in nav_buttons:
            btn.configure(state="disabled")

        window.protocol("WM_DELETE_WINDOW", block_close_running)

    def unfreeze_ui():
        for frame, row_idx, day in all_cell_frames:
            bind_cell(frame, row_idx, day)

        for btn in nav_buttons:
            btn.configure(state="normal")

        if timer.paused:
            window.protocol("WM_DELETE_WINDOW", close_while_paused)
        else:
            window.protocol("WM_DELETE_WINDOW", close_normal)

    def cell_bg(label):
        if label == "Short Break":
            return "#1a3a1a"
        if label == "Long Break":
            return "#1a2a1a"
        if label.startswith("Revision"):
            return "#1e2d45"
        if "Extra Focus" in label:
            return "#2a1a00"
        return BG_CARD

    def cell_fg(label):
        if label in ("Short Break", "Long Break"):
            return "#55efc4"
        if label.startswith("Revision"):
            return "#74b9ff"
        if "Extra Focus" in label:
            return ACCENT2
        return TEXT

    def make_complete_toggle(row_idx, day, frame, label_widget, original_text):
        def toggle(event):
            if row_idx >= len(completion[day]):
                return

            completion[day][row_idx] = not completion[day][row_idx]

            is_done = completion[day][row_idx]
            new_bg = "#1a3a1a" if is_done else cell_bg(original_text)
            new_fg = "#27ae60" if is_done else cell_fg(original_text)
            new_text = "Done - " + original_text if is_done else original_text

            frame.configure(bg=new_bg)
            label_widget.configure(bg=new_bg, fg=new_fg, text=new_text)
            recalc_progress()

        return toggle

    def on_cell_double_click(row_idx, day):
        if timer.is_active():
            messagebox.showwarning(
                "Timer Active",
                "A session is already running. Pause or reset it first."
            )
            return

        slot_label = schedule[day][row_idx]

        try:
            start_text, end_text = times[row_idx].split(" - ")
            t_start = datetime.strptime(start_text.strip(), "%H:%M")
            t_end = datetime.strptime(end_text.strip(), "%H:%M")
            duration = int((t_end - t_start).total_seconds())
        except Exception:
            duration = 3600

        session_label = f"{day} - {slot_label}"
        timer_session_var.set(session_label)

        timer.start(
            root=window,
            duration_seconds=duration,
            display_var=timer_display_var,
            session_var=timer_session_var,
            on_complete=on_session_complete,
            on_freeze=freeze_ui,
            on_unfreeze=unfreeze_ui,
            session_label=session_label,
        )

    def bind_cell(frame, row_idx, day):
        label_widget = None

        for child in frame.winfo_children():
            if isinstance(child, tk.Label):
                label_widget = child
                break

        if label_widget is not None:
            original_text = schedule[day][row_idx]
            toggle = make_complete_toggle(row_idx, day, frame, label_widget, original_text)
            frame.bind("<Button-1>", toggle)
            label_widget.bind("<Button-1>", toggle)

        double_click = lambda e, r=row_idx, d=day: on_cell_double_click(r, d)
        frame.bind("<Double-Button-1>", double_click)

        for child in frame.winfo_children():
            child.bind("<Double-Button-1>", double_click)

    tk.Frame(window, bg=ACCENT, height=5).pack(fill="x")
    tk.Frame(window, bg=ACCENT3, height=2).pack(fill="x")

    header = tk.Frame(window, bg=BG_PANEL)
    header.pack(fill="x")

    top_row = tk.Frame(header, bg=BG_PANEL)
    top_row.pack(fill="x", padx=24, pady=(16, 4))

    tk.Label(
        top_row,
        text="Weekly Timetable",
        font=(FONT, 20, "bold"),
        bg=BG_PANEL,
        fg=TEXT
    ).pack(side="left")

    right_top = tk.Frame(top_row, bg=BG_PANEL)
    right_top.pack(side="right")

    progress_frame = tk.Frame(right_top, bg=ACCENT2, padx=12, pady=6)
    progress_frame.pack(side="right", padx=(8, 0))

    tk.Label(
        progress_frame,
        textvariable=progress_var,
        font=(FONT, 11, "bold"),
        bg=ACCENT2,
        fg="#0a0f1e"
    ).pack()

    def save_changes():
        data["completion"] = completion

        with open(SCHEDULE_FILE, "w") as f:
            json.dump(data, f, indent=2)

        messagebox.showinfo("Saved", "Schedule changes saved successfully.")

    def edit_schedule():
        if timer.is_active():
            messagebox.showwarning("Timer Active", "Pause or reset the timer before editing.")
            return

        timer.stop()
        clear_saved_timer_state()
        window.destroy()
        create_schedule(parent)

    save_btn = styled_button(right_top, "Save Changes", ACCENT3, save_changes)
    save_btn.pack(side="right", ipadx=12, ipady=7, padx=(0, 4))

    edit_btn = styled_button(right_top, "Edit Schedule", BG_INPUT, edit_schedule, fg=TEXT)
    edit_btn.pack(side="right", ipadx=12, ipady=7, padx=(0, 6))

    report_btn = styled_button(
        right_top,
        "Report",
        ACCENT2,
        lambda: analyze_schedule_report(window),
        fg="#0a0f1e"
    )
    report_btn.pack(side="right", ipadx=12, ipady=7, padx=(0, 6))

    nav_buttons.extend([save_btn, edit_btn, report_btn])

    tk.Label(
        header,
        text="Single-click a study cell to mark it done. Double-click a study cell to start timer.",
        font=(FONT, 9),
        bg=BG_PANEL,
        fg=MUTED,
    ).pack(anchor="w", padx=24, pady=(0, 6))

    timer_display_var, timer_session_var = build_timer_panel(header)

    saved = load_saved_timer_state()

    if saved:
        saved_remaining, saved_label = saved
        timer_display_var.set(f"{saved_remaining // 60:02d}:{saved_remaining % 60:02d}")
        timer_session_var.set(saved_label if saved_label else "Paused session")

        timer.stop()
        timer._root = window
        timer.display_var = timer_display_var
        timer.session_var = timer_session_var
        timer.remaining = saved_remaining
        timer.paused = True
        timer.running = False
        timer.active_session_label = saved_label
        timer._on_complete = on_session_complete
        timer._on_freeze = freeze_ui
        timer._on_unfreeze = unfreeze_ui
        timer._update_display()

        window.after(
            300,
            lambda: messagebox.showinfo(
                "Paused Session Restored",
                f"A paused session was found:\n{saved_label}\n\nPress Resume to continue.",
            ),
        )

    table_outer = tk.Frame(window, bg=BG_DARK)
    table_outer.pack(fill="both", expand=True, pady=(6, 0))

    h_scroll = ttk.Scrollbar(table_outer, orient="horizontal")
    v_scroll = ttk.Scrollbar(table_outer, orient="vertical")

    canvas = tk.Canvas(
        table_outer,
        bg=BG_DARK,
        highlightthickness=0,
        xscrollcommand=h_scroll.set,
        yscrollcommand=v_scroll.set,
    )

    h_scroll.config(command=canvas.xview)
    v_scroll.config(command=canvas.yview)

    h_scroll.pack(side="bottom", fill="x")
    v_scroll.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    table_frame = tk.Frame(canvas, bg=BG_DARK)
    canvas.create_window((0, 0), window=table_frame, anchor="nw")

    def on_table_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    table_frame.bind("<Configure>", on_table_configure)

    def mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", mousewheel)

    time_width = 110
    day_width = 160
    row_height = 60
    header_height = 38

    header_row = tk.Frame(table_frame, bg=BG_DARK)
    header_row.pack(fill="x")

    def header_cell(parent_frame, text, width):
        frame = tk.Frame(
            parent_frame,
            bg=ACCENT,
            width=width,
            height=header_height
        )
        frame.pack_propagate(False)
        frame.pack(side="left")

        tk.Label(
            frame,
            text=text,
            font=(FONT, 11, "bold"),
            bg=ACCENT,
            fg="#ffffff"
        ).pack(expand=True)

    header_cell(header_row, "Time", time_width)

    for day in DAYS:
        header_cell(header_row, day, day_width)

    tk.Frame(table_frame, bg="#0d1a2a", height=2).pack(fill="x")

    for row_idx, (time_text, slot_type) in enumerate(zip(times, slot_types)):
        row_bg = "#080d1a" if row_idx % 2 == 0 else BG_DARK
        row_frame = tk.Frame(table_frame, bg=row_bg)
        row_frame.pack(fill="x")

        time_cell = tk.Frame(
            row_frame,
            bg=ACCENT,
            width=time_width,
            height=row_height
        )
        time_cell.pack_propagate(False)
        time_cell.pack(side="left")

        tk.Label(
            time_cell,
            text=time_text,
            font=(FONT, 9, "bold"),
            bg=ACCENT,
            fg="#ffffff",
            wraplength=time_width - 6,
            justify="center",
        ).pack(expand=True)

        for day in DAYS:
            label = schedule[day][row_idx] if row_idx < len(schedule[day]) else ""
            done = row_idx < len(completion.get(day, [])) and completion[day][row_idx]

            bg_color = "#1a3a1a" if done else cell_bg(label)
            fg_color = "#27ae60" if done else cell_fg(label)
            display_text = "Done - " + label if done else label

            cell_frame = tk.Frame(
                row_frame,
                bg=bg_color,
                width=day_width,
                height=row_height,
                highlightthickness=1,
                highlightbackground="#0d1a2a",
            )
            cell_frame.pack_propagate(False)
            cell_frame.pack(side="left")

            label_widget = tk.Label(
                cell_frame,
                text=display_text,
                font=(FONT, 10, "bold") if "Extra Focus" in label else (FONT, 10),
                bg=bg_color,
                fg=fg_color,
                wraplength=day_width - 10,
                justify="center",
            )
            label_widget.pack(expand=True)

            if slot_type == "Study":
                all_cell_frames.append((cell_frame, row_idx, day))
                bind_cell(cell_frame, row_idx, day)

        tk.Frame(table_frame, bg="#0d1a2a", height=1).pack(fill="x")

    if saved:
        window.protocol("WM_DELETE_WINDOW", close_while_paused)
    else:
        window.protocol("WM_DELETE_WINDOW", close_normal)

    tk.Label(
        window,
        text="Smart Learning  -  Weekly Timetable",
        font=(FONT, 9),
        bg=BG_DARK,
        fg="#1e3448"
    ).pack(side="bottom", pady=6)


def main():
    root = tk.Tk()
    root.title("Smart Learning")
    root.state("zoomed")
    root.configure(bg=BG_DARK)

    tk.Frame(root, bg=ACCENT, height=5).pack(fill="x")
    tk.Frame(root, bg=ACCENT3, height=2).pack(fill="x")

    header = tk.Frame(root, bg=BG_PANEL)
    header.pack(fill="x")

    tk.Label(
        header,
        text="Smart Learning",
        font=(FONT, 26, "bold"),
        bg=BG_PANEL,
        fg=TEXT
    ).pack(pady=(24, 6))

    tk.Label(
        header,
        text="Your intelligent study companion",
        font=(FONT, 12),
        bg=BG_PANEL,
        fg=MUTED
    ).pack(pady=(0, 20))

    center = tk.Frame(root, bg=BG_DARK)
    center.place(relx=0.5, rely=0.5, anchor="center", width=460)

    btn1 = styled_button(
        center,
        "Study Schedule",
        ACCENT,
        lambda: open_schedule(root)
    )
    btn1.pack(fill="x", ipady=18, pady=10)

    btn2 = styled_button(
        center,
        "Progress Tracker",
        ACCENT2,
        lambda: messagebox.showinfo("Coming Soon", "Progress Tracker coming soon."),
        fg="#0a0f1e"
    )
    btn2.pack(fill="x", ipady=18, pady=10)

    btn3 = styled_button(
        center,
        "Reminders",
        ACCENT3,
        lambda: messagebox.showinfo("Coming Soon", "Reminders coming soon.")
    )
    btn3.pack(fill="x", ipady=18, pady=10)

    tk.Label(
        root,
        text="Smart Learning  v1.0",
        font=(FONT, 9),
        bg=BG_DARK,
        fg="#1e3448"
    ).pack(side="bottom", pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
