import sys
import os
import random
import sqlite3

from PyQt5.QtWidgets import (
    QApplication, QWidget, QDialog, QLabel, QPushButton,
    QVBoxLayout, QMessageBox
)
from PyQt5.QtCore import (
    Qt, QTimer, pyqtSignal, QUrl
)
from PyQt5.QtGui import (
    QFont, QPixmap, QPainter, QColor
)
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel

# your own project imports
from database import DB_NAME, createdb
from ui.dashboard import Dashboard


#class for actual question popup
class QuestionPopup(QDialog):
    #constructor but make default subject math
    def __init__(self, subject="Math", mode="Study Mode", parent=None):
        super().__init__()
        self.mode = mode

        
        #window title
        self.setWindowTitle("Pop Quiz")
        #makes sure the pop is ontop of all windows
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        #positions the popup xy on screen and sizes it width and height
        # Bigger popup window
        self.setGeometry(350, 200, 450, 350)




        #make vertical layout of widgets
        layout = QVBoxLayout()
        #create a web view widget so you can add html, css, and js to style it and make animated ui

        #if u want web typa styled html call the webengineview
        self.webView = QWebEngineView()
        #get a random question from that subject in the db
        question, options, correctAnswer = self.generateQuest(subject)
        #make sure to store the correct answer before shuffling
        self.correctAns = correctAnswer

        #store the question text
        self.quest = question
        self.channel = QWebChannel()
        self.bridge = QuestionBridge(self)
        self.channel.registerObject("bridge", self.bridge)
        self.webView.page().setWebChannel(self.channel)



        htmlStyl = self.buildHtml(question, options)
        self.webView.setHtml(htmlStyl)
        layout.addWidget(self.webView)

