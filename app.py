
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

with open("*p.txt",'w') as f:
    f.write(os.environ.get('password'))
import sql

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/works")
async def getWork(request: Request):
    gr = request.headers.get('gr')
    email = request.headers.get('email')
    if gr:
        if gr:
            return {'works': sql.getAllWorkStudent(gr=gr)}
        else:
            return {'status': 'error'}

    elif email:
        credentials = sql.getTeacherCredential(email=email)
        if credentials:
            return{"works": sql.getAllWork(credentials['class'], credentials['section'])}
        else:
            return {'status': 'error'}
    else:
        return {'status': 'error'}


@app.get('/authStaff')
async def authStaff(req: Request):
    if req.headers.get('username') and req.headers.get('password'):
        w = sql.AuthStaff(req.headers.get('username'),
                          password=req.headers.get('password'))
        if w:
            return {"auth": True, "name": w}
        else:
            return{"auth": False}
    else:
        return{"auth": False}


@app.get('/addTeacher')
async def addTeacher(req: Request):
    email, name, _class, section, username, password = req.headers.get('email'), req.headers.get('name'), req.headers.get(
        'class'), req.headers.get('section'), req.headers.get('username'), req.headers.get('password')
    if (email and name and _class and section) and sql.AuthStaff(username=username, password=password):
        sql.newTeacher(email=email, name=name, _class=_class, section=section)
        return {'status': True}
    else:
        return{'status': False}


@app.get('/allTeachers')
async def allTeachers(req: Request):
    if sql.AuthStaff(username=req.headers.get('username'), password=req.headers.get('password')):
        return {'status': True, "teachers": sql.allTeachers()}
    else:
        return{'status': False}


@app.get('/parentWorks')
async def getParentWorks(req: Request):
    if req.headers.get('phone'):
        if sql.checkParent(req.headers.get('phone')):
            return {"status": True, "works": sql.getAllWorkForParent(phone=req.headers.get('phone'))}
        else:
            return {"status": False}
    else:
        return {"status": False}


@app.get('/workById')
async def workById(req: Request):
    if req.headers.get('id'):
        if req.headers.get('gr'):
            work = sql.getWorkWithId(req.headers.get(
                'id'), gr=req.headers.get('gr'))

        else:
            work = sql.getWorkWithId(req.headers.get('id'))
    return work if work else {'status': 'error'}


@app.get('/auth')
async def auth(request: Request):
    gr = request.headers.get('gr')
    work = sql.authStudent(gr=gr)
    return {"auth": True} if work else {"auth": False}


@app.get('/authTeacher')
async def authTeacher(req: Request):
    email, password = req.headers.get('email'), req.headers.get("password")
    work = sql.authTeacher(email=email, password=password)
    return {'auth': True} if work else {'auth': False}


@app.get('/authParent')
async def authParent(req: Request):
    if req.headers.get('phone') and sql.checkParent(req.headers.get('phone')):
        return {"status": True}
    else:
        return {"status": False}


@app.get('/authStudent')
async def authStudent(req: Request):
    if sql.authStudent(req.headers.get('gr')):
        return{"status": True}
    else:
        return {"status": False}


@app.get('/onDayWork')
async def onDayWork(req: Request):
    work = False
    if req.headers.get('gr'):
        cre = sql.getCredential(req.headers.get('gr'))
        work = sql.checkOnDayWork(_class=cre.get(
            'class'), section=cre.get('section')) if cre else False
    elif req.headers.get('email'):
        cre = sql.getTeacherCredential(req.headers.get('email'))
        work = sql.checkOnDayWork(_class=cre.get(
            'class'), section=cre.get('section')) if cre else False
    return {'status': True} if work else {"status": False}


# @app.get('/getTPmessages')
# async def getTPmessages(req: Request):
#     conditions = [req.headers.get('teacherEmail'), req.headers.get(
#         'studentGR'), req.headers.get('parentPhone')]
#     if conditions[1] and any(*conditions[1:]):
#         work = sql.getTPMessages(
#             parentPhone=conditions[2], teacherEmail=conditions[0], studentGr=conditions[1])
#         return {"status":True,"messages":work} if work else {"status":False}
#     else:
#         return False

# @app.get('/getTPChats')
# async def getTPChats(req: Request):
#     conditions = [req.headers.get('teacherEmail'), req.headers.get(
#         'parentPhone'), req.headers.get('studentGr')]
#     if any(conditions):
#         work = sql.getTPChats(
#             teacherEmail=conditions[0], parentPhone=conditions[1], studentGr=conditions[2])
#         return {'chats': work, "status": True} if work else {"status": False}
#     else:
#         return {"status": False}


@app.post('/uploadWork')
async def uploadWork(req: Request):
    jData = await req.json()
    if jData.get('email') and jData.get('cw') and jData.get('password'):
        if sql.authTeacher(jData.get('email'), jData.get('password')):
            teacher = sql.getTeacherCredential(jData.get('email'))
            if teacher:
                work = sql.insertWork(section=teacher.get('section'), _class=teacher.get(
                    'class'), hw=jData.get('hw'), cw=jData.get('cw'))
                if work:
                    return work
                else:
                    return{"status": False}
            else:
                return{"status": False}
        else:
            {"stauts": 'unauthorized'}
    else:
        return{"status": False}
