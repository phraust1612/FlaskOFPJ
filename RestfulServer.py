from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from CPortal import *
import time
import threading
import atexit

#global var
TODOS = {}
RES = {"message":"nothing"}
portal = CPortal()
dataLock = threading.Lock()
BGThread = threading.Thread()

def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))

parser = reqparse.RequestParser()
parser.add_argument("task",type=str)
parser.add_argument('ID',type=str)
parser.add_argument("PW",type=str)
parser.add_argument("yr",type=int)
parser.add_argument("mth",type=int)
parser.add_argument("day",type=int)
parser.add_argument("prior",type=int)

def create_app():
    app = Flask(__name__)
    api = Api(app)

    ##
    ## Actually setup the Api resource routing here
    ##
    api.add_resource(TodoList, '/todos')
    api.add_resource(Todo, '/todos/<todo_id>')
    api.add_resource(Res, '/result')

    def interrupt():
        global BGThread
        BGThread.cancel()

    def loop():
        global TODOS
        global RES
        global portal
        with dataLock:
            while len(TODOS)!=0:
                i = min(TODOS.keys())
                task = TODOS[i]["task"]
                if task == "login":
                    ID = TODOS[i]["ID"]
                    PW = TODOS[i]["PW"]
                    err = portal.SQLLogin(ID,PW)
                    if err != 0:
                        RES["message"] = "login failed"
                    else:
                        RES["message"] = "login suceeded"
                        portal.LoadMember()
                    del TODOS[i]
                elif task == "submit":
                    year = TODOS[i]["yr"]
                    month = TODOS[i]["mth"]
                    day = TODOS[i]["day"]
                    prior = TODOS[i]["prior"]
                    err = portal.SubmitWish("",prior,year,month,day)
                    if err==0:
                        RES["message"] = "submit suceeded"
                    else:
                        RES["message"] = "submit failed"
                    del TODOS[i]
                else:
                    RES["message"] = "unknown request"
                    del TODOS[i]
        BGThread = threading.Timer(0.1, loop, ())
        BGThread.start()

    def loopStart():
        global BGThread
        BGThread = threading.Timer(0.1, loop, ())
        BGThread.start()

    loopStart()
    atexit.register(interrupt)
    return app
    
# Todo
# shows a single todo item and lets you delete a todo item
class Todo(Resource):
    def get(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

    def put(self, todo_id):
        args = parser.parse_args()
        TODOS[todo_id] = args
        return task, 201

# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        return TODOS

    def post(self):
        args = parser.parse_args()
        todo_id = str(len(TODOS))
        TODOS[todo_id] = args
        return TODOS[todo_id], 201

class Res(Resource):
    def get(self):
        return RES

if __name__ == '__main__':
    app = create_app()
    app.run()
