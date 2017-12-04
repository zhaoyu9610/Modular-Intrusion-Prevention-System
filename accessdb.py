import sqlite3, tools, datetime

def getConnection():
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    return conn, c

def getBlackList():
    conn, c = getConnection()
    c.execute('select ip from IPs')
    result = c.fetchall()
    c.close()
    conn.close()
    a = []
    for row in result:
        a.append(row[0])
    return a

def add(li):
    conn, c = getConnection()
    x, y, z = getxyz()
    temp = datetime.datetime.now() + datetime.timedelta(minutes=z)
    for ip in li:
        c.execute('select count(*) from IPs where ip=?', (ip,))
        if(c.fetchall()[0][0] == 0):
            tools.addRule(ip)
            c.execute("insert into IPs(ip, disabledtime) values(?, ?)", (ip, temp))
    conn.commit()
    c.close()
    conn.close()

def remove(li):
    conn, c = getConnection()
    for ip in li:
        c.execute('select count(*) from IPs where ip=?', (ip,))
        if(c.fetchall()[0][0] == 1):
            tools.deleteRule(ip)
            c.execute('delete from IPs where ip = ?', (ip,))
            c.execute('delete from Logs where ip = ?', (ip,))
    conn.commit()
    c.close()
    conn.close()


def getxyz():
    conn, c = getConnection()
    c.execute('select x, y, z from Rules;')
    x, y, z = c.fetchall()[0]
    c.close()
    conn.close()
    return x, y, z

def updatexyz(x, y, z):
    conn, c = getConnection()
    c.execute("update Rules set x = ?, y = ?, z = ?", (x, y, z))
    conn.commit()
    c.close()
    conn.close()
    