#HERERERERERERE

        """question_label = QLabel(question)
        question_label.setWordWrap(True)
        layout.addWidget(question_label)"""
        #officialize it
        self.setLayout(layout)

        #will close the popup if the user hasnt answered
        #IMPLEMENT PUNISHMENT
        self._answered = False
        QTimer.singleShot(15000, self._auto_close)

        self.countdown_label = QLabel("You have 10 seconds to answer", self)
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #003399;
        """)
        layout.insertWidget(0, self.countdown_label)   # add to the top of layout
        self.time_remaining = 10
        self.timer_countdown = QTimer(self)
        self.timer_countdown.timeout.connect(self.update_timer)
        self.timer_countdown.start(1000)

    def update_timer(self):
        self.time_remaining -= 1
        self.countdown_label.setText(f"You have {self.time_remaining} seconds to answer")

        if self.time_remaining <= 0:
            self.timer_countdown.stop()
            self._answered = False
            self._auto_close()



    def _auto_close(self):
        if self._answered:
            return   # user already answered

        # treat timeout as wrong answer (Gaming Mode only)
        if self.mode == "Gaming Mode":
            import random
            punishment = random.choice(["freeze", "jumpscare"])
            parent = self.parent()

            # If popup has no parent (should never happen but avoid crashes)
            if not parent:
                self.accept()
                return

            # stop popup timer immediately
            parent.timer.stop()
            parent.freezeActive = True   # block popups during punishment

            if punishment == "jumpscare":
                self.jumpscare = JumpScareOverlay(self.correctAns, duration=7000, image_path="jumpscare.png")
                self.jumpscare.closed.connect(self._after_jumpscare)
                self.jumpscare.showFullScreen()
                self.accept()   # close popup NOW
                return

            else:  # freeze
                self.freeze_overlay = FreezeOverlay(self.correctAns, duration=6000)
                self.freeze_overlay.closed.connect(self.freezeEnded)
                self.freeze_overlay.showFullScreen()
                self.accept()   # close popup NOW
                return

        # if not gaming mode
        self.accept()


    def buildHtml(self, question, options):
        buttons_html = "".join([
            f'<button onclick="answerClicked(\'{opt}\')">{opt}</button>' for opt in options
        ])

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <style>
                body {{
                    background: #f0f4f8;
                    font-family: 'Arial', sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }}
                .container {{
                    background: white;
                    padding: 20px 30px;
                    border-radius: 12px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    width: 90%;
                    max-width: 700px;
                    min-width: 500px;

                    text-align: center;
                }}
                h2 {{
                    font-size: 22px;
                    margin-bottom: 15px;
                    color: #333;
                }}
                button {{
                    background-color: #007BFF;
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    margin: 8px;
                    border-radius: 8px;
                    font-size: 16px;
                    cursor: pointer;
                    transition: 0.3s;
                    width: 90%;
                }}
                button:hover {{
                    background-color: #0056b3;
                }}
            </style>
            <script>
                var bridge;
                new QWebChannel(qt.webChannelTransport, function(channel) {{
                    bridge = channel.objects.bridge;
                }});
                function answerClicked(option) {{
                    bridge.checkAnswer(option);
                }}
            </script>
        </head>
        <body>
            <div class="container">
                <h2>{question}</h2>
                {buttons_html}
            </div>
        </body>
        </html>
        """
        return html
    def check_answer(self, selected):
        self._answered = True
        self.timer_countdown.stop()

        # Correct answer
        if selected.strip().lower() == self.correctAns.strip().lower():
            QMessageBox.information(self, "Correct!", "Great job")
            parent = self.parent()
            if parent and getattr(parent, "freezeActive", False):
                parent.freezeActive = False
                parent.timer.start(parent.freqSlider.value() * 1000)
            self.accept()
            return

        # Incorrect branch
        QMessageBox.warning(self, "Incorrect", "Better luck next time")

        if self.mode == "Gaming Mode":
            import random
            punishment = random.choice(["freeze", "jumpscare"])
            parent = self.parent()

            if parent:
                parent.freezeActive = True
                parent.timer.stop()

            if punishment == "jumpscare":
                self.jumpscare = JumpScareOverlay(self.correctAns, duration=7000, image_path="jumpscare.png")
                self.jumpscare.closed.connect(self._after_jumpscare)
                self.jumpscare.showFullScreen()
                self.accept()    # 🔥 close popup
                return

            else:  # freeze
                self.freeze_overlay = FreezeOverlay(self.correctAns, duration=10000)
                self.freeze_overlay.closed.connect(self.freezeEnded)
                self.freeze_overlay.showFullScreen()
                self.accept()    # 🔥 close popup
                return


        # If not gaming mode, just close popup
        self.accept()



    def _after_jumpscare(self):
        parent = self.parent()
        if not parent:
            return

        # Jumpscare is over — end punishment fully
        parent.freezeActive = False

        # Start 3-second cooldown to prevent instant popup after jumpscare
        parent.punishmentCooldown = True
        QTimer.singleShot(3000, lambda: setattr(parent, "punishmentCooldown", False))

        # Resume popup timer ONLY if popups are running and no freeze is active
        if parent.popupsRunning and not parent.freezeActive:
            parent.timer.start(parent.freqSlider.value() * 1000)



    def _start_freeze_overlay(self, duration=10000):
        """Create and show the blue FreezeOverlay and wire up its closed handler."""
        # create freeze overlay (it emits closed when it ends)
        self.freeze_overlay = FreezeOverlay(self.correctAns, duration=duration)
        self.freeze_overlay.showFullScreen()
        # connect restore handler
        self.freeze_overlay.closed.connect(self.freezeEnded)


    def apply_freeze_penalty(self):
        overlay = QMessageBox(self)
        overlay.setWindowTitle("Penalty!")
        overlay.setText("You got the question wrong — screen frozen for 7 seconds!")
        overlay.setStandardButtons(QMessageBox.NoButton)
        overlay.show()

        QTimer.singleShot(7000, lambda: (
            overlay.close(),
            setattr(self.parent, "freezeActive", False)
        ))

    def freezeEnded(self):
        parent = self.parent()
        if not parent:
            return

        parent.freezeActive = False

        # Start punishment cooldown so no popup immediately after punishment
        parent.punishmentCooldown = True
        QTimer.singleShot(3000, lambda: setattr(parent, "punishmentCooldown", False))

        # Restart popup timer ONLY after cooldown + only if popup mode still running
        if parent.popupsRunning:
            parent.timer.start(parent.freqSlider.value() * 1000)



    def generateQuest(self, subject):
        #open db
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        #run a select query to get all the questions in this subject
        c.execute("SELECT question, correctAns, wrongAns FROM questions WHERE subject=?", (subject,))
        #fetchall will return the list of the question, correct ans and wrong ansrs
        rows = c.fetchall()

        #close that connection
        conn.close()

        #if there are no questions aka rows is empty then give a error message
        if not rows:
            return ("No questions availbale.", ["OK"])

        q = random.choice(rows)
        question = q[0]
        correct = q[1]
        #remmeber wrong ansrs seperated by comma
        wrongs = [w.strip() for w in q[2].split(",") if w.strip()]  # remove spaces + blanks
        options = [correct.strip()] + wrongs
        random.shuffle(options)
        return (question, options, correct.strip())



