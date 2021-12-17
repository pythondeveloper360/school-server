from fastapi import FastAPI, Request
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
    if gr:
        credentials = sql.getCredential(gr=gr)
        if credentials:
            return {'works': sql.getAllWork(credentials['class'], credentials['section'])}
    elif email:
        credentials = sql.getTeacherCredential(email=email)
        if credentials:
            return{"work": sql.getAllWork(credentials['class'], credentials['section'])}
    else:
        return {'status': 'error'}


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
async def authParent(req:Request):
    if req.headers.get('phone') and sql.checkParent(req.headers.get('phone')):
        return {"status": True}
    else: return {"status": False}

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
