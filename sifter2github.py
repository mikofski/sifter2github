import time
import requests
import json
from sifter_py import account

class SifterIssues(object):
    """
    Loads issues using sifter_py and Sifter API
    """
    def __init__(self, host, token, project):
        print "Loading issues from Sifter project ", project, "...",
        _account = account.Account(host, token)
        _projects = _account.projects()
        proj_names = [p.name for p in _projects]
        _project = _projects[proj_names.index(project)]
        self.issues = _project.issues()
        self.comments = [_issue.comments() for _issue in self.issues]
        self.milestones = _project.milestones()
        self.users = _project.people()
        print len(self.issues), "issues loaded."


class GithubRepo(object):
    """
    Establishes connection to Github repo
    using py-github
    """
    def __init__(self, username, pwd, repo, org=None):
        self.user = username
        if not org:
            self.org = username
        else:
            self.org = org
        self.url = 'https://api.github.com'
        self.pswd = pwd
        self.repo = repo


def import_issues(gh, sifter):
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

def sifter2github(path_to_csv, username, token, repository, version, org):
    from import_from_csv import SifterIssues, GithubRepo, import_issues
    s = SifterIssues(path_to_csv)
    g = GithubRepo(username, token, repository, version, org)
    
    import_issues(g, s)
    return 0

if __name__ == '__main__':
    import sys
    #sifter2github(*sys.argv[1:]) # sys.argv[0] is the module name

    if len(sys.argv[1:]) == 0:
        try:
            import inputs
        except Exception:
            print "You must include inputs.py containing Sifter and Github settings"
        from_file = True
    elif len(sys.argv[1:]) < 6:
        raise Exception("Not enough inputs")
    else:
        from_file = False

    SIFTER_HOST = inputs.SIFTER_HOST if from_file else sys.argv[1]
    SIFTER_TOKEN = inputs.SIFTER_TOKEN if from_file else sys.argv[2]
    SIFTER_PROJECT = inputs.SIFTER_PROJECT if from_file else sys.argv[3]
    GITHUB_USER = inputs.GITHUB_USER if from_file else sys.argv[4]
    GITHUB_PWD = inputs.GITHUB_PWD if from_file else sys.argv[5]
    GITHUB_REPO = inputs.GITHUB_REPO if from_file else sys.argv[6]
    if from_file:
        GITHUB_ORG = inputs.GITHUB_ORG
    elif len(sys.argv) > 7:
        GITHUB_ORG = sys.argv[7]
    else:
        GITHUB_ORG = None

    # print "Sifter host is: ", SIFTER_HOST
    # print "Sifter token is: ", SIFTER_TOKEN
    # print "Sifter project is: ", SIFTER_PROJECT
    # print "Github user is: ", GITHUB_USER
    # print "Github password is: ", GITHUB_PWD
    # print "Github repo is: ", GITHUB_REPO
    # print "Github org is: ", GITHUB_ORG

    s = SifterIssues(SIFTER_HOST, SIFTER_TOKEN, SIFTER_PROJECT)
    g = GithubRepo(GITHUB_USER, GITHUB_PWD, GITHUB_REPO, GITHUB_ORG)

