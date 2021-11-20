import datetime
import random
from json import dumps

from psycopg2 import connect, sql

db = connect(
    host='localhost',
    port='5432',
    user='postgres',
    database='school',
    password='qsa-1299'
)
cursor = db.cursor()

alphabet = [*[chr(i) for i in range(97, 123)], *[chr(i)
                                                 for i in range(65, 91)], *[chr(i) for i in range(48, 58)]]


def idGenerator(_range: int = 10):
    random.shuffle(alphabet)
    return ''.join(alphabet[0:int(_range)])


def getAllWork(_class: str, section: str):
    sqlquery = sql.SQL('select {id},{date} from work where {_class} = %s and {section} = %s').format(
        _class=sql.Identifier("class"),
        section=sql.Identifier("section"),
        id=sql.Identifier("id"),
        date=sql.Identifier("date")
    )

    cursor.execute(sqlquery, (_class, section))
    data = cursor.fetchall()
    return [{"id": i[0], "date":i[1].strftime('%b %d %A')} for i in data][::-1] if data else False


def getWorkWithId(id: str):
    sqlquery = sql.SQL(
        'select * from work where {id} = %s').format(id=sql.Identifier("id"))
    cursor.execute(sqlquery, (id,))
    data = cursor.fetchone()
    return {'id': data[0], 'date': data[1].strftime('%b %d %A'), 'hw': data[2]['hw'], 'cw': data[3]['cw'], 'time': data[6].strftime('%-I:%M %p')} if data else False


def checkOnDayWork(date = datetime.datetime.now().strftime('%Y-%m-%d')):
    sqlquery = sql.SQL('select id from work where {date} = %s').format(
        date=sql.Identifier("date"))
    cursor.execute(sqlquery, (date,))
    data = cursor.fetchone()
    return True if data else False


def insertWork(_class: str, section: str, hw: list, cw: list):
    _date = datetime.datetime.now().strftime('%Y-%m-%d')
    # TODO Add this line in deployment
    # if not checkOnDayWork(_date):
    sqlquery = sql.SQL(
        'insert into work ({id},{date},{hw},{cw},{_class},{section}) values (%s,%s,%s,%s,%s,%s)').format(
            id=sql.Identifier("id"),
            date=sql.Identifier("date"),
            _class=sql.Identifier("class"),
            hw=sql.Identifier('hw'),
            cw=sql.Identifier("cw"),
            section=sql.Identifier("section")
    )
    cursor.execute(sqlquery, (idGenerator(), _date,
                              dumps({"hw": hw}), dumps({"cw": cw}), _class, section.upper()))
    db.commit()
    return True
    # TODO and this line
    # else:
    #     return False


def getCredential(gr):
    sqlquery = sql.SQL(
        'select *from students where {gr} = %s').format(gr=sql.Identifier("gr"))
    cursor.execute(sqlquery, (gr,))
    data = cursor.fetchone()
    return {'name': data[1], 'class': data[2], 'section': data[3]} if data else False


def authStudent(gr):
    sqlquery = sql.SQL('select {grNo} from students where {grNo} = %s').format(
        grNo=sql.Identifier("gr"))
    cursor.execute(sqlquery, (gr,))
    data = cursor.fetchone()
    return data[0] if data else False


def authTeacher(email, password):
    sqlquery = sql.SQL('select * from teachers where {email} = %s and {password} = %s').format(
        email=sql.Identifier("email"), password=sql.Identifier("password"))
    cursor.execute(sqlquery,(email,password))
    data = cursor.fetchone()
    return {'auth':True} if data else False

def getTeacherCredential(email:str):
    sqlquery = sql.SQL('select * from teachers where {email} = %s').format(email = sql.Identifier("email"))
    cursor.execute(sqlquery,(email,))
    data = cursor.fetchone()
    return {"email":data[0],'name':data[1],"class":data[2],"section":data[3]} if data else False

def newTeacher(email:str,password:str,section:str,_class:str,name:str):
    sqlquery = sql.SQL('insert into newteachers ({email},{password},{name},{section},{_class} values (%s,%s,%s,%s,%s))').format(
        email = sql.Identifier("email"),
        password = sql.Identifier("password"),
        name = sql.Identifier("name"),
        section = sql.Identifier("section"),
        _class = sql.Identifier("class")
    )
    cursor.execute(sqlquery,(email,password,name,section,_class))
    db.commit()

