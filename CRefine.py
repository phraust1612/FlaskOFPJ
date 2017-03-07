def maxDayOfMonth(y,m):
    if m==1 or m==3 or m==5 or m==7 or m==8 or m==10 or m==12:
        return 31
    elif m==4 or m==6 or m==9 or m==11:
        return 30
    elif y%4==0 and m==2:
        return 29
    elif y%4!=0 and m==2:
        return 28
    else:
        return -1
    
class CRefine:
    def __init__(self,*argv):
        argc = len(argv)
        if argc == 1:
            if type(argv[0])!=str:
                print("Wrong initial input - you should use string")
                return
            ty = int(argv[0][:4])
            tm = int(argv[0][5:7])
            td = int(argv[0][8:])
            if ty <1900 or ty>2500:
                print("Wrong initial y")
                return
            tmax = maxDayOfMonth(ty,tm)
            if tmax<0:
                print("Wrong initial month")
                return
            if td>=tmax or td<1:
                print("Wrong initial day")
                return
            self.y = ty
            self.m = tm
            self.d = td
            self.errno = 0
            self.errmsg = ""
        elif argc == 3:
            ty = argv[0]
            tm = argv[1]
            td = argv[2]
            if type(ty)!=int or type(tm)!=int or type(td)!=int:
                print("Wrong initial input - you should use 3 int's")
                return
            if ty <1900 or ty>2500:
                print("Wrong initial year")
                return
            tmax = maxDayOfMonth(ty,tm)
            if tmax<0:
                print("Wrong initial month : ",str(tm))
                return
            if td>tmax or td<1:
                print("Wrong initial day : "+str(td)+"<"+str(tmax))
            self.y = ty
            self.m = tm
            self.d = td
            self.errno = 0
            self.errmsg = ""
        else:
            print("Wrong initial input")
            return
    def addDay(self, plus):
        tmax = maxDayOfMonth(self.y,self.m)
        if tmax<0:
            return -1
        self.d = self.d+plus
        while tmax<self.d:
            self.d -= tmax
            self.m += 1
            if self.m>12:
                self.y += 1
                self.m = 1
        return 0
    def diffBtwn(self, other):
        if type(other)!=CRefine:
            return -1
        a = self.d
        b = other.d
        if self.y == other.y:
            if self.m == other.m:
                return a-b
            else:
                for i in range(1,self.m):
                    a += maxDayOfMonth(self.y,i)
                for i in range(1,other.m):
                    b += maxDayOfMonth(other.y,i)
        else:
            for i in range(1,self.m):
                a += maxDayOfMonth(self.y,i)
            for i in range(1,other.m):
                b += maxDayOfMonth(other.y,i)
            if self.y > other.y:
                for i in range(other.y,self.y):
                    a+=365
                    if i%4==0:
                        a += 1
            else:
                for i in range(self.y, other.y):
                    b+=365
                    if i%4==0:
                        b+=1
        return a-b
    def refineToString(self):
        tmp = str(self.y)
        tmp += '-'
        tmp += str(self.m)
        tmp += '-'
        tmp += str(self.d)
        return tmp
    def clone(self):
        ans = CRefine(self.y,self.m,self.d)
        return ans
