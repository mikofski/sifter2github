from sifter_python import account
from py_github.github import github

class Sifter2Github(object):

	def __init__(self,sifter_host,sifter_key,github_user,github_token):
		self.sifter = account.Account(sifter_host,sifter_key)
		self.github = github.GitHub(github_user,github_token)
		self.github_user = github_user
	
	def get_sifter_project(self,sifter_project):
		all_projects = self.sifter.projects()
		for p in all_projects:
			if p.name == sifter_project:
				break
		return p
	
	def get_github_num_issues(self,github_repo):
		return len(self.github.issues.list(self.github_user,github_repo))
	
	def migrate_one_issue(self,sifter_project,github_repo,issue_num):
		p = self.get_sifter_project(sifter_project)
		issues = p.issues()
		self.github.issues.new(self.github_user,github_repo,issues[issue_num].subject,issues[issue_num].description)
		self.github.issues.add_label(self.github_user,github_repo,self.get_github_num_issues(github_repo)+1,issues[issue_num].category_name)
		self.github.issues.add_label(self.github_user,github_repo,self.get_github_num_issues(github_repo)+1,"M:"+issues[issue_num].milestone_name)
		if issues[issue_num].status == "Closed":
			self.github.issues.close(self.github_user,github_repo, self.get_github_num_issues(github_repo)+1)


	def migrate_all_issues(self,sifter_project,github_repo):
		issues = p.issues()
		for i in issues:
			print i.subject
		
