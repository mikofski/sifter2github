import requests, json

class Sifter(Object):
    def __init__(self, domain, accessKey):
        sifterURL = 'https://'+domain+'.sifterapp.com/api/projects'
        r = requests.get(sifterURL,
                         headers={'X-Sifter-Token':accessKey,
                         'Accept':'application/json'})
        projects = json.loads(r.content);
        for p in projects:
            
