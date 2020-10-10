import shutil
from typing import Set
import time
import hashlib
import markdown
from PyQt5.QtCore import QMimeData, QUrl
from PyQt5.QtWidgets import QApplication, QInputDialog, QMessageBox
from bs4 import BeautifulSoup
import csv

StrSet = Set[str]


def strSetToString(strset: StrSet):
    return ', '.join(strset)


def parseStrSetString(setstring: str):
    if not setstring:
        return set()
    ret = set()
    temp_list = setstring.split(',')
    for temp in temp_list:
        ret.add(temp.strip())
    return ret


def getFormatTime(stamp: float):
    temp = time.localtime(stamp)
    return time.strftime("%Y/%m/%d %H:%M:%S", temp)


def getMd5(filename: str):
    with open(filename, "rb") as f:
        text = f.read()
    return hashlib.md5(text).hexdigest()


def parseToC(filename):
    with open(filename, "r", encoding='utf-8') as f:
        text = f.read()
    extensions = [
        'markdown.extensions.abbr',
        'markdown.extensions.attr_list',
        'markdown.extensions.def_list',
        'markdown.extensions.fenced_code',
        'markdown.extensions.footnotes',
        'markdown.extensions.md_in_html',
        'markdown.extensions.tables',
        'markdown.extensions.codehilite',
        'markdown.extensions.legacy_em',
        'markdown.extensions.toc',
        'markdown.extensions.wikilinks',
        'markdown.extensions.admonition',
        'markdown.extensions.legacy_attrs',
        'markdown.extensions.meta',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
        'markdown.extensions.smarty',
    ]
    html = markdown.markdown(text, extensions=extensions)
    # print(html)
    soup = BeautifulSoup(html, 'html.parser')
    temp = soup.findAll(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    return [[int(line.name[1:]), line.text] for line in temp]


def copyFile(filepath):
    data = QMimeData()
    url = QUrl.fromLocalFile(filepath)
    data.setUrls([url])
    QApplication.clipboard().setMimeData(data)


def copyText(text):
    QApplication.clipboard().setText(text)


def getName(name, names):
    newname, ok = QInputDialog.getText(QInputDialog(), "重命名", "请输入新的名称", text=name)
    if not ok:
        return ""
    if not newname or newname in names:
        box = QMessageBox(QMessageBox.Question, '提醒', '名字为空或已存在同名文件')
        yes = box.addButton("重命名", QMessageBox.YesRole)
        no = box.addButton("取消", QMessageBox.NoRole)
        box.setIcon(1)
        box.exec_()
        if box.clickedButton() == yes:
            getName(name, names)
        elif box.clickedButton() == no:
            return ""
    return newname


def exportInfo(filepath, headers, rows):
    with open(filepath, 'w') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(headers)
        f_csv.writerows(rows)


def backUpFile(baseDir, filenames):
    suc = 0
    fail = 0
    for file in filenames:
        try:
            shutil.copy(file, baseDir)
        except:
            fail += 1
        else:
            suc += 1
    return suc, fail



