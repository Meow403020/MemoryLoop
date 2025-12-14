import sqlite3
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from database import DB_NAME

    #create a class to organize ur functions for adding questions
    #qdialog is a pyqt class for popup dialog windows
class AddQuestion(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add New Question")
        self.setGeometry(400, 300, 450, 380)

        layout = QVBoxLayout(self)
        self.setStyleSheet("""
            QDialog {
                background-color: #f7fbff;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #004a7c;
                margin-top: 6px;
            }
            QComboBox, QLineEdit {
                background-color: white;
                padding: 8px;
                border: 2px solid #007BFF;
                border-radius: 8px;
                font-size: 13px;
            }
            QComboBox:hover, QLineEdit:hover {
                border: 2px solid #0056b3;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                padding: 10px;
                font-size: 15px;
                border-radius: 10px;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        title = QLabel("➕ Add New Question")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #003d66; margin-bottom: 10px;")
        layout.addWidget(title, alignment=Qt.AlignCenter)

        # Category Selector
        layout.addWidget(QLabel("Select Category:"))
        self.categoryBox = QComboBox()
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT name FROM categories")
        rows = c.fetchall()
        conn.close()
        for r in rows:
            self.categoryBox.addItem(r[0])

        layout.addWidget(self.categoryBox)

        # Add category button
        self.addCategoryBtn = QPushButton("➕ Add Category")
        self.addCategoryBtn.clicked.connect(self.addCategory)
        layout.addWidget(self.addCategoryBtn)


        # Question Input
        layout.addWidget(QLabel("Question:"))
        self.questionInput = QLineEdit()
        self.questionInput.setPlaceholderText("Enter question text")
        layout.addWidget(self.questionInput)

        # Correct Answer
        layout.addWidget(QLabel("Correct Answer:"))
        self.correctAns = QLineEdit()
        self.correctAns.setPlaceholderText("Enter correct answer")
        layout.addWidget(self.correctAns)

        # Wrong Answers
        layout.addWidget(QLabel("Wrong Answers:"))

        wrongLayout = QHBoxLayout()

        self.wrongInput = QLineEdit()
        self.wrongInput.setPlaceholderText("Enter a wrong answer")
        wrongLayout.addWidget(self.wrongInput)

        self.addWrongBtn = QPushButton("Add")
        self.addWrongBtn.clicked.connect(self.addWrongAnswer)
        wrongLayout.addWidget(self.addWrongBtn)

        layout.addLayout(wrongLayout)

        self.wrongList = QListWidget()
        layout.addWidget(self.wrongList)

        self.wrongAnswers = []

        # Save Button
        self.saveBtn = QPushButton("💾 Save Question")
        self.saveBtn.clicked.connect(self.saveQuestion)
        layout.addWidget(self.saveBtn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def addCategory(self):
        text, ok = QInputDialog.getText(self, "Add Category", "Enter category name:")
        if not ok or not text.strip():
            return

        text = text.strip()

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO categories (name) VALUES (?)", (text,))
            conn.commit()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Duplicate", "Category already exists.")
            conn.close()
            return
        conn.close()

        self.categoryBox.addItem(text)
        QMessageBox.information(self, "Success", "Category added successfully!")

    def saveQuestion(self):
        categ = self.categoryBox.currentText()
        qstn = self.questionInput.text()
        correct = self.correctAns.text()
        wrongs = ",".join(self.wrongAnswers)

        if not qstn or not correct or not wrongs:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO questions (subject, question, correctAns, wrongAns) VALUES (?,?,?,?)",
                (categ, qstn, correct, wrongs))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", "Question added successfully!")
        self.accept()

    def addWrongAnswer(self):
        text = self.wrongInput.text().strip()
        if not text:
            return

        if text in self.wrongAnswers:
            QMessageBox.warning(self, "Duplicate", "This answer is already added.")
            return

        self.wrongAnswers.append(text)
        self.wrongList.addItem(text)
        self.wrongInput.clear()


