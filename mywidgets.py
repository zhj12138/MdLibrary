import os
import re

from PyQt5.QtCore import pyqtSignal, QSize, Qt, QUrl, QStringListModel
from PyQt5.QtGui import QFont, QIcon, QDesktopServices, QCursor
from PyQt5.QtWidgets import QToolBar, QAction, QMenu, QToolButton, QListWidget, QLabel, QFormLayout, \
    QTreeWidget, QTreeWidgetItem, QWidget, QScrollArea, QFrame, QListWidgetItem, QSplitter, QComboBox, QLineEdit, \
    QCompleter, QInputDialog

from basic import strSetToString
from mydatabase import MyDb
from note import Note


class MyToolBar(QToolBar):
    sortModeChangedSignal = pyqtSignal()

    def __init__(self):
        super(MyToolBar, self).__init__()
        # self.setMinimumSize(QSize(50, 50))
        self.setIconSize(QSize(50, 50))
        self.setFont(QFont("", 13))
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.url = 'https://github.com/zhj12138/ebook-manager'

        self.createNote = QAction(QIcon('img/add-7.png'), "新建", self)

        self.addNoteMenu = QMenu()
        self.addNoteMenu.setFont(QFont("", 13))
        self.addNotes = QAction("导入文件", self)
        self.addNotesByPath = QAction("导入目录下所有文件", self)
        self.addNoteMenu.addActions([self.addNotes, self.addNotesByPath])
        self.addNoteBtn = QToolButton()
        self.addNoteBtn.setText("导入")
        self.addNoteBtn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addNoteBtn.setIcon(QIcon('img/add-2.png'))
        self.addNoteBtn.setMenu(self.addNoteMenu)
        self.addNoteBtn.setPopupMode(QToolButton.MenuButtonPopup)

        self.editName = QAction(QIcon('img/edit-5.png'), "重命名", self)
        self.linkToPDF = QAction(QIcon('img/pdf.png'), "链接", self)
        self.editTags = QAction(QIcon('img/tag-1.png'), "标签", self)

        self.sortMode = "mod_date"
        self.sortReverse = True
        self.sortByName = QAction("按书名排序", self)
        # self.sortBySize = QAction("按文件大小排序", self)
        self.sortByModDate = QAction("按修改时间排序", self)
        self.sortByVisDate = QAction("按访问时间排序", self)
        self.sortByCreDate = QAction("按创建时间排序", self)
        self.sortByName.triggered.connect(lambda: self.changeSortMode("name"))
        self.sortByCreDate.triggered.connect(lambda: self.changeSortMode("cre_date"))
        self.sortByVisDate.triggered.connect(lambda: self.changeSortMode("vis_date"))
        # self.sortBySize.triggered.connect(lambda: self.changeSortMode("size"))
        self.sortByModDate.triggered.connect(lambda: self.changeSortMode("mod_date"))
        self.sortMenu = QMenu()
        self.sortMenu.setFont(QFont("", 13))
        self.sortMenu.addActions([self.sortByName, self.sortByVisDate, self.sortByModDate, self.sortByCreDate])
        self.sortBtn = QToolButton()
        self.sortBtn.setText("排序")
        self.sortBtn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.sortBtn.setIcon(QIcon('img/sortUp-2.png'))
        self.sortBtn.setMenu(self.sortMenu)
        self.sortBtn.setPopupMode(QToolButton.MenuButtonPopup)
        self.sortBtn.clicked.connect(self.changeReverse)

        self.openNote = QAction(QIcon('img/read-2.png'), "书写", self)
        self.openPDF = QAction(QIcon('img/PDF-1.png'), "阅读", self)
        self.openAll = QAction(QIcon('img/study-1.png'), "学习", self)

        self.deleteNote = QAction(QIcon('img/delete-4.png'), "移除", self)
        self.backUp = QAction(QIcon('img/bookshelf.png'), "备份", self)
        self.export = QAction(QIcon('img/export-1.png'), "导出", self)
        self.star = QAction(QIcon('img/star-1.png'), "支持", self)
        self.star.triggered.connect(self.toStar)

        self.copy = QAction(QIcon('img/copy-1.png'), "复制", self)
        self.refresh = QAction(QIcon('img/refresh-1.png'), "刷新", self)
        self.removeNote = QAction(QIcon('img/delete-1.png'), "删除", self)

        self.addActions([self.createNote])
        self.addWidget(self.addNoteBtn)
        self.addSeparator()
        self.addActions([self.editName, self.linkToPDF, self.editTags])
        self.addWidget(self.sortBtn)
        self.addSeparator()
        self.addActions([self.openNote, self.openPDF, self.openAll, self.copy, self.refresh])
        self.addSeparator()
        self.addActions([self.backUp])
        self.addActions([self.export])
        self.addSeparator()
        self.addActions([self.star])
        self.addSeparator()
        self.addActions([self.deleteNote, self.removeNote])

    def changeSortMode(self, attr: str):
        self.sortMode = attr
        self.sortModeChangedSignal.emit()

    def changeReverse(self):
        if self.sortReverse:
            self.sortReverse = False
            self.sortBtn.setIcon(QIcon('img/sortDown.png'))
        else:
            self.sortReverse = True
            self.sortBtn.setIcon(QIcon('img/sortUp-2.png'))
        self.sortModeChangedSignal.emit()

    def toStar(self):
        QDesktopServices.openUrl(QUrl(self.url))


