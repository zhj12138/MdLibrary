import sqlite3
from basic import strSetToString, parseStrSetString
from note import Note


class MyDb:
    def __init__(self, name):
        self.name = name
        self.mdTable = "mdTable"
        self.lastDir = "lastDirTable"
        self.conn = None
        self.cursor = None
        try:
            self.createDirTable()
            self.createMdTable()
        except:
            pass

    def connect(self):
        self.conn = sqlite3.connect(self.name)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.commit()
        self.conn.close()

    def createDirTable(self):
        self.connect()
        self.cursor.execute("create table %s (dir text)" % self.lastDir)
        self.close()

    def createMdTable(self):
        self.connect()
        self.cursor.execute("create table %s (name text primary key, filepath text, mtime text, ctime text, atime text,"
                            "md5code text, pdfpath text, tags text)" % self.mdTable)
        self.close()

    def hasDir(self):
        self.connect()
        ret = self.cursor.execute("select * from %s" % self.lastDir)
        temp = []
        for line in ret:
            temp.append(line)
        self.close()
        if temp:
            return True
        return False

    def changeDir(self, newDir):
        self.connect()
        self.cursor.execute("delete from %s" % self.lastDir)
        self.cursor.execute("insert into %s values('%s')" % (self.lastDir, newDir))
        self.close()

    def getDir(self):
        self.connect()
        ret = self.cursor.execute("select * from %s" % self.lastDir)
        temp = []
        for line in ret:
            temp.append(line[0])
        self.close()
        if temp:
            return temp[0]
        return "."

    def addNote(self, note):
        self.connect()
        self.cursor.execute("insert into %s values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (self.mdTable,
                                                                                                       note.name,
                                                                                                       note.file_path,
                                                                                                       note.mod_time,
                                                                                                       note.create_time,
                                                                                                       note.visit_time,
                                                                                                       note.md5code,
                                                                                                       note.pdf_path,
                                                                                                       strSetToString(
                                                                                                           note.tags)))
        self.close()

    def deleteNote(self, name):
        self.connect()
        self.cursor.execute("delete from %s where name='%s'" % (self.mdTable, name))
        self.close()

    def updateNote(self, note):
        self.connect()
        self.cursor.execute("update %s set filepath='%s', mtime='%s', ctime='%s', atime='%s', md5code='%s',         "
                            " pdfpath='%s', tags='%s' where name='%s'" % (self.mdTable, note.file_path, note.mod_time,
                                                                          note.create_time, note.visit_time,
                                                                          note.md5code, note.pdf_path,
                                                                          strSetToString(note.tags), note.name))
        self.close()

    def getAllTags(self):
        self.connect()
        ret = self.cursor.execute("select tags from %s" % self.mdTable)
        temp = set()
        for line in ret:
            tags = parseStrSetString(line[0])
            temp.update(tags)
        return temp

    def getAllNoteNames(self):
        self.connect()
        ret = self.cursor.execute("select name from %s" % self.mdTable)
        temp = []
        for line in ret:
            name = line[0]
            temp.append(name)
        return temp

    def getNoteByName(self, name):
        self.connect()
        ret = self.cursor.execute("select * from %s where name='%s'" % (self.mdTable, name))
        notes = []
        for line in ret:
            name = line[0]
            filepath = line[1]
            mtime = line[2]
            ctime = line[3]
            atime = line[4]
            md5code = line[5]
            pdfpath = line[6]
            tags = parseStrSetString(line[7])
            note = Note(name, filepath, mtime, ctime, atime, md5code, pdfpath, tags)
            notes.append(note)
        if not notes:
            return None
        return notes[0]

    def getAllNotes(self):
        self.connect()
        ret = self.cursor.execute("select * from %s" % self.mdTable)
        notes = []
        for line in ret:
            name = line[0]
            filepath = line[1]
            mtime = line[2]
            ctime = line[3]
            atime = line[4]
            md5code = line[5]
            pdfpath = line[6]
            tags = parseStrSetString(line[7])
            note = Note(name, filepath, mtime, ctime, atime, md5code, pdfpath, tags)
            notes.append(note)
        return notes

    def getAllPDFs(self):
        self.connect()
        ret = self.cursor.execute("select pdfpath from %s" % self.mdTable)
        pdfs = set()
        for line in ret:
            pdf = line[0]
            if pdf:
                pdfs.add(pdf)
        return pdfs

    def noteInDb(self, name):
        if self.getNoteByName(name):
            return True
        return False

    def getAllMd5(self):
        ret = self.cursor.execute("select md5code from %s" % self.mdTable)
        temp = []
        for line in ret:
            md5code = line[0]
            temp.append(md5code)
        return temp

    def hasTheSame(self, name, md5code):
        self.connect()
        ret = self.cursor.execute("select * from %s where name='%s' and md5code='%s'" % (self.mdTable, name, md5code))
        temp = []
        for line in ret:
            temp.append(line)
        if temp:
            return True
        return False
