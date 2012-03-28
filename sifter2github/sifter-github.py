import requests, json

class Sifter(Object):
    """
    Reads issues from Sifter using sifterapi
    """
    def __init__(self, domain, accessKey):
        sifterURL = 'https://'+domain+'.sifterapp.com/api/projects'
        r = requests.get(sifterURL,
                         headers={'X-Sifter-Token':accessKey,
                         'Accept':'application/json'})
        allProjects = json.loads(r.content);
        projects = allProjects['projects']
        for p in projects:
            
