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
  $ python sifter2github.py SIFTER_HOST SIFTER_TOKEN SIFTER_PROJECT GITHUB_USER GITHUB_PWD GITHUB_REPO GITHUB_ORG

Option 2: Inputs in inputs.py
-----------------------------

- Edit `inputs.py` with the appropriate inputs
- Run::

  $ python sifter2github.py

Inputs
======

- SIFTER_HOST: Sifter account/company
- SIFTER_TOKEN: Sifter API token
- SIFTER_PROJECT: Sifter project to migrate issues from
- GITHUB_USER: Github username used in calls to Github API. If a username match is not found from Sifter, this username will be set add the issue adder/owner
- GITHUB_PWD: Password for above account
- GITHUB_REPO: Github repository to receive the issues from Sifter
- GITHUB_ORG: Organization that owns the destination repository (Optional)