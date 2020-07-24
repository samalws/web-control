# TODO security

import socket
import subprocess
import urllib.parse
import threading

s = socket.socket()

s.bind(("", 880))
s.listen()

def processReceived(st):
    st = urllib.parse.unquote(st).replace("BACKSLASH", "\\").replace("\\\\", "\\")
    url = st[5:st.find(" HTTP/")]
    slashLoc = url.find("/")
    if slashLoc == -1:
        return (url, "")
    else:
        return (url[:slashLoc], url[slashLoc+1:])

def index(_):
    file = open("index.html", "r")
    pageText = file.read()
    file.close()
    return pageText

def runCmdStr(cmdStr):
    cmd = subprocess.run(["sh", "-c", cmdStr], timeout=20, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cmdOut = cmd.stdout.decode()
    cmdOut += cmd.stderr.decode()
    return cmdOut

urls = {"index": index, "cmd": runCmdStr}

def handleConnection(connection):
    try:
        rec = connection.recv(99999).decode()
        url = processReceived(rec)
        result = urls[url[0]](url[1])
        connection.send(("HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + result).encode())
    except Exception as e:
        connection.send(str(e).encode())
    connection.close()

while True:
    connection, address = s.accept()
    threading.Thread(target=handleConnection, args=(connection,)).start()
