import requests
r=requests.get("https://api.github.com/repos/MicrochipTech/PIC32MZW1_Workshop/topics", headers={"Accept":"application/vnd.github.mercy-preview+json"})
file = open("tags.json", "w")
file.write(r.text)