from github import github
import csv
import time
from sifter import Sifter
import requests, json

class SifterIssues(object):
    """
    Loads issues from CSV
    Use Sifter's 'Download as CSV' feature to save a file
    """
    def __init__(self, path_to_csv):
        if type(path_to_csv) == str:
            issues = []
            sifter = csv.DictReader(open(path_to_csv,'r'))
            for row in sifter:
                row['Number'] = int(row['Number'])
                issues.append(row)
            self.issues = sorted(issues,key=lambda k: k['Number'])
        elif type(path_to_csv) in set([list,tuple]) and len(path_to_csv) == 3:
            self.issues = Sifter(*path_to_csv)
        elif type(path_to_csv) == dict and len(path_to_csv) == 3:
            self.issues = Sifter(**path_to_csv)

class GithubRepo(object):
    """
    Establishes connection to Github repo
    using py-github
    """
    def __init__(self, username, token, repo, version=2, org=None):
        self.user = username
        if not org:
            self.org = username
        else:
            self.org = org
        if version==2:
            self.account = github.GitHub(username, token)
        elif version==3:
            self.url = 'https://api.github.com'
            self.pswd = token
        self.repo = repo


def import_issues(gh, sifter):
    if type(sifter) == SifterIssues:
        for i in sifter.issues:
            print "Importing sifter issue #", i['Number'],"...",
            subject = i['Subject'].replace("\\","_").replace("'","-").replace("\"","-").replace("/","-").replace(":","-").replace(",","-")
            descr = i['Description'].replace("\\","_").replace("'","-").replace("\"","-").replace("/","-").replace(":","-").replace(",","-")
            descr = "---Migrated from Sifter - Sifter issue " + str(i['Number']) + "---\n" + descr
            milestone = i['Milestone'].replace("\\","_").replace("'","-").replace("\"","-").replace("/","-").replace(":","-").replace(",","-")
            category = i['Category'].replace("\\","_").replace("'","-").replace("\"","-").replace("/","-").replace(":","-").replace(",","-")
            new_issue = gh.account.issues.new(gh.user, gh.repo, subject, descr)
            if milestone:
                gh.account.issues.add_label(gh.user, gh.repo, new_issue.number, milestone)
            if category:
                gh.account.issues.add_label(gh.user, gh.repo, new_issue.number, category)
            if i['Status'] == "Closed" or i['Status'] == "Resolved":
                gh.account.issues.close(gh.user, gh.repo, new_issue.number)
            print "done. Github issue #", new_issue.number
            time.sleep(2)
    elif type(sifter) == Sifter:
        for i in sifter.issues:
            print "Importing sifter issue #", i.number,"...",
            prev_miles = {}
            if i.milestone_name:
                if not i.milestone_name in set(prev_miles.keys()):
                    mile_ind = sifter.milestones.index(i.milestone_name)
                    due_on = sifter.milestones[mile_ind].due_date
                    endpoint = '/repos/' + gh.org + '/' + gh.repo + '/milestones'
                    data = json.dumps({'title':i.milestone_name,'due_on':due_on})
                    response = requests.post(gh.url + endpoint,data,auth=(gh.user,gh.pswd))
                    raw_json = json.loads(response.content)
                    mile_num = raw_json['number']
                    prev_miles.update({i.milestone_name:mile_num})
                else:
                    mile_num = prev_miles.get(i.milestone_name)
            else:
                mile_num = None
            endpoint = '/repos/' + gh.org + '/' + gh.repo + '/issues'
            body = "---Migrated from Sifter - Sifter issue " + str(i.number) + "---\n"
            body = body + i.description
            data = {'title':i.subject,
                    'body':body,
                    'assignee':i.assignee_name,
                    'milestone':mile_num,
                    'labels':i.category_name}
            response = requests.post(gh.url + endpoint,data,auth=(gh.user,gh.pswd))
            
            category = i.category_name.replace("\\","_").replace("'","-").replace("\"","-").replace("/","-").replace(":","-").replace(",","-")
            new_issue = gh.account.issues.new(gh.user, gh.repo, subject, descr)
            if milestone:
                gh.account.issues.add_label(gh.user, gh.repo, new_issue.number, milestone)
            if category:
                gh.account.issues.add_label(gh.user, gh.repo, new_issue.number, category)
            if i.status == "Closed" or i.status == "Resolved":
                gh.account.issues.close(gh.user, gh.repo, new_issue.number)
            print "done. Github issue #", new_issue.number
            time.sleep(2)