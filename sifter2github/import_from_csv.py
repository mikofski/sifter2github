from github import github
import csv
import time
from sifter import Sifter

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
    def __init__(self, username, token, repo):
        self.user = username
        self.account = github.GitHub(username, token)
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
            subject = i.subject.replace("\\","_").replace("'","-").replace("\"","-").replace("/","-").replace(":","-").replace(",","-")
            descr = i.description.replace("\\","_").replace("'","-").replace("\"","-").replace("/","-").replace(":","-").replace(",","-")
            descr = "---Migrated from Sifter - Sifter issue " + str(i.number) + "---\n" + descr
            milestone = i.milestone_name.replace("\\","_").replace("'","-").replace("\"","-").replace("/","-").replace(":","-").replace(",","-")
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