class TagView(QListWidget):
    itemClick = pyqtSignal(str)
    tagDeleted = pyqtSignal()
    tagRenamed = pyqtSignal(str, str)

    def __init__(self, db: MyDb):
        super(TagView, self).__init__()
        self.db = db
        self.setFont(QFont("", 14))
        self.itemClicked.connect(self.onItemClicked)

        self.contextMenu = QMenu()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        # self.noteMenu = self.contextMenu.addMenu("添加笔记")
        # self.noteMenu.triggered.connect(self.noteItemClicked)
        self.deleteTag = QAction("删除当前标签", self)
        self.renameTag = QAction("重命名当前标签", self)
        self.contextMenu.addActions([self.renameTag, self.deleteTag])
        self.deleteTag.triggered.connect(self.onDeleteTag)
        self.renameTag.triggered.connect(self.reNameTag)

    def reNameTag(self):
        if not self.currentItem():
            return
        tag = self.currentItem().text()
        newTagName, ok = QInputDialog.getText(self, "重命名", "请输入新的标签名", text=tag)
        if not ok:
            return
        if tag == newTagName:
            return
        self.tagRenamed.emit(tag, newTagName)

    def onDeleteTag(self):
        if not self.currentItem():
            return
        tag = self.currentItem().text()
        if tag == '所有笔记' or tag == "最近笔记":
            return
        notes = self.db.getAllNotes()
        RNotes = [note for note in notes if tag in note.tags]
        for note in RNotes:
            note.deleteTag(self.db, tag)
        self.tagDeleted.emit()

    def updateView(self):
        self.clear()
        item = QListWidgetItem("所有笔记")
        item.setIcon(QIcon('img/tag-5.png'))
        item2 = QListWidgetItem("最近笔记")
        item2.setIcon(QIcon('img/tag-5.png'))
        self.addItem(item)
        self.addItem(item2)
        tags = self.db.getAllTags()
        for tag in tags:
            item = QListWidgetItem(tag)
            item.setIcon(QIcon('img/tag-5.png'))
            # item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.addItem(item)

    def onItemClicked(self, item):
        tag = item.text()
        self.itemClick.emit(tag)

    # def updateNoteMenu(self):
    #     names = self.db.getAllNoteNames()
    #     for name in names:
    #         action = QAction(name, self)
    #         self.noteMenu.addAction(action)

    # def noteItemClicked(self, action):  # 为书籍添加一个tag
    #     name = action.text()
    #     note = self.db.getNoteByName(name)
    #     tag = self.currentItem().text()
    #     note.addTag(self.db, tag)
    #     # 可能还需要更新笔记显示区的view

    def showContextMenu(self, position):
        item = self.itemAt(position)
        if item and item.text() != "所有笔记" and item.text() != "最近笔记":
            self.contextMenu.exec_(QCursor.pos())


