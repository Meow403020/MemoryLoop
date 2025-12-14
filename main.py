import sys
import os
from database import createdb
from addQuestion import AddQuestion
from manageQuestions import ManageQuestions
from uiWidgets import ToggleSwitch, TitleBarButton

if __name__ == "__main__":
    createdb() 
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())

