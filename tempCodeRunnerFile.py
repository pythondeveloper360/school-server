
def AddTeachersCsv(content: str):
    lines = content.split('\n')
    rData = [(i) for i in lines]
    rData = tuple(rData)
    # args = ()
    print(rData)
f = 'w@g.com,fahad,10,D'
AddTeachersCsv(f)