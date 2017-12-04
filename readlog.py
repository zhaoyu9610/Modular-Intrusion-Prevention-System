import time, os, re, datetime, tools, sqlite3

conn = sqlite3.connect('test.db')
c = conn.cursor()
x, y, z = 2, 1, 1

def getRules():
    global x, y, z
    c.execute('select x, y, z from Rules;')
    x, y, z = c.fetchall()[0]

def insert(ipstr, dt, accesstype):
    c.execute('insert into Logs(ip, accesstime, accesstype) values (?, ?, ?)', (ipstr, dt, accesstype))
    conn.commit()
    if(check(ipstr)):
        print('check true')
        add(ipstr)

def check(ipstr):
    temp = '-'+str(y)+' minutes'
    c.execute("select count(*) from Logs where ip=? and accesstime > datetime('now', ?, 'localtime')", (ipstr, temp))
    xx = c.fetchall()[0][0]
    print('find ' + str(xx) + ' times')
    if xx >= x:
        return True
    return False

def add(ipstr):
    tools.addRule(ipstr)
    temp = datetime.datetime.now() + datetime.timedelta(minutes=z)
    c.execute("insert into IPs(ip, disabledtime) values(?, ?)", (ipstr, temp))
    print('add ' + ipstr + ' to black list')
    c.execute("select * from IPs where ip = ?", (ipstr,))
    print(c.fetchall())
    conn.commit()

def free():
    c.execute("select ip from IPs where disabledtime < datetime('now', 'localtime')")
    ips = c.fetchall()
    for ip in ips:
        tools.deleteRule(ip[0])
        c.execute('delete from IPs where ip = ?', (ip[0],))
        c.execute('delete from Logs where ip = ?', (ip[0],))
        print('free ', ip[0])
    conn.commit()

def blackList(ipstr):
    add(ipstr)

def main():
    try:
        c.execute('delete from IPs')
        c.execute('delete from Logs')
        conn.commit()
        
        fname1 = '/var/log/auth.log'
        fname2 = '/var/log/apache2/access.log'
        file1 = open(fname1,'r')
        file2 = open(fname2,'r')
        pattern1 = re.compile(r'(.+) vl38 sshd.+authentication failure.+(\d+\.\d+\.\d+\.\d+)')
        pattern2 = re.compile(r'(\d+\.\d+\.\d+\.\d+).+\[([a-zA-Z0-9/:]+).+401')
        st_results1 = os.stat(fname1)
        st_size1 = st_results1[6]
        file1.seek(st_size1)
        st_results2 = os.stat(fname2)
        st_size2 = st_results2[6]
        file2.seek(st_size2)
        print('init done')
        while 1:
            where1 = file1.tell()
            line1 = file1.readline()
            where2 = file2.tell()
            line2 = file2.readline()
            if not line1:
                file1.seek(where1)
            else:
                match1 = pattern1.match(line1)
                if(match1):
                    timestr1 = match1.groups()[0]
                    dt1 = datetime.datetime.strptime('2017 ' + timestr, '%Y %b %d %X')
                    ipstr1 = match1.groups()[1]
                    print("find ip: ", ipstr1)
                    insert(ipstr1, dt1, 'ssh')
            if not line2:
                file2.seek(where2)
            else:
                match2 = pattern2.match(line2)
                if(match2):
                    timestr = match2.groups()[1]
                    dt2 = datetime.datetime.strptime(timestr, '%d/%b/%Y:%X')
                    ipstr2 = match2.groups()[0]
                    print("find ip: ", ipstr2)
                    insert(ipstr2, dt2, 'https')
            free()
            getRules()
    finally:
        c.close()
        conn.close()

if __name__ == '__main__':
    main()
