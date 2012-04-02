import account


class Sifter(object):
    """
    Reads issues from Sifter using sifterapi
    """
    def __init__(self, host, token, project):
        _account = account.Account(host, token)
        _projects = _account.projects()
        proj_names = [p.name for p in _projects]
        _project = _projects[proj_names.index(project)]
        self.issues = _project.issues()
        self.comments = [_issue.comments() for _issue in self.issues]
        self.milestones = _project.milestones()
