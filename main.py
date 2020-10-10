import sys
from PyQt5.QtWidgets import QApplication
from ui import MdLibrary


app = QApplication(sys.argv)
mdLib = MdLibrary()
sys.exit(app.exec_())
