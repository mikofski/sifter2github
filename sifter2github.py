import csv
import time
from sifter import Sifter
import requests
import json


class SifterIssues(object):
    """
    Loads issues from CSV
    Use Sifter's 'Download as CSV' feature to save a file
    """
    def __init__(self, path_to_csv):
        if type(path_to_csv) == str:
            issues = []
            sifter = csv.DictReader(open(path_to_csv, 'r'))
            for row in sifter:
                row['Number'] = int(row['Number'])
                issues.append(row)
            self.issues = sorted(issues, key=lambda k: k['Number'])
            self.src = 'csv'
        elif len(path_to_csv) == 3:
            if type(path_to_csv) in [list, tuple]:
                _sifter = Sifter(*path_to_csv)
            elif type(path_to_csv) == dict:
                _sifter = Sifter(**path_to_csv)
            self.issues = _sifter.issues
            self.milestones = _sifter.milestones
            self.comments = _sifter.comments
            self.users = _sifter.users
            self.src = 'api'


class GithubRepo(object):
    """
    Establishes connection to Github repo
    using py-github
    """
    def __init__(self, username, token, repo, org=None):
        self.user = username
        if not org:
            self.org = username
        else:
            self.org = org
        self.url = 'https://api.github.com'
        self.pswd = token
        self.repo = repo