class JumpScareOverlay(QWidget):
    closed = pyqtSignal()

    def __init__(self, correctAnswer, duration=2000, image_path="jumpscare.png", parent=None):
        super().__init__(parent)

        # prevent double punish triggers
        self._manual_exit = False

        # jumpscare sound
        self.sound = QSoundEffect(self)
        self.sound.setSource(QUrl.fromLocalFile("jumpscare.wav"))
        self.sound.setVolume(1.0)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._duration = duration
        self._phase = 0
        self._scary_font = QFont("Arial", 160, QFont.Bold)

        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)

        # Correct Answer label
        self.correctLabel = QLabel(f"Correct Answer: {correctAnswer}", self)
        self.correctLabel.setAlignment(Qt.AlignCenter)
        self.correctLabel.setStyleSheet("""
            color: white;
            font-size: 32px;
            font-weight: bold;
            background-color: rgba(0, 0, 0, 180);
            padding: 12px 20px;
            border-radius: 12px;
        """)
        self.correctLabel.setGeometry(0, int(self.height() * 0.75), self.width(), 50)

        # Emergency Exit button (top-right)
        self.exitButton = QPushButton("Emergency Exit", self)
        self.exitButton.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                border: none;
                padding: 8px 14px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: darkred;
            }
        """)
        self.exitButton.adjustSize()
        self.exitButton.move(self.width() - self.exitButton.width() - 20, 20)

        # NEW — route click to emergency_close()
        self.exitButton.clicked.connect(self.emergency_close)

        # Try to load jumpscare image
        self.image = QPixmap(image_path) if os.path.exists(image_path) else None

        # AUTO CLOSE TIMER
        self._close_timer = QTimer(self)
        self._close_timer.setSingleShot(True)
        self._close_timer.timeout.connect(self.close)
        self._close_timer.start(self._duration)

    # ---- FIX: safe emergency close ----
    def emergency_close(self):
        self._manual_exit = True
        self._close_timer.stop()
        self.close()

    def resizeEvent(self, event):
        self.correctLabel.setGeometry(0, int(self.height() * 0.75), self.width(), 50)
        self.exitButton.move(self.width() - self.exitButton.width() - 20, 20)
        super().resizeEvent(event)

    def showEvent(self, event):
        self._phase = 0
        QTimer.singleShot(150, self._start_scary_phase)
        super().showEvent(event)

    def _start_scary_phase(self):
        self._phase = 1
        self.sound.stop()
        self.sound.setVolume(1.0)
        self.sound.play()
        self.update()


    # ---- FIX: closed signal emitted ONLY when it's NOT an emergency exit ----
    def closeEvent(self, event):
        self.sound.stop()
        if not self._manual_exit:
            self.closed.emit()
        super().closeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # white flash (phase 0)
        if self._phase == 0:
            painter.fillRect(self.rect(), QColor(255, 255, 255))
            return

        # ---- FULLSCREEN IMAGE ----
        if self.image:
            scaled = self.image.scaled(
                self.width(), self.height(),
                Qt.IgnoreAspectRatio,          # <— force full coverage
                Qt.SmoothTransformation
            )
            painter.drawPixmap(0, 0, scaled)
        else:
            painter.fillRect(self.rect(), Qt.black)

        



class FreezeOverlay(QWidget):

    closed = pyqtSignal()

    def __init__(self, correctAnswer, duration=3000):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Get screen geometry
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)

        # Create overlay background
        self.setStyleSheet("background-color: rgba(0, 0, 255, 150);")  # Blue with transparency

        # Add label text
        self.label = QLabel("FREEZE", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white;")
        self.label.setFont(QFont("Arial", 100, QFont.Bold))
        self.label.setGeometry(self.rect())

        self.correctLabel = QLabel(f"Correct Answer: {correctAnswer}", self)
        self.correctLabel.setAlignment(Qt.AlignCenter)
        self.correctLabel.setFont(QFont("Arial", 32, QFont.Bold))
        self.correctLabel.setStyleSheet("color: white;")
        self.correctLabel.setGeometry(0, int(self.height() * 0.76), self.width(), 60)



        # Safe Exit Button (top-right corner)
        self.exitButton = QPushButton("Emergency Exit", self)
        self.exitButton.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                border: none;
                padding: 8px 12px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: darkred;
            }
        """)
        self.exitButton.adjustSize()
        self.exitButton.move(self.width() - self.exitButton.width() - 20, 20)
        self.exitButton.clicked.connect(self.close)

        # Auto-close after duration
        QTimer.singleShot(duration, self.close)

    def resizeEvent(self, event):
        """Ensure the exit button stays top-right when screen resizes"""
        self.exitButton.move(self.width() - self.exitButton.width() - 20, 20)
        super().resizeEvent(event)
        if hasattr(self, "correctLabel"):
            self.correctLabel.setGeometry(0, int(self.height() * 0.70), self.width(), 60)
        super().resizeEvent(event)

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)
