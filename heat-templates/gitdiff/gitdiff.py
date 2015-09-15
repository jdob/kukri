# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import argparse
from datetime import datetime

from git import Repo


class RepoDiffer(object):

    def __init__(self, repo_dir, summary=False, depth=None):
        self.repo = Repo(repo_dir)
        self.summary = summary
        self.depth = depth

    def diff_repos(self, branch_1, branch_2):
        from_branch = Branch(self.repo, branch_1)
        to_branch = Branch(self.repo, branch_2)

        self.print_summary(from_branch, to_branch)
        self.print_change_id_lists(from_branch, to_branch)

        if not self.summary:
            self.print_change_id_details(from_branch, to_branch)
        self.print_non_change_id_changes(from_branch, to_branch)

    def print_summary(self, branch_1, branch_2):
        self._print_section('Summary')
        print('')
        print('Repository: %s' % self.repo.working_dir)
        print('Number of change IDs in %s: %s' %
              (branch_1.branch_name, len(branch_1.change_ids)))
        print('Number of change IDs in %s: %s' %
              (branch_2.branch_name, len(branch_2.change_ids)))
        print('')
        print('')

    def print_change_id_lists(self, branch_1, branch_2):
        self._print_section('Change IDs')
        print('')
        self._print_change_id_diff(branch_1, branch_2)
        print('')
        self._print_change_id_diff(branch_2, branch_1)
        print('')
        print('')

    def print_change_id_details(self, branch_1, branch_2):
        self._print_section('Change Details')
        print('')
        self._print_change_id_diff_details(branch_1, branch_2)
        print('')
        self._print_change_id_diff_details(branch_2, branch_1)
        print('')
        print('')

    def print_non_change_id_changes(self, branch_1, branch_2):
        self._print_section('Commits Without Change IDs')
        print('')
        self._print_message_diff(branch_1, branch_2)
        print('')
        self._print_message_diff(branch_2, branch_1)
        print('')
        print('')

    def _print_change_id_diff(self, from_branch, to_branch):
        f = set(from_branch.change_ids)
        t = set(to_branch.change_ids)
        differences = f - t
        if len(differences) == 0:
            print('* There are no change IDs in %s that are not in %s *' %
                  (from_branch.branch_name, to_branch.branch_name))
        else:
            print('* %s changes in %s that are not in %s *' %
                  (len(differences), from_branch.branch_name, to_branch.branch_name))

            if self.summary:
                return

            for change_id in differences:
                print('  %s' % change_id)

    def _print_message_diff(self, from_branch, to_branch):
        from_wrappers = [CommitMessageWrapper(c) for c in from_branch.commits]
        to_wrappers = [CommitMessageWrapper(c) for c in to_branch.commits]

        f = set(from_wrappers)
        t = set(to_wrappers)
        differences = f - t

        # Remove the "Merge *" commits that Jenkins adds
        differences = [c for c in differences if c.commit.author.name != 'Jenkins']

        # Remove entries with a change ID
        differences = [c for c in differences if _parse_change_id(c.commit.message) is None]

        if len(differences) == 0:
            print('* There are no extra changes in %s but not in %s *' %
                  (from_branch.branch_name, to_branch.branch_name))
        else:
            print('* %s extra changes in %s but not in %s *' %
                  (len(differences), from_branch.branch_name, to_branch.branch_name))

            if self.summary:
                return

            print('')

            for wrapper in differences:
                print('-----------------------------------')
                print('Commit ID: %s' % str(wrapper.commit))
                print('Author: %s' % wrapper.author)
                print('Author Date: %s' % datetime.fromtimestamp(wrapper.authored_date))
                print('Commit Date: %s' % datetime.fromtimestamp(wrapper.committed_date))
                print('')
                print(wrapper.message)

            print('-----------------------------------')

    def _print_change_id_diff_details(self, from_branch, to_branch):
        f = set(from_branch.change_ids)
        t = set(to_branch.change_ids)
        differences = f - t

        if len(differences) == 0:
            print('* There are no missing changes from %s into %s *' %
                  (from_branch.branch_name, to_branch.branch_name))
        else:
            print('* %s changes missing from %s that are in %s *' %
                  (len(differences), to_branch.branch_name, from_branch.branch_name))

            if self.summary:
                return

            print('')
            for change_id in differences:
                commit_id = from_branch.commit_id_for_change(change_id)
                c = self.repo.commit(commit_id)

                print('-----------------------------------')
                print('Commit ID: %s' % commit_id)
                print('Author: %s' % c.author)
                print('Author Date: %s' % datetime.fromtimestamp(c.authored_date))
                print('Commit Date: %s' % datetime.fromtimestamp(c.committed_date))
                print('')
                print(c.message)

            print('-----------------------------------')

    def _print_section(self, name):
        print('==== %s ==========================================================' % name)


class Branch(object):

    def __init__(self, repo, branch_name, depth=None):
        self.repo = repo
        self.branch_name = branch_name
        self.depth = depth

        self.change_id_to_commit_id = self._change_to_commit_id_map()

    @property
    def commits(self):
        all_commits = [c for c in self.repo.iter_commits(rev=self.branch_name)]
        return all_commits

    @property
    def commit_ids(self):
        commit_ids = [str(c) for c in self.repo.iter_commits(rev=self.branch_name)]

        if self.depth is not None:
            commit_ids = commit_ids[0:self.depth]

        return commit_ids

    @property
    def change_ids(self):
        return self.change_id_to_commit_id.keys()

    @property
    def non_change_commits(self):
        commit_ids = [c for c in self.commit_ids if
                      self.commit_id_for_change(c) is None]
        return commit_ids

    def change_id_for_commit(self, commit_id):
        message = self.repo.commit(rev=commit_id).message
        change_id = _parse_change_id(message)
        return change_id

    def message_for_commit(self, commit_id):
        return self.repo.commit(rev=commit_id).message

    def commit_id_for_change(self, change_id):
        commit_id = self.change_id_to_commit_id.get(change_id, None)
        return commit_id

    def _change_to_commit_id_map(self):
        all_commit_ids = self.commit_ids

        changes_to_commit_id = {}
        for commit_id in all_commit_ids:
            change_id = self.change_id_for_commit(commit_id)
            if change_id is not None:
                # Safety check
                if change_id in changes_to_commit_id:
                    print('Change ID %s already found in a commit' % change_id)

                changes_to_commit_id[change_id] = commit_id

        return changes_to_commit_id


class CommitMessageWrapper(object):

    def __init__(self, commit):
        self.commit = commit

    def __eq__(self, other):
        return self.commit.message == other.commit.message

    def __hash__(self):
        return self.commit.message.__hash__()

    def __getattr__(self, name):
        return getattr(self.commit, name)


def _parse_change_id(message):
    message_lines = message.split('\n')

    for l in message_lines:
        if l.startswith(u'Change-Id:'):
            change_id = l[10:].strip()
            return change_id

    return None


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('repo_dir',
                        help='Full path to the local clone of the repository')
    parser.add_argument('branch_1',
                        help='Branch name to use in the diff')
    parser.add_argument('branch_2',
                        help='Branch name to use in the diff')
    parser.add_argument('--counts-only', '-c', dest='counts_only', action='store_true',
                        help='if specified, only the counts for each diff will be displayed')

    args = parser.parse_args()

    return args.repo_dir, args.branch_1, args.branch_2, args.counts_only


if __name__ == '__main__':
    d, b1, b2, counts_only = parse_args()

    differ = RepoDiffer(d, summary=counts_only)
    differ.diff_repos(b1, b2)
