from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QDialog, QLineEdit, QLabel, QPushButton, QCompleter, QVBoxLayout, QHBoxLayout


class MyCompleter(QCompleter):
    def __init__(self):
        super(MyCompleter, self).__init__()
        self.setCaseSensitivity(Qt.CaseInsensitive)

    def pathFromIndex(self, index):  # 返回值为填充到框中的文本
        path = QCompleter.pathFromIndex(self, index)  # 当前在弹出窗口选择的文本
        print(path)
        lst = str(self.widget().text()).split(',')
        if len(lst) > 1:
            path = '%s, %s' % (', '.join(lst[:-1]), path)
        return path

    def splitPath(self, path):  # （列表模型中), 返回列表中的第一项用于匹配。
        toMatch = path.split(',')[-1].strip()
        return [toMatch]


class EditTagDialog(QDialog):
    modifySignal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(EditTagDialog, self).__init__(parent)
        self.noteLabel = QLabel("请输入标签")
        self.inputLine = QLineEdit()
        self.okBtn = QPushButton("修改")
        self.cancleBtn = QPushButton("取消")
        self.completer = MyCompleter()
        self.inputLine.setCompleter(self.completer)
        self.vBox = QVBoxLayout()
        self.hBox = QHBoxLayout()
        self.hBox.addWidget(self.okBtn)
        self.hBox.addWidget(self.cancleBtn)
        self.vBox.addWidget(self.noteLabel)
        self.vBox.addWidget(self.inputLine)
        self.vBox.addLayout(self.hBox)
        self.setLayout(self.vBox)
        self.setWindowTitle("标签")

        self.okBtn.clicked.connect(self.onOk)
        self.cancleBtn.clicked.connect(self.onCancle)

    def onOk(self):
        self.modifySignal.emit(self.inputLine.text())
        self.close()

    def onCancle(self):
        self.close()


