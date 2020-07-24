# TODO security

import socket
import subprocess
import urllib.parse
import threading
import hashlib

s = socket.socket()

s.bind(("", 880))
s.listen()

def processReceived(st):
    st = urllib.parse.unquote(st).replace("BACKSLASH", "\\").replace("\\\\", "\\")
    url = st[5:st.find(" HTTP/")]
    if len(url) <= 1:
        return (False,)
    else:
        slashLoc = url.find("/")
        return (True, url[:slashLoc], url[slashLoc+1:])

def index():
    file = open("index.html", "r")
    pageText = file.read()
    file.close()
    return pageText

def getPassRequ():
    file = open("passRequ.txt", "r")
    fileText = file.read()
    file.close()
    return eval(fileText)

def testPass(password):
    (correctHash, salt) = getPassRequ()
    gen = hashlib.sha512()
    gen.update(password.encode() + salt.encode())
    return gen.hexdigest() == correctHash

def runCmdStr(password, cmdStr):
    if not testPass(password):
        return "wrong password"
    cmd = subprocess.run(["sh", "-c", cmdStr], timeout=20, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cmdOut = cmd.stdout.decode()
    cmdOut += cmd.stderr.decode()
    return cmdOut

urls = {"index": index, "cmd": runCmdStr}

def handleConnection(connection):
    try:
        rec = connection.recv(99999).decode()
        url = processReceived(rec)
        result = runCmdStr(url[1], url[2]) if url[0] else index()
        connection.send(("HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + result).encode())
    except Exception as e:
        connection.send(str(e).encode())
    connection.close()

while True:
    connection, address = s.accept()
    threading.Thread(target=handleConnection, args=(connection,)).start()
