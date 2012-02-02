A simple tool for migrating issues from Sifter to Github Issues. Nowhere near complete yet.

Requirements
============

sifter-python by bryanmikaelian
py-github by dustin

Usage
=====

    from sifter2github import Sifter2Github

    m = Sifter2Github([sifter_host],[sifter_key],[github_username],[github_token])
    m.migrate_all_issues([sifter_project],[github_repo])
