import os
import re
import time

from PyQt5.QtWidgets import QMessageBox, QInputDialog

from basic import getFormatTime, getMd5, parseToC


class Note:
    def __init__(self, name="", file_path="", mod_time="", create_time="", visit_time="", md5code="", pdf_path="",
                 tags=None):
        if tags is None:
            tags = set()
        self.name = name
        self.file_path = file_path
        self.mod_time = mod_time  # 修改时间
        self.create_time = create_time  # 创建时间
        self.visit_time = visit_time  # 最近访问时间
        self.md5code = md5code
        self.pdf_path = pdf_path
        self.tags = tags

    def updateInfo(self, db):
        if not os.path.exists(self.file_path):  # 文件找不到了
            db.deleteNote(self.name)
            return
        self.mod_time = getFormatTime(os.path.getmtime(self.file_path))
        self.md5code = getMd5(self.file_path)
        if not os.path.exists(self.pdf_path):  # 链接的pdf找不到了
            self.pdf_path = ""
        self.updateDB(db)

    def deletePDF(self, db):
        self.pdf_path = ""
        self.updateDB(db)

    def addTag(self, db, tag):
        self.tags.add(tag)
        self.updateDB(db)

    def setTags(self, db, tags):
        self.tags = tags
        self.updateDB(db)

    def deleteTag(self, db, tagname):
        self.tags.remove(tagname)
        self.updateDB(db)

    def renameTag(self, db, oldtag, newtag):
        self.tags.remove(oldtag)
        self.tags.add(newtag)
        self.updateDB(db)

    def linkToPDF(self, db, pdf_path):
        if os.path.exists(pdf_path):
            self.pdf_path = pdf_path
            self.updateDB(db)

    def updateVisitTime(self, db):
        self.visit_time = getFormatTime(time.time())
        self.updateDB(db)

    def updateDB(self, db):
        db.updateNote(self)

    def getToC(self):
        if os.path.exists(self.file_path):
            return parseToC(self.file_path)
        else:
            return []

    def textInFile(self, text):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return text.lower() in content.lower()

    def hasTagAccurate(self, ta):
        for tag in self.tags:
            if ta.lower() == tag.lower():
                return True
        return False

    def hasTagFuzzy(self, ta):
        for tag in self.tags:
            if ta.lower() in tag.lower():
                return True
        return False

    def hasTagReg(self, ta):
        for tag in self.tags:
            if re.match(ta, tag):
                return True
        return False


def getNewName(names):
    newName, ok = QInputDialog.getText(QInputDialog(), '输入', "输入新的文件名")
    if not ok:
        return "", False
    if not newName:
        box = QMessageBox(QMessageBox.Question, '提醒', '您未输入任何字符')
        yes = box.addButton("重新输入", QMessageBox.YesRole)
        no = box.addButton("取消重命名", QMessageBox.NoRole)
        box.setIcon(1)
        box.exec_()
        if box.clickedButton() == no:
            return "", False
        elif box.clickedButton() == yes:
            getNewName(names)
    if newName in names:
        box = QMessageBox(QMessageBox.Question, '提醒', '已存在同名文件')
        yes = box.addButton("重新输入", QMessageBox.YesRole)
        no = box.addButton("取消重命名", QMessageBox.NoRole)
        box.setIcon(1)
        box.exec_()
        if box.clickedButton() == no:
            return "", False
        elif box.clickedButton() == yes:
            getNewName(names)
    return newName, True


def createANewNote(db, file_path):
    file = os.path.basename(file_path)
    name, sufix = os.path.splitext(file)
    flag = False
    md5code = getMd5(file_path)
    if db.hasTheSame(name, md5code):
        return
    if db.noteInDb(name):
        box = QMessageBox(QMessageBox.Question, '提醒', '存在同名文件{},是否覆盖'.format(name))
        yes = box.addButton("覆盖", QMessageBox.YesRole)
        rename = box.addButton("重命名", QMessageBox.ResetRole)
        no = box.addButton("跳过", QMessageBox.NoRole)
        box.setIcon(1)
        box.exec_()
        if box.clickedButton() == no:
            return
        elif box.clickedButton() == rename:
            names = db.getAllNoteNames()
            newName, ok = getNewName(names)
            if not ok:
                return
            name = newName
        elif box.clickedButton() == yes:
            flag = True
    if md5code:  # 允许多个空文件
        md5s = db.getAllMd5()
        if md5code in md5s:
            ret = QMessageBox.question(QMessageBox(), '提示', "已存在与{}内容相同的文件，是否继续导入".format(name),
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if ret == QMessageBox.No:
                return
    # try:
    #     newFilePath = shutil.copy(file_path, base_path)
    # except:
    #     QMessageBox.warning(QMessageBox(), "抱歉", "导入{}失败".format(name))
    #     return
    mod_time = getFormatTime(os.path.getmtime(file_path))
    create_time = getFormatTime(os.path.getctime(file_path))
    visit_time = getFormatTime(time.time())
    note = Note(name, file_path, mod_time, create_time, visit_time, md5code)
    if flag:
        db.updateNote(note)
    else:
        db.addNote(note)


def createAEmptyNote(db, file_path):
    file = os.path.basename(file_path)
    name, sufix = file.split('.')
    flag = False
    if db.noteInDb(name):
        box = QMessageBox(QMessageBox.Question, '提醒', '存在同名文件{},是否覆盖'.format(name))
        yes = box.addButton("覆盖", QMessageBox.YesRole)
        rename = box.addButton("重命名", QMessageBox.ResetRole)
        no = box.addButton("跳过", QMessageBox.NoRole)
        box.setIcon(1)
        box.exec_()
        if box.clickedButton() == no:
            return
        elif box.clickedButton() == rename:
            names = db.getAllNoteNames()
            newName, ok = getNewName(names)
            if not ok:
                return
            name = newName
        elif box.clickedButton() == yes:
            flag = True
    f = open(file_path, 'w', encoding='utf-8')
    f.close()
    create_time = getFormatTime(time.time())
    visit_time = create_time
    mod_time = create_time
    md5code = ""
    note = Note(name, file_path, mod_time, create_time, visit_time, md5code)
    if flag:
        db.updateNote(note)
    else:
        db.addNote(note)
