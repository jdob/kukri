# Requirements

GitPython is required:

```
  pip install gitpython
```

# Usage

The script runs against a local clone of a repository. All of the branches
must be fetched from their remotes before running; the script doesn't make
any changes to the git repository itself.

Example:

```
  python gitdiff.py /opt/openstack/tripleo/tuskar master mgt-master
```
