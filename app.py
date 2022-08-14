

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
        return {"auth": True}
    elif email and password and sql.authTeacher(email=email, password=password):
        credentials = sql.getTeacherCredential(email=email)
        return {'auth': True}
    elif phone and sql.authParent(phone=phone):
        return {'auth': True}
    return {'auth': False}


@app.get('/onDayWork')
async def onDayWork(req: Request):
    cre = sql.getTeacherCredential(req.headers.get('email'))
    work = sql.checkOnDayWork(_class=cre.get(
        'class'), section=cre.get('section'), date=req.headers.get('date')) if cre else False
    return {'todayWork': True} if work else {"todayWork": False}


@app.post('/uploadWork')
async def uploadWork(req: Request):
    jData = await req.json()
    if 'email' in jData and 'work' in jData and 'password' in jData:
        auth = sql.authTeacher(jData.get('email'), jData.get('password'))
        teacher = sql.getTeacherCredential(jData.get('email'))
        if auth and teacher:
            work = sql.insertWork(section=teacher.get('section'), _class=teacher.get(
                'class'), work=jData.get('work'), date=jData.get('date'))
            if work:
                return {'status': True, "data": work}

    else:
        return{"status": False}

app.post('/reportBug')
async def reportBug(req: Request):
    jData = await req.json()
    if sql.reportBug(by=jData.get('by'), bug=jData.get("bug"),
                     credential=jData.get("credential"), date=jData.get("date")):
        return {'status': True}
    return {'status': 'False'}
