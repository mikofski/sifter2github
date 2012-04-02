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
            self.src = 'csv'
        elif type(path_to_csv) in set([list,tuple]) and len(path_to_csv) == 3:
            _sifter = Sifter(*path_to_csv)
            self.issues = _sifter.issues
            self.milestones = _sifter.milestones
            self.comments = _sifter.comments
            self.src = 'api'
        elif type(path_to_csv) == dict and len(path_to_csv) == 3:
            _sifter = Sifter(**path_to_csv)
            self.issues = _sifter.issues
            self.milestones = _sifter.milestones
            self.comments = _sifter.comments
            self.src = 'api'

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
    if sifter.src == 'csv':
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
    elif sifter.src == 'api':
        n = 0 # issue counter
        milestones = [milestone.name for milestone in sifter.milestones]
        endpoint = '/repos/' + gh.org + '/' + gh.repo + '/milestones'
        response = requests.get(gh.url + endpoint,auth=(gh.user,gh.pswd))
        raw_json = json.loads(response.content)
        gh_mile_name = [milestone.title for milestone in raw_json]
        gh_mile_num = [milestone.number for milestone in raw_json]
        for i in sifter.issues:
            print "Importing sifter issue #", i.number,"...",
            prev_miles = {}
            if i.milestone_name:
                if i.milestone_name in set(gh_mile_name):
                    mile_num = gh_mile_num(gh_mile_name.index(i.milestone_name))
                elif not i.milestone_name in set(prev_miles.keys()):
                    mile_ind = milestones.index(i.milestone_name)
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
            data = json.dumps({'title':i.subject,
                               'body':body,
                               'assignee':i.assignee_name,
                               'milestone':mile_num,
                               'labels':[i.category_name]})
            print data
            response = requests.post(gh.url + endpoint,data,auth=(gh.user,gh.pswd))
            print response.status_code
            raw_json = json.loads(response.content)
            iss_num = raw_json['number']
            if i.status == "Closed" or i.status == "Resolved":
                endpoint = '/repos/' + gh.org + '/' + gh.repo + '/issues' + str(iss_num)
                data = json.dumps({'state':'closed'})
                response = requests.post(gh.url + endpoint,data,auth=(gh.user,gh.pswd))
            if i.comment_count>0:
                endpoint = '/repos/' + gh.org + '/' + gh.repo + '/issues' + str(iss_num) + '/comments'
                for c in sifter.comments[n]:
                    json_raw = json.loads(sifter.comments[n])
                    body = json_raw['body']
                    data = json.dumps({'body':body})
                    response = requests.post(gh.url + endpoint,data,auth=(gh.user,gh.pswd))
                n += 1
            print "done. Github issue #", new_issue.number
            time.sleep(2)