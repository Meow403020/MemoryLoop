

#make the class inehirt from qwidget which is base class for buttons labels etc
#not qdialog because its more suitable for always staying there rather than pop ups and confirmation messages
class Dashboard(QWidget):
    #constructor for vcreating objects
    #calls parent class qwidget for basic functionality
    def __init__(self):
        super().__init__()

        self.resizing = False
        self.moving = False
        self.offset = None

        #title at top of app
        self.setWindowTitle("Study Popup Dashboard")
        #xy position for first two nums and width height for secnd nums
        self.setGeometry(300,200,500,450)

        # Remove system title bar (no white strip)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # === MAIN ROOT LAYOUT ===
        mainLayout = QVBoxLayout(self)  # root layout
        mainLayout.setContentsMargins(0, 0, 0, 0)

        # === Custom Title Bar ===
        titleBar = QWidget()
        titleBar.setFixedHeight(40)
        titleBar.setStyleSheet("background-color: #1E3A8A;")  # dark blue

        titleLayout = QHBoxLayout(titleBar)
        titleLayout.setContentsMargins(10, 0, 10, 0)

        title = QLabel("📘 POPSHOCK: Study Dashboard")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: white;
            }
        """)
        titleLayout.addWidget(title)

        titleLayout.addStretch()

        # Minimize button

        # Minimize button
        minBtn = TitleBarButton("–", "#61c1c7", "#3c9499")
        minBtn.setToolTip("Minimize")
        minBtn.clicked.connect(self.showMinimized)

        # Close button
        closeBtn = TitleBarButton("X", "#EF4444", "#DC2626")
        closeBtn.setToolTip("Close")
        closeBtn.clicked.connect(self.close)



        titleLayout.addWidget(minBtn)
        titleLayout.addWidget(closeBtn)

        # Add title bar to root layout
        mainLayout.addWidget(titleBar)

        # === DASHBOARD CONTENT (all your widgets go here) ===
        content = QWidget()
        layout = QVBoxLayout(content)  # vertical layout for dashboard widgets

        # --- Category Selection Row ---
        layout.addWidget(QLabel("Select Subject:"))

        categRow = QHBoxLayout()

        self.categBox = QComboBox()
        self.loadCategories()


        categRow.addWidget(self.categBox)

        layout.addLayout(categRow)

        layout.addWidget(QLabel("Mode:"))

        # --- Mode Toggle Switch + Side Labels ---
        modeLayout = QHBoxLayout()

        self.studyLabel = QLabel("Study Mode")
        self.gamingLabel = QLabel("Gaming Mode")

        self.modeToggle = ToggleSwitch()

        modeLayout.addWidget(self.studyLabel)
        modeLayout.addWidget(self.modeToggle)
        modeLayout.addWidget(self.gamingLabel)

        modeLayout = QHBoxLayout()

        modeLayout.addStretch()                  # push everything to the center
        modeLayout.addWidget(self.studyLabel)
        modeLayout.addSpacing(10)
        modeLayout.addWidget(self.modeToggle)
        modeLayout.addSpacing(10)
        modeLayout.addWidget(self.gamingLabel)
        modeLayout.addStretch()

        layout.addLayout(modeLayout)

        # initial mode
        self.mode = "Study Mode"

        # highlight/unhighlight labels based on current mode
        def updateModeVisuals():
            if self.modeToggle.checked:  # Gaming Mode
                self.studyLabel.setStyleSheet("color: #BFBFBF;")   # dim
                self.gamingLabel.setStyleSheet("color: #FFFFFF; font-weight: bold;")  # bright
            else:  # Study Mode
                self.studyLabel.setStyleSheet("color: #FFFFFF; font-weight: bold;")  # bright
                self.gamingLabel.setStyleSheet("color: #BFBFBF;")  # dim

        def handleToggle(state):
            self.mode = "Gaming Mode" if state else "Study Mode"
            updateModeVisuals()

        self.modeToggle.toggled.connect(handleToggle)

        # call once so labels are styled at startup
        updateModeVisuals()

        self.currentSubject = None
        self.currentMode = None


        # Slider to select popup frequency
        self.freqSlider = QSlider(Qt.Horizontal)
        self.freqSlider.setRange(10, 300)   # 10 seconds to 5 minutes
        self.freqSlider.setValue(30)        # default 30 seconds
        self.freqSlider.setTickInterval(10)
        self.freqSlider.setTickPosition(QSlider.TicksBelow)

        # Label to show current slider value
        self.freqLabel = QLabel("Popup Frequency: 30 seconds")
        self.freqSlider.valueChanged.connect(self.updateFreqLabel)

        layout.addWidget(self.freqLabel)
        layout.addWidget(self.freqSlider)

        # --- Start / Stop Popup Button ---
        
        self.popBtn = QPushButton("Start Popups")
        self.popBtn.setStyleSheet("""
            QPushButton {
                background-color: #6879e8;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4f5cc9;    /* darker shade of the same blue */
            }
        """)

        self.popBtn.clicked.connect(self.togglePopups)
        layout.addWidget(self.popBtn)

        self.popupsRunning = False   # Track running/not running
        self.punishmentCooldown = False
        self.punishmentRunning = False


        #same here but for adding extra questions
        addQst = QPushButton("Add Question")
        addQst.clicked.connect(self.questAdd)
        layout.addWidget(addQst)

        # Button to view/manage questions
        manageQst = QPushButton("Manage Questions")
        manageQst.clicked.connect(self.manageQuestions)
        layout.addWidget(manageQst)

        # Add content section to main layout (under title bar)
        mainLayout.addWidget(content)

        #custom method for css
        self.applyStyle()

        self.timer = QTimer()
        self.timer.timeout.connect(self.showPopup)

        self.freezeActive = False  # Track if freeze overlay is on

        self.dragging = False
        self.offset = None

        self.setFont(QFont("Arial Rounded MT Bold", 11))

    def resizeEvent(self, event):
        # Scale text size based on width of dashboard
        w = self.width()
        
        # Pick a base size to scale from
        base_size = 12   # minimum font size
        scale = max(base_size, int(w / 42))   # divide window width to tune sensitivity

        self.applyDynamicFont(scale)
        super().resizeEvent(event)

    def loadCategories(self):
        self.categBox.clear()
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT name FROM categories")
        categories = c.fetchall()
        conn.close()

        for (name,) in categories:
            self.categBox.addItem(name)

    def togglePopups(self):
        if not self.popupsRunning:
            # Set current subject/mode from UI immediately
            self.currentSubject = self.categBox.currentText()
            self.currentMode = self.mode


            # START POPUPS
            interval = self.freqSlider.value() * 1000
            # start the timer but it will be stopped when the first popup shows
            self.timer.start(interval)
            self.showPopup()
            self.popupsRunning = True

            self.popBtn.setText("Stop Popups")
            self.popBtn.setStyleSheet("""
                QPushButton {
                    background-color: red;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #b30000;
                }
            """)
        else:
            # STOP POPUPS
            self.timer.stop()
            self.popupsRunning = False

            if hasattr(self, "popup") and self.popup.isVisible():
                self.popup.close()

            self.popBtn.setText("Start Popups")
            self.popBtn.setStyleSheet("""
                QPushButton {
                    background-color: #6879e8;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #4f5cc9;
                }
            """)



                


    def addCategory(self):
        text, ok = QInputDialog.getText(self, "Add Category", "Enter new category name:")
        if not ok or not text.strip():
            return   # user cancelled or empty
        
        name = text.strip()

        # Prevent duplicates in UI
        if self.categBox.findText(name) != -1:
            QMessageBox.warning(self, "Exists", "This category already exists.")
            return

        # Insert into database
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            conn.commit()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Database Error", "This category already exists in the database.")
            conn.close()
            return
        conn.close()

        # Add to dropdown and select it
        self.categBox.addItem(name)
        self.categBox.setCurrentText(name)


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()   # store where the mouse clicked
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging:
            # move window relative to where it was clicked
            self.move(self.pos() + event.pos() - self.offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False

    RESIZE_MARGIN = 8

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.resizing = False
            self.offset = event.pos()

            rect = self.rect()
            x, y = event.pos().x(), event.pos().y()

            # Flags for which edges are being resized
            self.resizeLeft = (x <= self.RESIZE_MARGIN)
            self.resizeRight = (x >= rect.width() - self.RESIZE_MARGIN)
            self.resizeTop = (y <= self.RESIZE_MARGIN)
            self.resizeBottom = (y >= rect.height() - self.RESIZE_MARGIN)

            if self.resizeLeft or self.resizeRight or self.resizeTop or self.resizeBottom:
                self.resizing = True
            else:
                self.dragging = True
            event.accept()

    def mouseMoveEvent(self, event):
        if self.resizing:
            rect = self.geometry()
            dx = event.globalX() - self.mapToGlobal(self.offset).x()
            dy = event.globalY() - self.mapToGlobal(self.offset).y()

            if self.resizeLeft:
                new_x = rect.x() + dx
                new_w = rect.width() - dx
                if new_w >= 300:
                    rect.setX(new_x)
                    rect.setWidth(new_w)

            elif self.resizeRight:
                new_w = rect.width() + dx
                if new_w >= 300:
                    rect.setWidth(new_w)

            if self.resizeTop:
                new_y = rect.y() + dy
                new_h = rect.height() - dy
                if new_h >= 250:
                    rect.setY(new_y)
                    rect.setHeight(new_h)

            elif self.resizeBottom:
                new_h = rect.height() + dy
                if new_h >= 250:
                    rect.setHeight(new_h)

            self.setGeometry(rect)
            self.offset = event.pos()  # reset offset for smooth resizing
            event.accept()

        elif self.dragging:
            self.move(self.pos() + event.pos() - self.offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing = False



    def manageQuestions(self):
        self.timer.stop()
        dialog = ManageQuestions()
        dialog.exec_()
        self.loadCategories()

        # only resume timer if popups were already running
        if self.popupsRunning:
            self.timer.start(self.freqSlider.value() * 1000)


    def viewQuestions(self):
        self.timer.stop()  # Pause popups while managing
        manager = QuestionManager()
        manager.exec_()
        self.timer.start(self.freqSlider.value() * 1000)  # Resume popups

    def updateFreqLabel(self, value):
        if (value % 60) == 0:
            value = value // 60
            self.freqLabel.setText(f"Popup Frequency: {value} minutes")
        elif value % 60 == value:
            self.freqLabel.setText(f"Popup Frequency: {value} seconds")
        else:
            secns = value % 60
            minss = math.floor(value // 60)
            self.freqLabel.setText(f"Popup Frequency: {minss} minutes and {secns} seconds")

    def applyStyle(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #5e5ed1;
                font-family: 'Arial Rounded MT Bold', 'Segoe UI', sans-serif;
                font-size: 14px;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #65a8b8;
                color: white;
                padding: 10px;
                margin: 5px;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                font-family: 'Arial Rounded MT Bold', 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background-color: #356773;
            }
            QLabel {
                font-size: 15px;
                font-weight: bold;
                font-family: 'Arial Rounded MT Bold', 'Segoe UI', sans-serif;
            }
        """)

    def applyDynamicFont(self, size):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #4b4b94;
                font-family: 'Arial Rounded MT Bold', 'Segoe UI', sans-serif;
                font-size: {size}px;
                color: #FFFFFF;
            }}
            QPushButton {{
                background-color: #65a8b8;
                color: white;
                padding: 10px;
                margin: 5px;
                border-radius: 8px;
                font-size: {size + 2}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #334487;
            }}
            QLabel {{
                font-size: {size + 2}px;
                font-weight: bold;
            }}
        """)


    #creates and displays the popups
    def showPopup(self):
        if getattr(self, "freezeActive", False):
            return

        if getattr(self, "punishmentCooldown", False):
            return

        # Block popups during punishment
        if getattr(self, "freezeActive", False):
            return

        # Pull live subject/mode from UI if not set
        subject = self.currentSubject or self.categBox.currentText()
        mode = self.currentMode or self.mode

        # Defensive: if still nothing, skip
        if not subject or not mode:
            return

        # Make sure timer won't trigger another popup while this one is active
        self.timer.stop()

        self.popup = QuestionPopup(
            subject=subject,
            mode=mode,
            parent=self
        )

        # ensure popupClosed will be called when popup finishes
        self.popup.finished.connect(self.popupClosed)
        self.popup.show()


    def popupClosed(self):
        # Only restart timer if popups are meant to be running and no punishment active
        if self.popupsRunning and not getattr(self, "freezeActive", False):
            self.timer.start(self.freqSlider.value() * 1000)


    def questAdd(self):
        #stop the popups while were adding a question
        self.timer.stop()
        #function created before so user can input question
        question = AddQuestion()
        #runs it in modal mode, must complete this beforfe returning to dashboard
        question.exec_()
        self.timer.start(self.freqSlider.value()* 1000)