class NoteView(QListWidget):
    itemClick = pyqtSignal(str)
    itemDoubleClick = pyqtSignal()
    addTagSignal = pyqtSignal(str)
    deleteTagSignal = pyqtSignal(str)
    linkPDFSignal = pyqtSignal(str)

    def __init__(self, db):
        super(NoteView, self).__init__()
        self.setFont(QFont("", 14))
        self.db = db
        self.itemClicked.connect(self.onItemClicked)
        self.itemDoubleClicked.connect(self.onItemDoubleClicked)
        self.contextMenu = QMenu()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        self.rename = QAction("重命名", self)
        self.copy = QAction("复制", self)
        self.contextMenu.addActions([self.rename, self.copy])
        self.addToTag = self.contextMenu.addMenu("添加标签")
        self.deleteTag = self.contextMenu.addMenu("删除标签")
        self.link = self.contextMenu.addMenu("链接PDF")
        self.addToTag.triggered.connect(self.onAddTag)
        self.deleteTag.triggered.connect(self.onDeleteTag)
        self.link.triggered.connect(self.onLinkPDF)
        self.delete = QAction("移除", self)
        self.remove = QAction("从磁盘删除", self)
        self.contextMenu.addActions([self.delete, self.remove])

    def onAddTag(self, action):
        self.addTagSignal.emit(action.text())

    def onDeleteTag(self, action):
        self.deleteTagSignal.emit(action.text())

    def onLinkPDF(self, action):
        self.linkPDFSignal.emit(action.text())

    def generateAddTagMenu(self):
        self.addToTag.clear()
        tags = self.db.getAllTags()
        for tag in tags:
            action = QAction(tag, self)
            self.addToTag.addAction(action)

    def generateDelTagMenu(self):
        self.deleteTag.clear()
        name = self.currentItem().text()
        note = self.db.getNoteByName(name)
        for tag in note.tags:
            action = QAction(tag, self)
            self.deleteTag.addAction(action)

    def generateLinkMenu(self):
        self.link.clear()
        pdfs = self.db.getAllPDFs()
        for pdf in pdfs:
            action = QAction(pdf, self)
            self.link.addAction(action)

    def showContextMenu(self, pos):
        item = self.itemAt(pos)
        if not item:
            return
        self.itemClick.emit(item.text())
        self.generateAddTagMenu()
        self.generateDelTagMenu()
        self.generateLinkMenu()
        self.contextMenu.exec_(QCursor.pos())

    def updateView(self, noteNames):
        self.clear()
        for name in noteNames:
            item = QListWidgetItem(name)
            item.setIcon(QIcon('img/markdown-2.png'))
            # item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.addItem(item)

    def onItemClicked(self, item):
        self.itemClick.emit(item.text())

    def onItemDoubleClicked(self, item: QListWidgetItem) -> None:
        self.itemDoubleClick.emit()


class MyLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, ev) -> None:
        self.clicked.emit()
        super(MyLabel, self).mousePressEvent(ev)


class DetailView(QSplitter):
    openFileSignal = pyqtSignal()
    openPDFSignal = pyqtSignal()

    def __init__(self):
        super(DetailView, self).__init__()
        self.setOrientation(Qt.Vertical)
        self.form = QFormLayout()
        self.toc = QTreeWidget()
        self.toc.setColumnCount(1)
        self.toc.setHeaderLabels(["目录"])
        self.toc.setFont(QFont("", 14))
        self.scrollarea = QScrollArea()
        self.scrollarea.setFont(QFont("", 14))
        self.scrollarea.setFrameShape(QFrame.NoFrame)
        self.addWidget(self.scrollarea)
        self.addWidget(self.toc)
        self.setSizes([450, 350])

    def updateToC(self, toc):
        self.toc.clear()
        floorlist = [0]
        nodelist = [self.toc]
        for line in toc:
            layer, title = line
            while floorlist[-1] >= layer:
                floorlist.pop()
                nodelist.pop()
            node = QTreeWidgetItem(nodelist[-1])
            node.setText(0, title)
            floorlist.append(layer)
            nodelist.append(node)

    def deleteForm(self):
        while self.form.count():
            item = self.form.takeAt(0)

    def updateView(self, note: Note):
        self.deleteForm()
        namelabel = QLabel("文件名")
        ctimelabel = QLabel("创建时间")
        atimelabel = QLabel("访问时间")
        mtimelabel = QLabel("修改时间")
        filelabel = QLabel("文件")
        pdflabel = QLabel("链接")
        taglabel = QLabel("标签")
        name = QLabel("未知")
        ctime = QLabel("未知")
        atime = QLabel("未知")
        mtime = QLabel("未知")
        file = MyLabel("无")
        pdf = MyLabel("无")
        tag = MyLabel("无")
        if note.name:
            name.setText(note.name)
            self.form.addRow(namelabel, name)
        if note.create_time:
            ctime.setText(note.create_time)
            self.form.addRow(ctimelabel, ctime)
        if note.visit_time:
            atime.setText(note.visit_time)
            self.form.addRow(atimelabel, atime)
        if note.mod_time:
            mtime.setText(note.mod_time)
            self.form.addRow(mtimelabel, mtime)
        if note.file_path:
            file.setText("<a style='color: blue'>{}</a>".format(note.file_path))
            self.form.addRow(filelabel, file)
            file.clicked.connect(lambda: self.openFile(note.file_path))
        if note.pdf_path:
            base, hfile = os.path.split(note.pdf_path)
            pdfname, sufix = os.path.splitext(hfile)
            pdf.setText("<a style='color: blue'>{}</a>".format(pdfname))
            self.form.addRow(pdflabel, pdf)
            pdf.clicked.connect(lambda: self.openFile(note.pdf_path))
        if note.tags:
            tag.setText(strSetToString(note.tags))
            self.form.addRow(taglabel, tag)
        tempWidget = QWidget()
        tempWidget.setLayout(self.form)
        self.scrollarea.setWidget(tempWidget)
        self.updateToC(note.getToC())

    def openFile(self, file_path):
        os.system('explorer /select, {}'.format(os.path.abspath(file_path)))


