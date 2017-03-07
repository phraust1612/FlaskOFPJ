import random
import mysql.connector
from mysql.connector import errorcode
from CRefine import *
class InfoStr:
    def __init__(self):
        self.start = CRefine(1990,1,1)
        self.end = CRefine(1990,1,1)

class Member:
    def __init__(self):
        self.name = ""
        #default allocated : 1 / 0 when it has an application
        self.allocated = 1
        self.wish = [InfoStr(),InfoStr(),InfoStr()]
        self.fixed = []

class Slot:
    def __init__(self):
        self.start = CRefine(1990,1,1)
        self.end = CRefine(1990,1,1)
        self.num = 0
        self.list = []

class CPortal:
    def __init__(self):
        self.loginsuccess = 0
        self.p_err = 0
        self.slot = []
        self.member = []
        self.maxMem = 0
        self.maxSlot = 0
        self.ID = ""
        self.p = []
        self.r = []
    def __del__(self):
        self.slot = 0
        self.member = 0
        self.ID = ""
        self.p = 0
        self.r = 0
        try:
            self.cursor
        except AttributeError:
            pass
        else:
            self.connection.close()
            self.cursor.close()

    #try login with id,pw
    #return errno if error occurs
    def SQLLogin(self,ID,PW):
        try:
            self.connection = mysql.connector.connect(user=ID,password=PW,host='127.0.0.1',database='OffdayProj3',port=3306)
        except mysql.connector.Error as err:
            return err.errno
        self.ID = ID
        self.cursor=self.connection.cursor()
        if ID=='root':
            self.loginsuccess = 1
        else:
            self.loginsuccess = 2
        return 0

    #make a new account and grant it for right privileges
    def SQLNewID(self,ID,PW,name):
        if self.loginsuccess ==0:
            return 1
        else:
            query = "create user '" + ID + "'@'%'identified by '" + PW + "'"
            try:
                self.cursor.execute(query)
                self.connection.commit()
            except mysql.connector.Error as err:
                return err.errno * -1
            query = "grant all privileges on *.* to '" + ID +"'@'%'"
            try:
                self.cursor.execute(query)
                self.connection.commit()
            except mysql.connector.Error as err:
                return err.errno * -1
            self.AddMember(name,ID)
            return 0

    def SQLModID(self,ID,PW,name):
        if self.loginsuccess ==0:
            return 1
        else:
            query = "set password for '"+ID+"'@'%'=password('"+PW+"')"
            try:
                self.cursor.execute(query)
                self.connection.commit()
            except mysql.connector.Error as err:
                return err.errno * -1
            query = "update member set name='"+name+"' where ID like '"+ID+"'"
            try:
                self.cursor.execute(query)
                self.connection.commit()
            except mysql.connector.Error as err:
                return err.errno * -1
            return 0

    #quick sort :)
    def q_sort(self,left,right):
        if left>=right:
            return
        lhold=left
        rhold=right
        pivot=self.r[left]
        ppivot=self.p[left]
        while left<right:
            while self.r[right]>=pivot and left<right:
                right-=1
            if left!=right:
                self.r[left]=self.r[right]
                self.p[left]=self.p[right]
                left+=1
            while self.r[left]<=pivot and left<right:
                left+=1
            if left!=right:
                self.r[right]=self.r[left]
                self.p[right]=self.p[left]
                right-=1
        self.r[left]=pivot
        self.p[left]=ppivot
        pivot=left
        left=lhold
        right=rhold
        if left<pivot:
            self.q_sort(left,pivot-1)
        if right>pivot:
            self.q_sort(pivot+1,right)

    #load from Member table to self.member
    def LoadMember(self):
        self.maxMem=0
        self.maxSlot=0
        if self.loginsuccess==0:
            return 1
        query="select name from Member"
        try:
            self.cursor.execute(query)
        except mysql.connector.Error as err:
            return err.errno * -1
        for name in self.cursor:
            self.AddMember(name[0],0)
        return 0

    #load from Application, Fixed tables to self.member
    def LoadData(self,y,m,d):
        if self.loginsuccess==0:
            return 1
        y2=y
        m2=m+2
        if m2>12:
            y2+=1
            m2 -= 12
        for i in range(0,self.maxMem):
            tmpname = self.member[i].name
            query = "select outdate,indate,priority from Application where memNo like "
            query += str(i)+" and outdate>='"
            query += str(y)+"-"+str(m)+"-"+str(d)
            query += "' and indate<'"
            query += str(y2)+"-"+str(m2)+"-1'"
            try:
                self.cursor.execute(query)
            except mysql.connector.Error as err:
                return err.errno * -1
            self.member[i].allocated=1
            for (outdate,indate,priority) in self.cursor:
                #allocated = 0  if application exists
                oiso = outdate.isoformat()
                iiso = indate.isoformat()
                self.member[i].allocated=0
                self.member[i].wish[priority].start = CRefine(oiso)
                self.member[i].wish[priority].end = CRefine(iiso)
        for i in range(0,self.maxMem):
            tmpname = self.member[i].name
            query = "select outdate,indate from Fixed where memNo like "
            query += str(i)+" and outdate>='"
            query += str(y)+"-"+str(m)+"-"+str(d)
            query += "' and indate<'"
            query += str(y2)+"-"+str(m2)+"-1'"
            try:
                self.cursor.execute(query)
            except mysql.connector.Error as err:
                return err.errno * -1
            for (outdate,indate) in self.cursor:
                oiso = outdate.isoformat()
                iiso = indate.isoformat()
                self.member[i].fixed.append(InfoStr())
                tlen = len(self.member[i].fixed) - 1
                self.member[i].fixed[tlen].start = CRefine(oiso)
                self.member[i].fixed[tlen].end = CRefine(iiso)
        return 0

    #reset all datas from self.slot and db datas
    def FlushData(self):
        if len(self.slot)>0:
            outstr = self.slot[0].start.refineToString()
            instr = self.slot[self.maxSlot-1].end.refineToString()
        #self.member.clear()
        #self.maxMem=0
        #self.p.clear()
        #self.r.clear()
        self.slot.clear()
        self.maxSlot=0
        if self.loginsuccess==0:
            return 1
        try:
            outstr
        except AttributeError:
            return 2
        except NameError:
            return 3
        query = "delete from Application where outdate>='"
        query += outstr + "' and outdate<'"
        query += instr + "'"
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except mysql.connector.Error as err:
            return err.errno * -1
        query = "delete from Fixed where outdate>='"
        query += outstr + "' and outdate<'"
        query += instr + "'"
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except mysql.connector.Error as err:
            return err.errno * -1
        return 0
    
    #look for his member no. and return it
    #if he doesn't exist, return -2
    def SearchMemNo(self,name):
        for i in range(0,self.maxMem):
            if self.member[i].name == name:
                return i
        return -2

    #search memno by self.ID
    def SearchByID(self):
        if self.loginsuccess ==0:
            return -1
        query = "select name from Member where ID like '"+self.ID+"'"
        try:
            self.cursor.execute(query)
        except mysql.connector.Error as err:
            return err.errno * -1
        tname = "nonameexist"
        for name in self.cursor:
            tname = name[0]
        return self.SearchMemNo(tname)
    
    #add a new member if he doesn't exist before
    #if no error occurs, return his member no.
    #if some db error occurs, return negative errno
    #if qgo==0, it doesn't input into db
    def AddMember(self,name,nID):
        i=self.SearchMemNo(name)
        if i>=0:
            return i
        if self.loginsuccess>0 and type(nID)==str:
            query = "select memNo from Member where ID like '"+nID+"'"
            try:
                self.cursor.execute(query)
            except mysql.connector.Error as err:
                return err.errno * -1
            tNo = -1
            for memNo in self.cursor:
                tNo = memNo
            if tNo>=0:
                query = "update Member set name='"+name+"' where ID like '"
                query += nID + "'"
            else:
                query = "insert into Member (memNo,name,ID) values ("
                query += str(self.maxMem)+",'"+name+"','"+nID+"')"
            try:
                self.cursor.execute(query)
                self.connection.commit()
            except mysql.connector.Error as err:
                return err.errno * -1
        self.member.append(Member())
        self.member[self.maxMem].name=name
        self.maxMem+=1
        return self.maxMem-1

    #load datas from db and allocate self.slots
    #if some db error occurs return negative errno
    def AutoAllocateSlot(self,y,m,d):
        err = self.LoadData(y,m,d)
        if err<0:
            return err
        PeriodEnd = CRefine(y,m,d)
        while PeriodEnd.m-m<2 and m-PeriodEnd.m<2:
            self.slot.append(Slot())
            self.slot[self.maxSlot].start = PeriodEnd.clone()
            self.slot[self.maxSlot].end = PeriodEnd.clone()
            self.slot[self.maxSlot].end.addDay(3)
            self.slot[self.maxSlot].num=0
            self.maxSlot+=1
            PeriodEnd.addDay(4)
        return 0

    #randomly allocate vacation according to previous datas
    def RandSimulate(self):
        #reset slots
        for i in range(0,self.maxSlot):
            self.slot[i].list.clear()
        #allocate fixed vacations
        for i in range(0,self.maxMem):
            for j in self.member[i].fixed:
                slotleft=0
                while slotleft<self.maxSlot and j.start.diffBtwn(self.slot[slotleft].start)>=0:
                    slotleft+=1
                slotleft-=1
                if slotleft>=self.maxSlot:
                    continue
                slotright=slotleft
                while slotright<self.maxSlot and j.end.diffBtwn(self.slot[slotright].end)>0:
                    slotright+=1
                if slotright>=self.maxSlot:
                    slotright=self.maxSlot-1
                for k in range(slotleft,slotright+1):
                    self.slot[k].list.append(i)
                    self.slot[k].num+=1
        #clear and randomly sort members
        self.p.clear()
        self.r.clear()
        for i in range(0,self.maxMem):
            self.p.append(i)
            self.r.append(random.random())
        self.q_sort(0,self.maxMem-1)
        #allocate vacations
        for i in self.slot:
            for k in range(0,3):
                for j in range(0,self.maxMem):
                    #if this slot is full, go for next one
                    if i.num > 1:
                        continue
                    if self.member[self.p[j]].allocated > 0:
                        continue
                    if self.member[self.p[j]].wish[k].start.diffBtwn(i.start)==0:
                        i.list.append(self.p[j])
                        i.num += 1
                        self.member[self.p[j]].allocated = 1
        return 0

    #input query into Application table
    #return negative int if error occurs
    def SubmitWish(self,no,p, y,m,d):
        p -= 1
        if type(no)==str:
            if no=="":
                no = self.SearchByID()
            else:
                no=self.AddMember(no,1)
            if no<0:
                return no
        if no>=self.maxMem or no<0:
            return -1
        if p<0 or p>2:
            return -2
        for i in range(p,3):
            self.member[no].wish[i].start = CRefine(y,m,d)
            self.member[no].wish[i].end = CRefine(y,m,d)
            self.member[no].wish[i].end.addDay(3)
        self.member[no].allocated = 0
        if self.loginsuccess>0:
            query = "select priority from Application where memNo like "+str(no)
            try:
                self.cursor.execute(query)
            except mysql.connector.Error as err:
                return err.errno * -1
            t=0
            for priority in self.cursor:
                if priority[0]==p:
                    t=1
            outdatestr = self.member[no].wish[p].start.refineToString()
            indatestr = self.member[no].wish[p].end.refineToString()
            if t:
                query = "update Application set outdate='"
                query += outdatestr+"',indate='"
                query += indatestr+"' where priority like "+str(p)
            else:
                query = "insert into Application (memNo,outdate,indate,priority) values ("
                query += str(no)+",'"+outdatestr + "','"+ indatestr + "'," + str(p) + ")"
            try:
                self.cursor.execute(query)
                self.connection.commit()
            except mysql.connector.Error as err:
                return err.errno * -1
        return 0

    #input query into Fixed table
    #return neg int if error occurs
    def InsertFixed(self,no, y,m,d, y2,m2,d2):
        if type(no)==str:
            if no=="":
                no = self.SearchByID()
            else:
                no=self.AddMember(no,1)
            if no<0:
                return no
        self.member[no].fixed.append(InfoStr())
        tlen = len(self.member[no].fixed) - 1
        self.member[no].fixed[tlen].start = CRefine(y,m,d)
        self.member[no].fixed[tlen].end = CRefine(y2,m2,d2)
        if self.loginsuccess>0:
            outdatestr = self.member[no].fixed[tlen].start.refineToString()
            indatestr = self.member[no].fixed[tlen].end.refineToString()
            query = "insert into fixed (memNo,outdate,indate) values ("
            query += str(no) + ",'"
            query += outdatestr +"','"
            query += indatestr + "')"
            try:
                self.cursor.execute(query)
                self.connection.commit()
            except mysql.connector.Error as err:
                return err.errno * -1
        return 0
