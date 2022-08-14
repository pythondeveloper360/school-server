import os
import random
from datetime import datetime
from json import dumps

from psycopg2 import connect, sql

# Server
db = connect(
    port=os.environ.get('port'),
    host=os.environ.get('host'),
    user=os.environ.get('user'),
    database=os.environ.get('database'),
    password=os.environ.get('password')
)
cursor = db.cursor()

alphabet = [*[chr(i) for i in range(97, 123)], *[chr(i)
                                                 for i in range(65, 91)], *[chr(i) for i in range(48, 58)]]


def idGenerator(_range: int = 10):
    random.shuffle(alphabet)
    return ''.join(alphabet[0:int(_range)])


def getAllWork(_class: str, section: str):
    sqlquery = sql.SQL('select {id},{date} from work where {_class} = %s and {section} = %s order by {date} DESC').format(
        _class=sql.Identifier("class"),
        section=sql.Identifier("section"),
        id=sql.Identifier("id"),
        date=sql.Identifier("date")
    )

    cursor.execute(sqlquery, (_class, section))
    data = cursor.fetchall()
    return [{"id": i[0], "date":i[1]} for i in data] if data else False


def getAllWorkStudent(gr):
    rData = []
    cre = getCredential(gr=gr)
    if cre:
        sqlquery = sql.SQL('select {id},{date},{seenBy} from work where {_class} = %s and {section} = %s order by {date} DESC').format(
            _class=sql.Identifier("class"),
            section=sql.Identifier("section"),
            id=sql.Identifier("id"),
            seenBy=sql.Identifier("seenby"),
            date=sql.Identifier("date")
        )

        cursor.execute(sqlquery, (cre['class'], cre['section']))
        data = cursor.fetchall()
        if data:
            for i in data:
                rData.append({"id": i[0], "date": i[1], "seen": checkSeenBy(
                    seenBy=i[2], gr=gr), 'section': cre.get('section'), 'class': cre.get('class')})
            return rData
        else:
            return False
    else:
        return False


def checkSeenBy(gr: str, seenBy: list = []):
    if seenBy:
        for item in seenBy:
            if item['gr'] == gr:
                return True
    return False


def getWorkWithId(_id: str, gr=None):
    sqlquery = sql.SQL(
        'select {_id},{date},{works} from work where {_id} = %s').format(
            _id=sql.Identifier("id"),
            date=sql.Identifier("date"),
            works=sql.Identifier("works"),
            time=sql.Identifier("time"))
    cursor.execute(sqlquery, (_id,))
    data = cursor.fetchone()
    if gr:
        seenWork(_id, gr)
    return {'id': data[0], 'date': data[1], 'work': data[2]} if data else False


def checkOnDayWork(_class, section, date):
    _date = datetime.strptime(date, '%a %b %d %Y')
    sqlquery = sql.SQL('select id from work where {date} = %s and {_class} = %s and {section} = %s').format(
        date=sql.Identifier("date"),
        _class=sql.Identifier("class"),
        section=sql.Identifier("section"))
    cursor.execute(sqlquery, (_date.strftime('%Y-%m-%d'), _class, section))
    data = cursor.fetchone()
    return True if data else False


def getParentList(_class: str, section: str):
    destiny = f"{_class}-{section}"
    rData = []
    sqlquery = sql.SQL('select phone from parents where %s = any(classes)')
    cursor.execute(sqlquery, (destiny,))
    data = cursor.fetchall()
    if data:
        for i in data:
            rData.append(i[0])
    return rData


def insertWork(_class: str, section: str, work: dict, date):
    _id = idGenerator()
    _date = datetime.strptime(date, "%a %b %d  %Y")
    sqlquery = sql.SQL(
        'insert into work ({id},{date},{works},{_class},{section},{parents}) values (%s,%s,%s,%s,%s,%s)').format(
            id=sql.Identifier("id"),
            date=sql.Identifier("date"),
            _class=sql.Identifier("class"),
            section=sql.Identifier("section"),
            works=sql.Identifier("works"),
            parents=sql.Identifier("parents")
    )
    cursor.execute(sqlquery, (_id, _date.strftime('%Y-%m-%d'), dumps(work),
                   _class, section.upper(), getParentList(_class, section.upper())))
    db.commit()

    return {'work': True, "id": _id, 'date': date}


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
    cursor.execute(sqlquery, (email, password))
    data = cursor.fetchone()
    return {'auth': True} if data else False


