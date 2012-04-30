A simple tool for migrating issues from Sifter to Github.

Requirements
============

- [sifter-python](https://github.com/bryanmikaelian/sifter-python)
- [requests](https://github.com/kennethreitz/requests)

Usage
=====

Option 1: Inputs at command line
--------------------------------

- Run the following::

  $ cd sifter2github
  % sifter2github
  % python sifter2github.py sifter-host sifter-token sifter-project github-user github-password github-repo github-org

Option 2: Inputs in inputs.py
-----------------------------

- Edit `inputs.py` with the appropriate inputs
- Run::

  % python sifter2github.py

Where:

- sifter-host:
- sifter-token:
- sifter-project:
- github-user:
- github-password:
- github-repo:
- github-org: (Optional)