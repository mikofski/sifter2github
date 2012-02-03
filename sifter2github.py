from sifter_python import account
from py_github.github import github

class Sifter2Github(object):

	def __init__(self,sifter_host,sifter_key,github_user,github_token):
		self.sifter = account.Account(sifter_host,sifter_key)
		self.github = github.GitHub(github_user,github_token)
		self.github_user = github_user
		self.migrated = []
	
	def get_sifter_project(self,sifter_project):
		all_projects = self.sifter.projects()
		for p in all_projects:
			if p.name == sifter_project:
				break
		return p
	
	def load_issues(self,sifter_project):
		p = self.get_sifter_project(sifter_project)
		self.issues = p.issues()
	
	def get_github_num_issues(self,github_repo):
		return len(self.github.issues.list(self.github_user,github_repo))
	
	def show_sifter_issue(self,sifter_project,issue_num):
		p = self.get_sifter_project(sifter_project)
		issues = p.issues()
		i = issues[issue_num]
		print "Subject:", i.subject
		print "Description:", i.description
		if i.category_name:
			print "Category Name:", i.category_name
		if i.milestone_name:
			print "Milestone:", i.milestone_name
		print "Status:", i.status
		if i.status == "Closed":
			print "This issue is closed."
		print "-----------------------"
	
	def add_to_github(self,user,github_repo,subj,desc):
		g_num = self.get_github_num_issues(github_repo) + 1
		self.github.issues.new(user,github_repo,subj,desc)

		#istart = self.get_github_num_issues(github_repo) + 1
		#self.github.issues.new(self.github_user,github_repo,issues[issue_num].subject,issues[issue_num].description)
		#self.github.issues.add_label(self.github_user,github_repo,istart,issues[issue_num].category_name)
		#self.github.issues.add_label(self.github_user,github_repo,istart,"M:"+issues[issue_num].milestone_name)
		#if issues[issue_num].status == "Closed":
		#	self.github.issues.close(self.github_user,github_repo,istart)


	def migrate_all_issues(self,user,sifter_project,github_repo):
		p = self.get_sifter_project(sifter_project)
		issues = p.issues()
		g_num = self.get_github_num_issues(github_repo) + 1
		for i in issues:
			subj = i.subject.replace('.','-').replace('/','-').replace(',','-').replace("'","-")[:60]
			print "Adding:", subj
			if i.description:
				desc = i.description.replace('.','-').replace('/','-').replace(',','-')
				self.github.issues.new(user,github_repo,subj,desc)
			else:
				self.github.issues.new(user,github_repo,str(subj),str(subj))
			if i.milestone_name:
				mi = i.milestone_name.replace('.','-').replace('/','-').replace(',','-')
				self.github.issues.add_label(user,github_repo,g_num,mi)
			if i.category_name:
				cat = i.category_name.replace('.','-').replace('/','-').replace(',','-')
				self.github.issues.add_label(user,github_repo,g_num,cat)
			if i.status == "Resolved":
				self.github.issues.add_label(user,github_repo,g_num,"RESOLVED")
			elif i.status == "Closed":
				self.github.issues.close(user,github_repo,g_num)
			g_num = g_num + 1

	def migrate_five(self,user,sifter_project,github_repo):
		g_num = self.get_github_num_issues(github_repo) + 1
		count = 0
		i_num = 0
		while count < 5 and i_num < len(self.issues):
			i = self.issues[i_num]
			already_migrated = False
			for m in self.migrated:
				if m == i.number:
					already_migrated = True
					break
			if i.number not in self.migrated:
				subj = i.subject.replace('/','-')
				print "Adding:", subj,
				if i.description:
					desc = i.description.replace('/','-')
				else:
					desc = ""
				try:
					self.github.issues.new(user,github_repo,subj,desc)
					if i.milestone_name:
						mi = i.milestone_name.replace('.','-').replace('/','-').replace(',','-')
						self.github.issues.add_label(user,github_repo,g_num,mi)
					if i.category_name:
						cat = i.category_name.replace('.','-').replace('/','-').replace(',','-')
						self.github.issues.add_label(user,github_repo,g_num,cat)
					if i.status == "Resolved":
						self.github.issues.add_label(user,github_repo,g_num,"RESOLVED")
					elif i.status == "Closed":
						self.github.issues.close(user,github_repo,g_num)
					print "Success"
				except:
					print "\nCould not add", subj
				
				count = count + 1
				g_num = g_num + 1
				self.migrated.append(i.number)
			i_num = i_num + 1
			
	
	def migrate_one_issue(self,sifter_project,github_repo,issue_num):
		p = self.get_sifter_project(sifter_project)
		issues = p.issues()
		g_num = self.get_github_num_issues(github_repo) + 1
		i = issues[issue_num]
		self.github.issues.new(self.github_user,github_repo,i.subject,i.description)
		if i.milestone_name:
			self.github.issues.add_label(self.github_user,github_repo,g_num,i.milestone_name)
		if i.category_name:
			self.github.issues.add_label(self.github_user,github_repo,g_num,i.category_name.replace('/','-'))
		if i.status == "Closed":
			self.github.issues.close(self.github_user,github_repo,g_num)