def getTeacherCredential(email: str):
    sqlquery = sql.SQL(
        'select * from teachers where {email} = %s').format(email=sql.Identifier("email"))
    cursor.execute(sqlquery, (email,))
    data = cursor.fetchone()
    return {"email": data[0], 'name': data[1], "class": data[2], "section": data[3]} if data else False


def authParent(phone):
    sqlquery = sql.SQL(
        'select {phone} from parents where {phone}  = %s').format(phone=sql.Identifier("phone"))
    cursor.execute(sqlquery, (phone,))
    data = cursor.fetchall()
    return True if data else False


def getAllWorkForParent(phone):
    sqlquery = sql.SQL('select {id},{date},{_class},{section} from work where %s = any(parents) order by {date} DESC').format(
        id=sql.Identifier("id"),
        date=sql.Identifier("date"),
        _class=sql.Identifier("class"),
        section=sql.Identifier("section")
    )
    cursor.execute(sqlquery, (phone,))
    data = cursor.fetchall()
    rList = [{'id': i[0], 'date':i[1], 'class':i[2], "section":i[3]}
             for i in data]
    return rList


def seenByStudents(id):
    sqlquery = sql.SQL('select {seenBy} from work where id = %s').format(
        seenBy=sql.Identifier("seenby")
    )
    cursor.execute(sqlquery, (id,))
    data = cursor.fetchone()
    return data[0] if data[0] else []


def seenWork(id, by):
    sqlquery = sql.SQL('select {seenBy} from work where {id} = %s').format(
        seenBy=sql.Identifier("seenby"), id=sql.Identifier("id"))
    cursor.execute(sqlquery, (id,))
    data = cursor.fetchone()
    data = data[0] if data[0] else []
    studentCredentials = getCredential(by)
    if studentCredentials:
        for x in data:
            if x['gr'] == by:
                return True
        data.append({"name": studentCredentials['name'], 'gr': by})
        sqlquery = sql.SQL('update work set {seenBy} = %s where {id} = %s').format(
            seenBy=sql.Identifier("seenby"), id=sql.Identifier("id"))
        cursor.execute(sqlquery, (dumps(data), id))
        db.commit()
        return True
    else:
        return False
    # data.append(by)


def reportBug(by, bug, credential, date):
    _id = idGenerator()
    _date = datetime.strptime(date, '%a %b %d  %Y')
    if by == 'teacher':
        email = credential.get('email')
        sqlquery = sql.SQL('insert into bugs ({id},{by},{credential},{date},{bug} values (%s,%s,%s,%s,%s))').format(
            id=sql.Identifier("id"),
            by=sql.Identifier("by"),
            credential=sql.Identifier("credential"),
            date=sql.Identifier("date"),
            bug=sql.Identifier("bug")
        )
        cursor.execute(sqlquery, (_id, by, email, _date, bug))
        db.commit()
        return True
    elif by == 'parent':
        phone = credential.get('phone')
        sqlquery = sql.SQL('insert into bugs ({id},{by},{credential},{date},{bug} values (%s,%s,%s,%s,%s))').format(
            id=sql.Identifier("id"),
            by=sql.Identifier("by"),
            credential=sql.Identifier("credential"),
            date=sql.Identifier("date"),
            bug=sql.Identifier("bug")
        )
        cursor.execute(sqlquery, (_id, by, phone, _date, bug))
        db.commit()
        return True

    elif by == 'student':
        gr = credential.get('gr')
        sqlquery = sql.SQL('insert into bugs ({id},{by},{credential},{date},{bug} values (%s,%s,%s,%s,%s))').format(
            id=sql.Identifier("id"),
            by=sql.Identifier("by"),
            credential=sql.Identifier("credential"),
            date=sql.Identifier("date"),
            bug=sql.Identifier("bug")
        )
        cursor.execute(sqlquery, (_id, by, gr, _date, bug))
        db.commit()
        return True
    return False