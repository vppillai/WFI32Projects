import requests,json,shutil,os

#get all repo names
orgName='MicrochipTech'
page=True
pageNum=0
repoDict=[]

print("Fetching repo names")

while page:
    reposJson=json.loads(requests.get(f"https://api.github.com/orgs/{orgName}/repos?per_page=100&page={pageNum}", headers={"Authorization":"token fa7b7a8af85cfb0bc0cd993a828635734864e289"}).text)
    if len(reposJson):
        for repo in reposJson:
            try:
                repoDict.append({"name":repo["name"],"description":repo["description"],"html_url":repo["html_url"],})
            except Exception as e:
                print(e)
                print("ERROR!! Error processing repo list\n\n")
                print(reposJson)
                input("eenter")
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
for repo in repoDict:
    repoTopics=json.loads(requests.get(f'https://api.github.com/repos/{orgName}/{repo["name"]}/topics', headers={"Accept":"application/vnd.github.mercy-preview+json","Authorization":"token fa7b7a8af85cfb0bc0cd993a828635734864e289"}).text)
    if len(repoTopics):
        try:
            if(len(repoTopics["names"])):
                for repoTopic in repoTopics["names"]:
                    if repoTopic in topicsFilter:
                        #create table header
                        fileName=os.path.join(".","docs",repoTopic+".md")
                        if not os.path.exists(fileName):
                            file = open(fileName, "w")
                            file.write(f'|**Project**|**Description**|'+'\n')    
                            file.write(f'|---|---|'+'\n')    
                        else:
                            file = open(fileName, "a")
                        file.write(f'[{repo["name"]}]({repo["html_url"]}) | {repo["description"]}'+'\n')
                        file.close()
        except Exception as e:
            print(e)
            print("ERROR!! Error processing repo Topics")
            exit(-2)