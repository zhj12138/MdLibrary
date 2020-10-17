import os
import time
import heapq

from PyQt5.QtCore import Qt, QStringListModel
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QSplitter, QFileDialog, QLabel, QMessageBox

from mydialogs import EditTagDialog
from mythreads import ExportThread, backUpThread
from note import createANewNote, Note, createAEmptyNote
from mydatabase import MyDb
from mywidgets import MyToolBar, TagView, DetailView, NoteView, MySearch
from basic import parseStrSetString, strSetToString, copyFile, getName, exportInfo, backUpFile


class MdLibrary(QMainWindow):
    def __init__(self):
        super(MdLibrary, self).__init__()
        self.mainExePath = os.getcwd()
        self.db = MyDb("info.db")

        self.toolbar = MyToolBar()
        self.addToolBar(self.toolbar)
        self.generateToolBar()
        self.searchBar = MySearch(self.db)
        self.addToolBar(Qt.BottomToolBarArea, self.searchBar)
        self.searchBar.updateBookViewSignal.connect(self.updateNoteView)

        self.tagView = TagView(self.db)
        self.generateTagView()
        self.noteView = NoteView(self.db)
        self.generateNoteView()
        self.detailNote = None
        self.curNotes = None
        self.detailView = DetailView()
        self.detailView.openFileSignal.connect(self.openNote)
        self.detailView.openPDFSignal.connect(self.openPDF)

        self.splitter1 = QSplitter()
        self.splitter1.addWidget(self.noteView)
        self.splitter1.addWidget(self.detailView)
        self.splitter1.setSizes([400, 370])
        self.splitter2 = QSplitter()
        self.splitter2.addWidget(self.tagView)
        self.splitter2.addWidget(self.splitter1)
        self.splitter2.setSizes([200, 800])

        self.setCentralWidget(self.splitter2)

        self.numLabel = QLabel()
        self.statusBar().addPermanentWidget(self.numLabel)

        self.updateData()
        self.showAll()
        self.tagView.updateView()

        self.setWindowTitle("MD Library")
        self.setWindowIcon(QIcon('img/notebook.png'))
        self.setGeometry(300, 100, 1300, 800)
        self.show()

    def generateTagView(self):
        self.tagView.itemClick.connect(self.tagClicked)
        self.tagView.tagDeleted.connect(self.ontagDelete)
        self.tagView.tagRenamed.connect(self.renameTag)

    def renameTag(self, oldName, newName):
        notes = self.db.getAllNotes()
        for note in notes:
            if oldName in note.tags:
                note.renameTag(self.db, oldName, newName)
        if self.detailNote and (oldName in self.detailNote.tags):
            self.detailNote.tags.remove(oldName)
            self.detailNote.tags.add(newName)
            self.detailView.updateView(self.detailNote)
        self.tagView.updateView()

    def generateNoteView(self):
        self.noteView.itemClick.connect(self.onNoteItemClicked)
        self.noteView.itemDoubleClick.connect(self.openNote)
        self.noteView.rename.triggered.connect(self.rename)
        self.noteView.delete.triggered.connect(self.deleteMD)
        self.noteView.remove.triggered.connect(self.removeNote)
        self.noteView.copy.triggered.connect(self.copyFile)
        self.noteView.linkPDFSignal.connect(self.onContextPDF)
        self.noteView.addTagSignal.connect(self.onContextAdd)
        self.noteView.deleteTagSignal.connect(self.onContextDelete)

    def onContextPDF(self, pdf_path):
        self.detailNote.linkToPDF(self.db, pdf_path)
        self.detailView.updateView(self.detailNote)

    def onContextAdd(self, tag):
        self.detailNote.addTag(self.db, tag)
        self.detailView.updateView(self.detailNote)

    def onContextDelete(self, tag):
        self.detailNote.deleteTag(self.db, tag)
        self.detailView.updateView(self.detailNote)
        self.tagView.updateView()

    def showAll(self):
        self.curNotes = self.db.getAllNotes()
        self.Sort()
        names = [note.name for note in self.curNotes]
        self.updateNoteView(names)
        note = Note()
        self.detailView.updateView(note)

    def generateToolBar(self):
        self.toolbar.createNote.triggered.connect(self.createMD)
        self.toolbar.addNoteBtn.clicked.connect(self.inMD)
        self.toolbar.addNotes.triggered.connect(self.inMD)
        self.toolbar.addNotesByPath.triggered.connect(self.inMDbyPath)
        self.toolbar.editName.triggered.connect(self.rename)
        self.toolbar.linkToPDF.triggered.connect(self.linkToPDF)
        self.toolbar.editTags.triggered.connect(self.editTags)
        self.toolbar.openNote.triggered.connect(self.openNote)
        self.toolbar.openPDF.triggered.connect(self.openPDF)
        self.toolbar.openAll.triggered.connect(self.openAll)
        self.toolbar.deleteNote.triggered.connect(self.deleteMD)
        self.toolbar.backUp.triggered.connect(self.backUp)
        self.toolbar.export.triggered.connect(self.export)
        self.toolbar.sortModeChangedSignal.connect(self.sortCur)
        self.toolbar.refresh.triggered.connect(self.refresh)
        self.toolbar.copy.triggered.connect(self.copyFile)
        self.toolbar.removeNote.triggered.connect(self.removeNote)

    def tagClicked(self, tag):
        notes = self.db.getAllNotes()
        if tag == '所有笔记':
            pass
        elif tag == '最近笔记':
            notes = heapq.nlargest(10, notes, key=lambda note: note.visit_time)
        else:
            notes = [note for note in notes if tag in note.tags]
        self.curNotes = notes
        self.Sort()
        self.updateCurShow()
        note = Note()
        self.detailView.updateView(note)
        self.detailNote = None

    def removeNote(self):
        if not self.detailNote:
            return
        box = QMessageBox(QMessageBox.Warning, "警告", "您确定要从磁盘上中删除此文件吗？")
        yes = box.addButton("确定", QMessageBox.YesRole)
        no = box.addButton("取消", QMessageBox.NoRole)
        # box.setIcon(2)
        box.exec_()
        if box.clickedButton() == no:
            return
        elif box.clickedButton() == yes:
            if os.path.exists(self.detailNote.file_path):
                os.remove(self.detailNote.file_path)
            self.db.deleteNote(self.detailNote.name)
            for note in self.curNotes:
                if note.name == self.detailNote.name:
                    self.curNotes.remove(note)
                    break
            note = Note()
            self.detailView.updateView(note)
            self.detailNote = None
            self.updateCurShow()

    def copyFile(self):
        if self.detailNote:
            copyFile(self.detailNote.file_path)

    def sortCur(self):
        self.Sort()
        names = [note.name for note in self.curNotes]
        self.updateNoteView(names)
        note = Note()
        self.detailView.updateView(note)

    def updateData(self):
        notes = self.db.getAllNotes()
        for note in notes:
            note.updateInfo(self.db)

    def refresh(self):
        self.updateData()
        self.showAll()

    def Sort(self):
        rev = self.toolbar.sortReverse
        mode = self.toolbar.sortMode
        if mode == 'mod_date':
            self.curNotes.sort(key=lambda note: note.mod_time, reverse=rev)
        elif mode == 'vis_date':
            self.curNotes.sort(key=lambda note: note.visit_time, reverse=rev)
        elif mode == 'cre_date':
            self.curNotes.sort(key=lambda note: note.create_time, reverse=rev)
        else:
            self.curNotes.sort(key=lambda note: note.name, reverse=rev)

    def onNoteItemClicked(self, text):
        note = self.db.getNoteByName(text)
        self.detailNote = note
        self.detailView.updateView(self.detailNote)

    def ontagDelete(self):
        self.tagView.updateView()
        if self.detailNote:
            self.detailView.updateView(self.detailNote)

    def updateNoteView(self, notenames):
        num = len(notenames)
        self.noteView.updateView(notenames)
        self.numLabel.setText("共有{}个文件".format(num))

    def createMD(self):
        filedir = self.db.getDir()
        if not os.path.exists(filedir):
            filedir = "."
        file_path, _ = QFileDialog.getSaveFileName(self, "选择路径", filedir, "markdown file(*.md)")
        if file_path:
            base_dir = os.path.dirname(file_path)
            self.db.changeDir(base_dir)
            createAEmptyNote(self.db, file_path)
            self.showAll()

    def inMD(self):
        filedir = self.db.getDir()
        if not os.path.exists(filedir):
            filedir = "."
        md_files, _ = QFileDialog.getOpenFileNames(self, "选择文件", filedir, "markdown file(*.md)")
        if md_files:
            base_dir = os.path.dirname(md_files[0])
            self.db.changeDir(base_dir)
            for md_file in md_files:
                createANewNote(self.db, md_file)
            self.showAll()

    def inMDbyPath(self):
        filedir = self.db.getDir()
        if not os.path.exists(filedir):
            filedir = "."
        file_path = QFileDialog.getExistingDirectory(self, "选择目录", filedir)
        if file_path:
            self.db.changeDir(file_path)
            md_files = [os.path.abspath(os.path.join(file_path, file)) for file in os.listdir(file_path) if file.endswith('.md')]
            for md_file in md_files:
                createANewNote(self.db, md_file)
            self.showAll()

    def rename(self):
        if self.detailNote:
            newName = getName(self.detailNote.name, self.db.getAllNoteNames())
            if newName:
                curNoteDir = os.path.dirname(self.detailNote.file_path)
                newFilePath = os.path.abspath(os.path.join(curNoteDir, newName + '.md'))
                try:
                    os.rename(self.detailNote.file_path, newFilePath)
                except:
                    QMessageBox.about(self, "抱歉", "文件目录已存在同名文件，重命名失败")
                    return
                for note in self.curNotes:
                    if note.name == self.detailNote.name:
                        note.name = newName
                self.db.deleteNote(self.detailNote.name)
                self.detailNote.name = newName
                self.detailNote.file_path = newFilePath
                self.db.addNote(self.detailNote)
                self.updateCurShow()
                self.detailView.updateView(self.detailNote)

    def updateCurShow(self):
        names = [note.name for note in self.curNotes]
        self.updateNoteView(names)

    def linkToPDF(self):
        if not self.detailNote:
            return
        filedir = self.db.getDir()
        if not os.path.exists(filedir):
            filedir = "."
        filename, _ = QFileDialog.getOpenFileName(self, "选择文件", filedir, "PDF file(*.pdf)")
        if filename:
            base_dir = os.path.dirname(filename)
            self.db.changeDir(base_dir)
            self.detailNote.linkToPDF(self.db, filename)
            self.detailView.updateView(self.detailNote)

    def editTags(self):
        if not self.detailNote:
            return
        # tagStr, ok = QInputDialog.getText(self, "编辑标签", "请输入标签", text=strSetToString(self.detailNote.tags))
        # if ok:
        #     self.detailNote.setTags(self.db, parseStrSetString(tagStr))
        #     self.detailView.updateView(self.detailNote)
        #     self.tagView.updateView()
        dig = EditTagDialog(self)
        dig.inputLine.setText(strSetToString(self.detailNote.tags))
        tags = self.db.getAllTags()
        model = QStringListModel()
        model.setStringList(tags)
        dig.completer.setModel(model)
        dig.modifySignal.connect(self.tagModify)
        dig.show()

    def tagModify(self, tagStr):
        tags = parseStrSetString(tagStr)
        self.detailNote.setTags(self.db, tags)
        self.detailView.updateView(self.detailNote)
        self.tagView.updateView()

    def openNote(self):
        if self.detailNote:
            try:
                os.startfile(self.detailNote.file_path)
                self.detailNote.updateVisitTime(self.db)
                for note in self.curNotes:
                    if note.name == self.detailNote.name:
                        note.visit_time = self.detailNote.visit_time
                self.detailView.updateView(self.detailNote)
            except:
                QMessageBox.about(self, "提醒", "文件不存在")
                self.db.deleteNote(self.detailNote.name)
                names = self.db.getAllNoteNames()
                self.updateNoteView(names)
                temp = Note()
                self.detailView.updateView(temp)

    def openPDF(self):
        if self.detailNote:
            if self.detailNote.pdf_path:
                try:
                    os.startfile(self.detailNote.pdf_path)
                except:
                    QMessageBox.about(self, "提醒", '未找到PDF文件')
                    self.detailNote.deletePDF(self.db)
                    self.detailView.updateView(self.detailNote)

    def openAll(self):
        self.openNote()
        self.openPDF()

    def deleteMD(self):
        if not self.detailNote:
            return
        box = QMessageBox(QMessageBox.Question, "注意", "您确定要从库中移除此文件吗？")
        yes = box.addButton("确定", QMessageBox.YesRole)
        no = box.addButton("取消", QMessageBox.NoRole)
        # box.setIcon(1)
        box.exec_()
        if box.clickedButton() == no:
            return
        elif box.clickedButton() == yes:
            self.db.deleteNote(self.detailNote.name)
            for note in self.curNotes:
                if note.name == self.detailNote.name:
                    self.curNotes.remove(note)
                    break
            note = Note()
            self.detailView.updateView(note)
            self.detailNote = None
            self.updateCurShow()

    def export(self):
        filedir = self.db.getDir()
        if not os.path.exists(filedir):
            filedir = "."
        filename, _ = QFileDialog.getSaveFileName(self, "导出信息", filedir, "CSV file(*.csv)")
        if not filename:
            return
        base_dir = os.path.dirname(filename)
        self.db.changeDir(base_dir)
        headers = ['名称', '文件路径', 'PDF路径', '标签', '创建时间', '访问时间', '修改时间', 'md5码']
        rows = [(note.name, note.file_path, note.pdf_path, strSetToString(note.tags), note.create_time, note.visit_time,
                 note.mod_time, note.md5code) for note in self.curNotes]
        t = ExportThread(exportInfo, (filename, headers, rows))
        t.finishSignal.connect(lambda: self.finishExport(filename))
        t.start()
        time.sleep(1)

    def finishExport(self, filename):
        if os.path.exists(filename):
            box = QMessageBox(QMessageBox.Question, "提醒", "导出完成，是否打开文件")
            yes = box.addButton("确定", QMessageBox.YesRole)
            no = box.addButton("取消", QMessageBox.NoRole)
            # box.setIcon(1)
            box.exec_()
            if box.clickedButton() == no:
                return
            elif box.clickedButton() == yes:
                os.startfile(filename)
        else:
            QMessageBox.warning(self, "抱歉", "导出失败")

    def backUp(self):
        filedir = self.db.getDir()
        if not os.path.exists(filedir):
            filedir = "."
        dirname = QFileDialog.getExistingDirectory(self, "选择目录", filedir)
        if not dirname:
            return
        self.db.changeDir(dirname)
        filepaths = [note.file_path for note in self.curNotes]
        t = backUpThread(backUpFile, (dirname, filepaths))
        t.finishSignal.connect(self.finishBackUp)
        t.start()
        time.sleep(1)

    def finishBackUp(self, ret):
        suc, fail = ret
        QMessageBox.about(self, "提醒", "{}个文件备份成功, {}个文件备份失败".format(suc, fail))



