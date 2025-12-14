import sqlite3
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from db.database import DB_NAME

class ManageQuestions(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manage Questions")
        self.resize(800, 850)
        self.move(QApplication.primaryScreen().availableGeometry().center() - self.frameGeometry().center())


        # MAIN LAYOUT
        main = QVBoxLayout(self)

        ## ---- CATEGORY AREA ----
        catScroll = QScrollArea()
        catScroll.setWidgetResizable(True)
        catWidget = QWidget()
        self.categoryLayout = QVBoxLayout(catWidget)
        catScroll.setWidget(catWidget)

        main.addWidget(QLabel("<b>Categories</b>"))
        main.addWidget(catScroll, stretch=3)



        ## ---- QUESTIONS AREA (SCROLL) ----
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.questionLayout = QVBoxLayout(content)
        scroll.setWidget(content)
        main.addWidget(QLabel("<b>Questions</b>"))
        main.addWidget(scroll, stretch=4)


        # Load from DB
        self.loadCategories()
        self.loadQuestions()

    # ===================== CATEGORIES =====================
    def loadCategories(self):
        # clear category list
        while self.categoryLayout.count():
            item = self.categoryLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT name FROM categories")
        categories = c.fetchall()
        conn.close()

        for (name,) in categories:
            self.addCategoryBox(name)

    def addCategoryBox(self, name):
        box = QFrame()
        box.setStyleSheet("""
            QFrame { background-color: #e6f2ff; border: 2px solid #3399ff;
                     border-radius: 10px; padding: 8px; margin: 6px 0; }
        """)
        layout = QHBoxLayout(box)
        layout.addWidget(QLabel(f"<b>{name}</b>"))

        deleteBtn = QPushButton("Delete Category")
        deleteBtn.setStyleSheet("background-color:#ff4d4d; color:white; border-radius:6px;")
        deleteBtn.clicked.connect(lambda _, n=name, f=box: self.deleteCategory(n, f))
        layout.addWidget(deleteBtn)

        self.categoryLayout.addWidget(box)

    def deleteCategory(self, name, frame):
        reply = QMessageBox.question(
            self, "Delete Category",
            f"Delete ALL questions under '{name}' as well?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )
        if reply == QMessageBox.Cancel:
            return

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        if reply == QMessageBox.Yes:
            c.execute("DELETE FROM questions WHERE subject=?", (name,))
            c.execute("DELETE FROM categories WHERE name=?", (name,))
        else:
            c.execute("SELECT COUNT(*) FROM questions WHERE subject=?", (name,))
            if c.fetchone()[0] > 0:
                QMessageBox.warning(self, "Cannot Delete",
                                    "There are still questions in this category.")
                conn.close()
                return
            c.execute("DELETE FROM categories WHERE name=?", (name,))
        conn.commit()
        conn.close()

        frame.deleteLater()
        self.loadQuestions()
        self.loadCategories()

    # ===================== QUESTIONS =====================
    def loadQuestions(self):
        # clear questions list
        while self.questionLayout.count():
            item = self.questionLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT id, subject, question, correctAns, wrongAns FROM questions")
        rows = c.fetchall()
        conn.close()

        for qid, subject, question, correct, wrongs in rows:
            self.addQuestionBox(qid, subject, question, correct, wrongs)

    def addQuestionBox(self, qid, subject, question, correct, wrongs):
        box = QFrame()
        box.setStyleSheet("""
            QFrame { background-color: #f0f8ff; border: 2px solid #007BFF;
                     border-radius: 12px; padding: 15px; margin: 10px 0; }
        """)
        boxLayout = QVBoxLayout(box)

        topRow = QHBoxLayout()
        topRow.addWidget(QLabel(f"<b>{subject}</b>"))
        delBtn = QPushButton("Delete")
        delBtn.clicked.connect(lambda _, id=qid, frame=box: self.deleteQuestion(id, frame))
        topRow.addWidget(delBtn, alignment=Qt.AlignRight)
        boxLayout.addLayout(topRow)

        qLabel = QLabel(f"<b>Q:</b> {question}")
        qLabel.setWordWrap(True)
        boxLayout.addWidget(qLabel)

        boxLayout.addWidget(QLabel(f"<span style='color:green;'><b>✔ Correct:</b> {correct}</span>"))
        boxLayout.addWidget(QLabel(f"<span style='color:red;'><b>✘ Wrong:</b> {wrongs}</span>"))

        self.questionLayout.addWidget(box)

    def deleteQuestion(self, qid, frame):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("DELETE FROM questions WHERE id=?", (qid,))
        conn.commit()
        conn.close()

        frame.deleteLater()
        QMessageBox.information(self, "Deleted", "Question removed successfully!")


