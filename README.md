# 🎓 Smart Learning

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![GUI](https://img.shields.io/badge/GUI-Tkinter-green)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-Educational-lightgrey)

---

## 📌 About the Project

Smart Learning is a desktop application built using Python that helps students organize and improve their study routine.

Instead of using multiple apps, this system combines scheduling, learning resources, video search, and past paper access into a single platform.

---

## 🎯 Key Highlights

* Smart timetable generation
* Weak subject prioritization
* Built-in study timer
* Resource & PDF finder
* Video learning from notes
* Past papers access
* Progress tracking

---

## ✨ Features

### 📅 Smart Study Schedule

* Automatically generates weekly timetable
* Includes breaks and revision slots
* Prioritizes weak subjects
* Tracks completion progress

---

### ⏱ Study Timer

* Start session by double-click
* Pause, Resume, Reset
* Auto-save timer state

---

### 🎬 Video Learning

* Search videos by topic
* Upload notes/PDF to auto-generate topics
* Opens relevant YouTube videos
* Save all links as PDF

---

### 📚 Notes & Resource Finder

* Search study materials instantly
* Filter by subject, topic, level
* Open PDFs directly
* Save links

---

### 📄 Past Papers Finder

* Filter by subject and year
* Opens Google search results
* Quick access to exam papers

---

### 📊 Progress Tracking

* Mark tasks as completed
* Displays progress percentage
* Generates detailed analysis report

---

## 🛠 Tech Stack

* Python
* Tkinter
* Pandas
* JSON
* yt-dlp
* ReportLab

---

## ⚙️ Installation

Clone the repository:

```
git clone https://github.com/AyushD2406/Smart-learning-app.git
```

Go to project folder:

```
cd Smart-learning-app
```

Install dependencies:

```
pip install pandas yt-dlp reportlab
```

Run the application:

```
python app.py
```

---

## 📂 Project Structure

smart-learning-app/
├── src/
│   ├── __init__.py
│   ├── main.py                 # renamed from app.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py      # main UI components
│   │   ├── dashboard.py        # notes dashboard
│   │   └── styles.py           # shared UI constants
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── notes_manager.py    # add_notes.py functionality
│   │   ├── video_manager.py    # video.py functionality
│   │   ├── past_papers.py      # existing past_papers.py
│   │   └── schedule.py         # existing schedule.py
│   └── utils/
│       ├── __init__.py
│       ├── file_handler.py     # file operations
│       └── config.py           # configuration settings
├── data/
│   ├── datasets/
│   │   ├── Complete_Study_Materials_FINAL.xlsx
│   │   ├── Past_Papers_UPDATED.xlsx
│   │   └── other_excel_files.xlsx
│   └── user_data/
│       ├── schedule.json
│       ├── timer_state.json
│       └── saved_links.txt
├── assets/
│   ├── icons/
│   └── fonts/
├── tests/
│   ├── __init__.py
│   └── test_modules/
├── docs/
│   ├── README.md
│   ├── requirements.txt
│   └── user_guide.md
├── .venv/
├── .gitignore
└── requirements.txt                

---

## 📸 Screenshots

(Add images here)

<img width="1019" height="533" alt="Dashboard" src="https://github.com/user-attachments/assets/e382d7e9-2cf6-4a02-b6b9-ab27cb4ca7c7" />
<img width="969" height="527" alt="Schedule" src="https://github.com/user-attachments/assets/7c77fff1-66ea-45c0-bbcb-c1e276e710d9" />
<img width="1012" height="586" alt="Video" src="https://github.com/user-attachments/assets/2c123e16-cf07-4f2f-b324-284dc58fd16a" />
<img width="505" height="417" alt="Notes" src="https://github.com/user-attachments/assets/14100d81-3afc-405b-92e1-bb940fced98e" />Assets/Video.jpeg


---

## 🚀 Future Scope

* Mobile app version
* AI-based recommendations
* Cloud sync
* Reminder system

---

## 👨‍💻 Author

Ayush & Vidhi

---

## 📜 License

For educational purposes only

---

## ⭐ Support

If you like this project, consider giving it a star ⭐


