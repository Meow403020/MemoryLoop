import sys
import os

if __name__ == "__main__":
    createdb() 
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())

