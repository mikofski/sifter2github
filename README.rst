A simple tool for migrating issues from Sifter to Github.

Requirements
============

- [sifter-python](https://github.com/bryanmikaelian/sifter-python)
- [requests](https://github.com/kennethreitz/requests)

Overview
========

Migrates issues, comments, milestones and labels from Sifter to Github. If organization is specified, sifter2github will also match usernames correponding to the issue owners and commenters.

Usage
=====

Option 1: Inputs at command line
--------------------------------

- Run the following::

  $ cd sifter2github
  $ python sifter2github.py sifter-host sifter-token sifter-project github-user github-password github-repo github-org

Option 2: Inputs in inputs.py
-----------------------------

- Edit `inputs.py` with the appropriate inputs
- Run::

  $ python sifter2github.py

Where:

- sifter-host: Sifter account/company
- sifter-token: Sifter API token
- sifter-project: Sifter project to migrate issues from
- github-user: Github username used in calls to Github API. If a username match is not found from Sifter, this username will be set add the issue adder/owner
- github-password: Password for above account
- github-repo: Github repository to receive the issues from Sifter
- github-org: Organization that owns the destination repository (Optional)