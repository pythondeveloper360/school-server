import datetime
import random
from json import dumps

from psycopg2 import connect, sql
# Server
db = connect(
    host='ec2-34-204-58-13.compute-1.amazonaws.com',
    port='5432',
    user='qabfwlyhrismmv',
    database='d52fn9luqlu0bq',
    password='7bb22ef7886bc5b2bd31a2e83c28ffc3ef1bec7ea038fca50bb04d720386121d'
)
# db = connect(
#     host='localhost',
#     port='5432',
#     user='postgres',
#     database='school',
#     password='qsa-1299'
# )

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
        'select {id},{date},{hw},{cw},{time} from work where {id} = %s').format(
            id=sql.Identifier("id"),
            date=sql.Identifier("date"),
            hw=sql.Identifier("hw"),
            cw=sql.Identifier("cw"),
            time=sql.Identifier("time"))
    cursor.execute(sqlquery, (id,))
    data = cursor.fetchone()
    # print(data[1].strftime('%b %d %A'))
    return {'id': data[0], 'date': data[1].strftime('%b %d %A'), 'hw': data[2]['hw'], 'cw': data[3]['cw'], 'time': data[4].strftime('%-I:%M %p') if data[4] else ''} if data else False


def checkOnDayWork(_class,section,date = None):
    date = datetime.datetime.now() if not date else date
    t = datetime.timedelta(hours = 12)
    date = date+t
    sqlquery = sql.SQL('select id from work where {date} = %s and {_class} = %s and {section} = %s').format(
        date=sql.Identifier("date"),
        _class = sql.Identifier("class"),
        section = sql.Identifier("section"))
    cursor.execute(sqlquery, (date,_class,section))
    data = cursor.fetchone()
    return True if data else False


def insertWork(_class: str, section: str, hw: list, cw: list):
    _date = datetime.datetime.now()
    _id = idGenerator()
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
    cursor.execute(sqlquery, (_id, _date.strftime('%Y-%m-%d'),
                              dumps({"hw": hw}), dumps({"cw": cw}), _class, section.upper()))
    db.commit()
    return {'work':True,"id":_id,'date':_date.strftime('%b %d %A')}
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
    print(gr)
    return data[0] if data else False


def authTeacher(email, password):
    sqlquery = sql.SQL('select * from teachers where {email} = %s and {password} = %s').format(
        email=sql.Identifier("email"), password=sql.Identifier("password"))
    cursor.execute(sqlquery, (email, password))
    data = cursor.fetchone()
    return {'auth': True} if data else False


def getTeacherCredential(email: str):
    sqlquery = sql.SQL(
        'select * from teachers where {email} = %s').format(email=sql.Identifier("email"))
    cursor.execute(sqlquery, (email,))
    data = cursor.fetchone()
    return {"email": data[0], 'name': data[1], "class": data[2], "section": data[3]} if data else False


def newTeacher(email: str, password: str, section: str, _class: str, name: str):
    sqlquery = sql.SQL('insert into newteachers ({email},{password},{name},{section},{_class} values (%s,%s,%s,%s,%s))').format(
        email=sql.Identifier("email"),
        password=sql.Identifier("password"),
        name=sql.Identifier("name"),
        section=sql.Identifier("section"),
        _class=sql.Identifier("class")
    )
    cursor.execute(sqlquery, (email, password, name, section, _class))
    db.commit()
