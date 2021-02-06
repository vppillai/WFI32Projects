import requests,json,shutil,os,sys,time,glob,datetime

#get all repo names
orgName='MicrochipTech'
page=True

if len(sys.argv) >=2:
    token=sys.argv[1]
else :
    token=""

#get all topics to filter for
with open('topics.txt') as f:
    topicsFilter = f.read().splitlines()

#prepare the output folder
try:
    shutil.rmtree(os.path.join(".","docs"))
except:
    pass
os.mkdir(os.path.join(".","docs"))

for topic in topicsFilter:
    if len(topic)<2:
        continue
    print(f'processing topic : {topic}')
    repoDict=[]
    pageNum=0
    page= True
    while page: #more pages to fetch
        time.sleep(0.1) #ratelimit
        searchResult=json.loads(requests.get(f'https://api.github.com/search/repositories?q=topic:{topic}+org:{orgName}&per_page=100&page={pageNum}', headers={"Authorization": f'token {token}'}).text)
        reposJson=searchResult["items"]
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
        if not searchResult["incomplete_results"]:
            page=False
        
        #create table header
        fileName=os.path.join(".","docs",topic+".md")
        if not os.path.exists(fileName): #prepare the table header
            file = open(fileName, "a")
            file.write(f'### Projects under topic *"{topic}"* in {orgName}'+'\n\n')    
            file.write(f'|**Project**|**Description**|**Latest Release**|'+'\n')    
            file.write(f'|---|---|'+'\n')    
        else:
            file = open(fileName, "a")

        #write data to file
        for repo in repoDict:
            time.sleep(0.1) #ratelimit
            relStr=""
            release=json.loads(requests.get(f'https://api.github.com/repos/{orgName}/{repo["name"]}/releases', headers={"Authorization":f"token {token}"}).text)
            if len(release):         #not every repo will have a release              
                latestRel=release[0] #take the latest release
                if "tag_name" in latestRel.keys(): #just a Defensive check
                    relStr=f'[{latestRel["tag_name"]}]({latestRel["html_url"]})'
            file.write(f'[{repo["name"]}]({repo["html_url"]}) | {repo["description"]} | {relStr}'+'\n')
        file.close()

#attach timestamp. will cause a force commit.
current_utc = datetime.datetime.utcnow()
for filename in glob.glob(os.path.join('docs', '*.md')):
   with open(os.path.join(os.getcwd(), filename), 'a') as f:
      f.write('\n\n'+f'<sub><i>Generated on UTC {current_utc}</i></sub>'+'\n')
