import os

def findLine(ip):
    ip_l = searchLine(ip)
    if(ip_l == -1):
        return -1
    else:
         return ip_l - searchLine('INPUT') - 1

def searchLine(s):
    result = os.popen('sudo iptables -L -n -v | grep -n ' + s).read()
    if(len(result) == 0):
        return -1
    return int(result[0])

def deleteRule(ip):
    ip_l = findLine(ip)
    print(ip_l)
    if(ip_l > 0):
        result = os.popen('sudo iptables -D INPUT ' + str(ip_l))

def addRule(ip):
    os.popen('sudo iptables -I INPUT -s ' + ip + ' -j DROP')
