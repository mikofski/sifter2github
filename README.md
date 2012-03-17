A simple tool for migrating issues from Sifter to Github.

## Requirements ##

[py-github](https://github.com/dustin/py-github)

## Usage ##

 1. Download issues from Sifter as CSV
 2. Edit fields in settings.py to specify
 2. Run the following:


```
from import_from_csv import *

s = SifterIssues('path/to/csv')
g = GithubRepo(username, token, repository)
import_issues(g, s)
```