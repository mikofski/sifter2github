from py_github.github import github
import csv
import time

class SifterIssues(object):
    """
    Loads issues from CSV
    Use Sifter's 'Download as CSV' feature to save a file
    """
    def __init__(self, path_to_csv):
        issues = []
        sifter = csv.DictReader(open(path_to_csv,'r'))
        for row in sifter:
            issues.append(row)
        self.issues = sorted(issues,key=lambda k: k['Number'])


class GithubRepo(object):
    """
    Establishes connection to Github repo
    using github-python
    """
    def __init__(self, username, token, repo):
        self.user = username
        self.account = github.GitHub(username, token)
        self.repo = repo

    def get_last_issue_number(self):
        return len(self.account.issues.list(self.user,self.repo))


def import_issues(gh, sifter):
    # issue number for new issue expected to be 1 plus the
    # last issue already in the repo
    i_num = gh.get_last_issue_number() + 1
    for i in sifter.issues:
        subject = i['Subject'].replace("\\","/").replace("'","-").replace("\"","-")
        descr = i['Description'].replace("\\","/").replace("'","-").replace("\"","-")
        descr = "---Migrated from Sifter - Sifter issue " + str(i['Number']) + "---\n" + descr
        milestone = i['Milestone'].replace("\\","/").replace("'","-").replace("\"","-")
        category = i['Category'].replace("\\","/").replace("'","-").replace("\"","-")
        gh.account.issues.new(gh.user, gh.repo, subject, descr)
        if milestone:
            gh.account.issues.add_label(gh.user, gh.repo, i_num, milestone)
        if category:
            gh.account.issues.add_label(gh.user, gh.repo, i_num, category)
        if i['Status'] == "Closed" or i['Status'] == "Resolved":
            gh.account.issues.close(gh.user, gh.repo, i_num)
        print "Imported Sifter issue #", i['Number']," to Github #", i_num
        i_num += 1
        time.sleep(2)


        