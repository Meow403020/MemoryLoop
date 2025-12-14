from PyQt5.QtCore import QObject, pyqtSlot


class QuestionBridge(QObject):
    def __init__(self, popup):
        super().__init__()
        self.popup = popup

    @pyqtSlot(str)
    def checkAnswer(self, selected):
        self.popup.check_answer(selected)
