from PyQt5.QtCore import QThread, pyqtSignal


class ExportThread(QThread):
    finishSignal = pyqtSignal()

    def __init__(self, func, args):
        super(ExportThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.func(*self.args)
        self.finishSignal.emit()


class backUpThread(QThread):
    finishSignal = pyqtSignal(tuple)

    def __init__(self, func, args):
        super(backUpThread, self).__init__()
        self.func = func
        self.args = args
        self.ret = None

    def run(self):
        self.ret = self.func(*self.args)
        self.finishSignal.emit(self.ret)