def import_issues(gh, sifter):
    if sifter.src == 'csv':
        for i in sifter.issues:
            print "Importing sifter issue #", i['Number'], "...",
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
        n = 0  # issue counter
        # make a list of Sifter milestones and user email addresses
        milestones = [milestone.name.lower() for milestone in sifter.milestones]
        sifter_members = [_member.first_name + ' ' + _member.last_name for _member in sifter.users]
        # Github v3 api - list of members in org
        endpoint = '/orgs/' + gh.org + '/members'
        try:
            response = requests.get(gh.url + endpoint, auth=(gh.user, gh.pswd))
            response.raise_for_status()
        except Exception as _e:
            handle_exception(_e)
        if response.status_code == requests.codes.OK:
            raw_json = json.loads(response.content)
            member_login = [member['login'] for member in raw_json]
            member_url = [member['url'] for member in raw_json]
        else:
            member_login = []
            member_url = []
            print 'HTTPError code {0!s}. {1} members not loaded from Github.'.format(response.status_code, gh.org)
        member_name = []
        for m in member_url:
            try:
                response = requests.get(m, auth=(gh.user, gh.pswd))
                response.raise_for_status()
            except Exception as _e:
                handle_exception(_e)
            if response.status_code == requests.codes.OK:
                raw_json = json.loads(response.content)
                try:
                    _member = raw_json['name']
                except KeyError as _e:
                    _member = member_login[member_url.index(m)]
                    prompt = 'Full Name for Member: {0}:'.format(_member)
                    _member = input(prompt)
            else:
                _member = None
            while not _member in sifter_members:
                print '%r not found in Sifter.', _member
                _member = member_login[member_url.index(m)]
                prompt = 'Re-enter Full Name for Member: {0} or "skip" to skip:'.format(_member)
                _member = input(prompt)
                if _member == 'skip':
                    break
            member_name.append(_member)
        members = dict(zip(member_name, member_login))
        # Github v3 api - list of open milestones
        endpoint = '/repos/' + gh.org + '/' + gh.repo + '/milestones'
        try:
            response = requests.get(gh.url + endpoint, auth=(gh.user, gh.pswd))
            response.raise_for_status()
        except Exception as _e:
            handle_exception(_e)
        if response.status_code == requests.codes.OK:
            raw_json = json.loads(response.content)
            gh_mile_name = [milestone['title'].lower() for milestone in raw_json]
            gh_mile_num = [milestone['number'] for milestone in raw_json]
        else:
            gh_mile_name = []
            gh_mile_num = []
            print 'HTTPError code {!s}. Github milestones not loaded.'.format(response.status_code)
        # Github v3 api - list of closed milestones
        endpoint = endpoint + '?state=closed'
        try:
            response = requests.get(gh.url + endpoint, auth=(gh.user, gh.pswd))
            response.raise_for_status()
        except Exception as _e:
            handle_exception(_e)
        if response.status_code == requests.codes.OK:
            raw_json = json.loads(response.content)
            gh_mile_name = gh_mile_name + [milestone['title'].lower() for milestone in raw_json]
            gh_mile_num = gh_mile_num + [milestone['number'] for milestone in raw_json]
        # Github v3 api - list of labels
        endpoint = '/repos/' + gh.org + '/' + gh.repo + '/labels'
        try:
            response = requests.get(gh.url + endpoint, auth=(gh.user, gh.pswd))
            response.raise_for_status()
        except Exception as _e:
            handle_exception(_e)
        if response.status_code == requests.codes.OK:
            raw_json = json.loads(response.content)
            gh_labels = [label['name'].lower() for label in raw_json]
        else:
            gh_labels = []
            print 'HTTPError code {!s}. Github labels not loaded.'.format(response.status_code)
        for i in sifter.issues:
            print "Importing Sifter issue #", i.number, "...",
            prev_miles = {}  # an empty dict for previous Sifter milestones
            if i.milestone_name:
                if i.milestone_name.lower() in gh_mile_name:
                    # milestone is already in Github
                    mile_num = gh_mile_num[gh_mile_name.index(i.milestone_name.lower())]
                elif not i.milestone_name.lower() in prev_miles.keys():
                    # copy milestone from Sifter to Github
                    mile_ind = milestones.index(i.milestone_name.lower())
                    due_on = sifter.milestones[mile_ind].due_date
                    # Github v3 api - create milestone
                    endpoint = '/repos/' + gh.org + '/' + gh.repo + '/milestones'
                    data = json.dumps({'title': i.milestone_name,
                                       'due_on': due_on})
                    try:
                        response = requests.post(gh.url + endpoint, data, auth=(gh.user, gh.pswd))
                        response.raise_for_status()
                    except Exception as _e:
                        handle_exception(_e)
                    if response.status_code == requests.codes.CREATED:
                        raw_json = json.loads(response.content)
                        mile_num = raw_json['number']
                    else:
                        mile_num = None
                    prev_miles.update({i.milestone_name.lower(): mile_num})
                else:
                    mile_num = prev_miles.get(i.milestone_name.lower())
            else:
                mile_num = None
            # Github v3 api - create label
            if i.category_name and not i.category_name.lower() in gh_labels:
                endpoint = '/repos/' + gh.org + '/' + gh.repo + '/labels'
                data = json.dumps({'name': i.category_name})
                try:
                    response = requests.post(gh.url + endpoint, data, auth=(gh.user, gh.pswd))
                    response.raise_for_status()
                except Exception as _e:
                    handle_exception(_e)
                gh_labels.append(i.category_name.lower())
            endpoint = '/repos/' + gh.org + '/' + gh.repo + '/issues'
            body = "---Migrated from Sifter - Sifter issue " + str(i.number) + "---\n"
            body = body + i.description
            assignee = members[i.assignee_name]
            if not assignee:
                assignee = gh.user
            data = {'title': i.subject,
                    'body': body,
                    'assignee': assignee}
            if i.category_name:
                data.update({'labels': [i.category_name]})            
            if mile_num:
                data.update({'milestone': mile_num})
            data = json.dumps(data)
            try:
                response = requests.post(gh.url + endpoint, data, auth=(gh.user, gh.pswd))
                response.raise_for_status()
            except Exception as _e:
                handle_exception(_e)
            if response.status_code == requests.codes.CREATED:
                raw_json = json.loads(response.content)
                iss_num = raw_json['number']
            else:
                iss_num = None
            if i.status == "Closed" or i.status == "Resolved":
                endpoint = '/repos/' + gh.org + '/' + gh.repo + '/issues/' + str(iss_num)
                data = json.dumps({'state': 'closed'})
                try:
                    response = requests.post(gh.url + endpoint, data, auth=(gh.user, gh.pswd))
                except Exception as _e:
                    handle_exception(_e)
            if i.comment_count > 0:
                endpoint = '/repos/' + gh.org + '/' + gh.repo + '/issues/' + str(iss_num) + '/comments'
                p = 0
                for c in sifter.comments[n]:                    
                    if p > 0 and c.body:
                        data = json.dumps({'body': c.body})
                        try:
                            response = requests.post(gh.url + endpoint, data, auth=(gh.user, gh.pswd))
                        except Exception as _e:
                            handle_exception(_e)
                    p += 1
            n += 1
            print "done. Github issue #", i.number
            time.sleep(2)


def handle_exception(_e):
    if type(_e) == requests.HTTPError:
        raise _e
    else:
        raise _e