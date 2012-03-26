#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       siter2github.py
#       
#       Copyright 2012 Mark Mikofski <bwanamarko@yahoo.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#       
#       



def sifter2github(path_to_csv, username, token, repository, path_to_py_github='~/Downloads/py-github'):
	from import_from_csv import *
	s = SifterIssues(path_to_csv)
	g = GithubRepo(username, token, repository)
	import_issues(g, s)
	return 0

if __name__ == '__main__':
	import sys
	sys.path.append(path_to_py_github)
    sifter2github(*sys.argv[1:]) # sys.argv[0] is the module name