class MySearch(QToolBar):
    updateBookViewSignal = pyqtSignal(list)

    def __init__(self, db: MyDb):
        super(MySearch, self).__init__()
        self.db = db
        self.setFont(QFont("", 13))
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.searchBy = QComboBox()
        self.searchBy.addItems(['按名称', '按标签', '按内容'])
        self.searchAttr = self.searchBy.currentText()
        self.searchBy.currentTextChanged.connect(self.changeAttr)
        self.searchMode = QComboBox()
        self.searchMode.addItems(['模糊匹配', '准确匹配', '正则匹配'])
        self.searchAttrMode = self.searchMode.currentText()
        self.searchMode.currentTextChanged.connect(self.changeAttrMode)
        self.inputLine = QLineEdit()
        self.inputLine.returnPressed.connect(self.onSearch)  # 开始搜索
        self.inputCompleter = QCompleter()
        self.inputCompleter.setCaseSensitivity(Qt.CaseInsensitive)

        # 初始化
        model = QStringListModel()
        notenames = self.db.getAllNoteNames()
        model.setStringList(notenames)
        self.inputCompleter.setModel(model)
        self.inputCompleter.setFilterMode(Qt.MatchExactly)
        self.inputLine.setCompleter(self.inputCompleter)
        self.inputCompleter.popup().setFont(QFont("", 14))
        self.inputLine.setPlaceholderText("搜索")
        self.searchAct = QAction(QIcon("img/search-4.png"), "搜索", self)

        self.searchAct.triggered.connect(self.onSearch)

        self.addWidget(self.searchBy)
        self.addWidget(self.searchMode)
        self.addSeparator()
        self.addWidget(self.inputLine)
        self.addAction(self.searchAct)

    def onSearch(self):
        notes = self.db.getAllNotes()
        keyword = self.inputLine.text()
        if not keyword:
            notes = [note.name for note in notes]
            self.updateBookViewSignal.emit(notes)
            return
        if self.searchAttr == '按名称':
            if self.searchAttrMode == '准确匹配':
                notes = [note.name for note in notes if keyword == note.name]
            elif self.searchAttrMode == '模糊匹配':
                notes = [note.name for note in notes if keyword in note.name]
            else:
                notes = [note.name for note in notes if re.match(keyword, note.name)]
        elif self.searchAttr == '按标签':
            if self.searchAttrMode == '准确匹配':
                notes = [note.name for note in notes if keyword in note.tags]
            elif self.searchAttrMode == '模糊匹配':
                notes = [note.name for note in notes if note.hasTagFuzzy(keyword)]
            else:
                notes = [note.name for note in notes if note.hasTagReg(keyword)]
        elif self.searchAttr == '按内容':
            notes = [note.name for note in notes if note.textInFile(keyword)]
        self.updateBookViewSignal.emit(notes)

    def changeAttr(self, attr):
        self.searchAttr = attr
        model = QStringListModel()
        if attr == '按名称':
            notenames = self.db.getAllNoteNames()
            model.setStringList(notenames)
        elif attr == '按标签':
            tags = self.db.getAllTags()
            model.setStringList(tags)
        else:  # 按内容
            model.setStringList([])
        self.inputCompleter.setModel(model)

    def changeAttrMode(self, attrMode):
        self.searchAttrMode = attrMode
        if attrMode == '准确匹配':
            self.inputCompleter.setFilterMode(Qt.MatchExactly)
        elif attrMode == '模糊匹配':
            self.inputCompleter.setFilterMode(Qt.MatchContains)
