import requests,json,shutil,os,sys,time,glob,datetime

#get all repo names
orgName='MicrochipTech'
page=True
pageNum=0
repoDict=[]

if len(sys.argv) >=2:
    token=sys.argv[1]
else :
    token=""

print("Fetching repo names")

while page:
    time.sleep(1) #ratelimit
    reposJson=json.loads(requests.get(f'https://api.github.com/orgs/{orgName}/repos?per_page=100&page={pageNum}', headers={"Authorization": f'token {token}'}).text)
    if len(reposJson):
        for repo in reposJson:
            try:
                repoDict.append({"name":repo["name"],"description":repo["description"],"html_url":repo["html_url"]})
            except Exception as e:
                print(e)
                print("ERROR!! Error processing repo list\n\n")
                print(reposJson)
                exit(-1)
        pageNum=pageNum+1
    else:
        page=False


#get all topics to filter for
with open('topics.txt') as f:
    topicsFilter = f.read().splitlines()

#prepare the output folder
try:
    shutil.rmtree(os.path.join(".","docs"))
except:
    pass
os.mkdir(os.path.join(".","docs"))

print("Fetching repo topics")

#get all topics in repos and filter
file=open(os.path.join(".","docs","readme.md"),"w")
file.write(f'## Project topics in {orgName}'+'\n\n')    
for topic in topicsFilter:
    file.write(f'### [{topic}]({topic})' +'\n')

for repo in repoDict:
    time.sleep(1) #ratelimit
    repoTopics=json.loads(requests.get(f'https://api.github.com/repos/{orgName}/{repo["name"]}/topics', headers={"Accept":"application/vnd.github.mercy-preview+json","Authorization":f"token {token}"}).text)
    if len(repoTopics):
        try:
            if(len(repoTopics["names"])):
                for repoTopic in repoTopics["names"]:
                    if repoTopic in topicsFilter:
                        #create table header
                        fileName=os.path.join(".","docs",repoTopic+".md")
                        if not os.path.exists(fileName):
                            file = open(fileName, "w")
                            file.write(f'### Projects under topic {repoTopic} under {orgName}'+'\n\n')    
                            file.write(f'|**Project**|**Description**|**Latest Release**|'+'\n')    
                            file.write(f'|---|---|'+'\n')    
                        else:
                            file = open(fileName, "a")
                        release=json.loads(requests.get(f'https://api.github.com/repos/{orgName}/{repo["name"]}/releases', headers={"Authorization":f"token {token}"}).text)[0]
                        relStr=""
                        if "tag_name" in release.keys():
                            relStr=f'[{release["tag_name"]}]({release["html_url"]})'
                        file.write(f'[{repo["name"]}]({repo["html_url"]}) | {repo["description"]} | {relStr}'+'\n')
                        file.close()
        except Exception as e:
            print(e)
            print("ERROR!! Error processing repo Topics")
            exit(-2)

#attach timestamp. will cause a force commit.
current_utc = datetime.datetime.utcnow()
for filename in glob.glob(os.path.join('docs', '*.md')):
   with open(os.path.join(os.getcwd(), filename), 'a') as f:
      f.write('\n\n'+f'*Generated on UTC {current_utc}*'+'\n')

