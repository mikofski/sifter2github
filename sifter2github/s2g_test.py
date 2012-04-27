# -*- coding: utf-8 -*-
"""
Created on Mon Apr 02 11:03:37 2012

@author: mmikofski
"""

from import_from_csv import SifterIssues, GithubRepo, import_issues
path_to_csv = {'host': 'sunpower',
               'token': '5f014e1037370992f43a3cd0739955a7',
               'project': 'PVLife'}
s = SifterIssues(path_to_csv)
print 'sifter loaded'
g = GithubRepo('mikofski', 'Oscar6months', 'PVLife', 3, 'SunPower')
import_issues(g, s)