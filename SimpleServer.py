import socket
from time import time
TIME_INTERVAL=0.2

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 8089))
server.listen(1)

while True:
    conn, addr = server.accept()
    x=conn.recv(9)
    print(x)
    while True:
        t= time()
        while time()-t<TIME_INTERVAL:
            pass
        t= time()
        angle=180
        light=1
        should_continue=0
        conn.sendall(str(angle).encode('utf-8'))
        
        
        # 1st digit-->boolean
        # 2nd digit-->continue receiving
        txt=str(light)+str(should_continue)
        conn.sendall(txt.encode('utf-8'))
        

        if should_continue:
            angle=66            
            light=0
            
            conn.sendall(str(angle).encode('utf-8'))
            conn.sendall(str(light).encode('utf-8'))
            
        dt=time()-t
        print(dt*1000)
    
server.close()