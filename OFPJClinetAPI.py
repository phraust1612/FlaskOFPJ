from requests import *

# {"message": <some message will be here>}
# ex. After you called TryLogin function and if it suceeds,
# GetLastResponse will return {"message":"login suceeded"} and 200
def GetLastResponse():
    return get("http;//172.22.55.148:5000/result")

def TryLogin(ID,PW):
    return post("http://172.22.55.148:5000/todos",
                data={"task":"login","ID":ID,"PW":PW})


def SubmitWish(year,month,day,prior):
    return post("http://172.22.55.148:5000/todos"
                data={"task":"submit","yr":year,"mth":month,"day":day,"prior":prior})
