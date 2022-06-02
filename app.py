

from json import loads

from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware

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
    phone = request.headers.get('phone')
    if gr and sql.authStudent(gr=gr):
        return {'works': sql.getAllWorkStudent(gr=gr), 'status': True}

    elif email:
        credentials = sql.getTeacherCredential(email=email)
        return{"works": sql.getAllWork(_class=credentials.get('class'), section=credentials.get('section')), 'status': True}
    elif phone:
        return {"works": sql.getAllWorkForParent(phone=phone), 'status': True}
    return {'status': False}


@app.get('/seenByStudent')
async def seenByStudents(req: Request):
    if req.headers.get('id'):
        return {'students': sql.seenByStudents(req.headers.get('id')), "status": True}
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
    return {"status": True, "work": work} if work else {'status': 'error'}


@app.get('/auth')
async def auth(request: Request):
    gr = request.headers.get('gr')
    email, password = request.headers.get(
        'email'), request.headers.get('password')
    phone = request.headers.get('phone')
    if gr and sql.authStudent(gr=gr):
        works = sql.getAllWorkStudent(gr=gr)
        return {"auth": True, "works": works}
    elif email and password and sql.authTeacher(email=email, password=password):
        credentials = sql.getTeacherCredential(email=email)
        return {'auth': True, "works": sql.getAllWork(_class=credentials.get('class'), section=credentials.get('section'))}
    elif phone and sql.checkParent(phone=phone):
        return {'auth': True, "works": sql.getAllWorkForParent(phone=phone)}
    return {'auth': False}


@app.get('/onDayWork')
async def onDayWork(req: Request):
    cre = sql.getTeacherCredential(req.headers.get('email'))
    work = sql.checkOnDayWork(_class=cre.get(
        'class'), section=cre.get('section'), date=req.headers.get('date')) if cre else False
    return {'todayWork': True} if work else {"todayWork": False}


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

@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        if (data):
            ...
            # print(data)


@app.post('/uploadWork')
async def uploadWork(req: Request):
    jData = await req.json()
    if jData.get('email') and jData.get('work') and jData.get('password'):
        if sql.authTeacher(jData.get('email'), jData.get('password')):
            teacher = sql.getTeacherCredential(jData.get('email'))
            if teacher:
                work = sql.insertWork(section=teacher.get('section'), _class=teacher.get(
                    'class'), work=jData.get('work'), date=jData.get('date'))
                if work:
                    return {'status': True, "data": work}
                else:
                    return{"status": False}
            else:
                return{"status": False}
        else:
            {"stauts": 'unauthorized'}
    else:
        return{"status": False}
