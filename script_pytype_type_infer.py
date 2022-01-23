#author: Malinda Dilhara
from __future__ import print_function

import ast
import gc
import json
import multiprocessing
import os
import subprocess
import sys
import textwrap
from glob import glob
from os import path

import pytype
from git import Repo
from pydriller import GitRepository
from pydriller import RepositoryMining as rp
from pytype import config
from pytype.tools.annotate_ast import annotate_ast
from typed_ast import ast27 as ast27
from typed_ast import ast3

py_version_s = '3.7'
py_version = (3, 7)


def annotate(source, file_name, pytype_storage, type_repo):
    source = textwrap.dedent(source.lstrip('\n'))
    ast_factory = lambda unused_options: ast
    # pytype_options = config.Options.create(python_version=(3,7),nofail=True,protocols=True,no_report_errors=True,keep_going=True,
    #               imports_map=pytype_out_path+'/imports/'+file_name)
    try:
        pytype_options = config.Options.create(python_version=py_version, nofail=True, protocols=True,
                                               imports_map=pytype_storage + '/imports/' + file_name)
        module = annotate_ast.annotate_source(source, ast_factory, pytype_options)
    except pytype.tools.annotate_ast.annotate_ast.PytypeError as e:
        print(e)
        return None
    except IndexError as e:
        print(e)
        return None
    except FileNotFoundError as e:
        print(e)
        return None
    except SyntaxError as e:
        print(e)
        return None
    except ValueError as e:
        return None

    return module


def get_annotations_dict(module, empty_line):
    return [{"lineNumber": _get_node_key(node)[0] + empty_line, "col_offset": _get_node_key(node)[1],
             "nodeName": _get_node_key(node)[2], "type": node.resolved_annotation}
            for node in ast.walk(module)
            if hasattr(node, 'resolved_type')]


def generate_pytype_folder(project_path, file_path, pytype_storage, type_repo):
    env = os.environ.copy()
    subprocess.run(['pytype', '--pythonpath=' + project_path, '--python-version=' + py_version_s, '--no-report-errors',
                    '--keep-going', '--protocols', '--output=' + pytype_storage, file_path], shell=False, env=env,
                   cwd=os.path.dirname(os.path.realpath(__file__)))


def _get_node_key(node):
    # AST Name = node.__class__.__name__
    base = (node.lineno, node.col_offset)
    if isinstance(node, ast.Name):
        return base + (node.id,)
    elif isinstance(node, ast.Attribute):
        return base + (node.attr,)
    elif isinstance(node, ast.FunctionDef):
        return base + (node.name,)
    elif isinstance(node, ast.Param):
        return base + (node.name,)
    else:
        return base


def get_ast(options):
    major = options.python_version[0]
    return {2: ast27, 3: ast3}[major]


def main1():
    pytype_storage = sys.argv[1]   #a directory for pytype's intermediate processing files
    gitrepo_loc = sys.argv[2]   # a directory to store the GitRepos
    type_repo = sys.argv[3]    # a directory to store type information
    project_name = sys.argv[4] # GitHub full name of the project e.g., author/project_name
    url = sys.argv[5]      # GitHub clone url e.g., https://github.com/author/project_name.git

    if not os.path.exists(pytype_storage):
        os.makedirs(pytype_storage)
    if not os.path.exists(gitrepo_loc):
        os.makedirs(gitrepo_loc)
    if not os.path.exists(type_repo):
        os.makedirs(type_repo)

    project_path = gitrepo_loc + "/" + project_name
    repo_clone(url, gitrepo_loc, project_name)
    iterate_commits(project_path, project_name, pytype_storage, type_repo)


def repo_clone(url, location, repo_name):
    if not os.path.exists(location + repo_name):
        os.makedirs(location + repo_name)
        print("Repo is downloading to :" + location + "/" + repo_name)
        Repo.clone_from(url=url, to_path=location + "/" + repo_name)
    else:
        print("Repo already exists")


def iterate_commits(project_path, project_name, pytype_storage, type_repo):
    git = GitRepository(project_path)
    error_commits = 0
    total_commits = 0

    p = glob(type_repo + project_name + "/" + "*/")
    analysed = [x.split('/')[-2] for x in p]
    # , only_in_branch = git.repo.active_branch
    for commit in rp(project_path, only_modifications_with_file_types=['.py'], order='reverse').traverse_commits():

        git.checkout(commit.hash)
        print("before " + commit.hash)
        first_rev = True
        manager = multiprocessing.Manager()
        state = manager.dict(list_size=5 * 1000 * 1000)  # shared state
        p1 = multiprocessing.Process(target=process_before_change,
                                     args=(commit, first_rev, project_name, project_path, pytype_storage,
                                           total_commits, type_repo,))
        # first_rev, total_commits = process_before_side(commit, first_rev, project_name, project_path, pytype_storage,
        #                                                total_commits, type_repo)

        p1.start()
        p1.join()
        p1.close()
        del p1
        try:
            git.checkout(commit.parents.pop(0))
        except IndexError as e:
            print(e)
            continue
        except OSError as e:
            print(e)
            continue
        print("after " + commit.hash)
        p2 = multiprocessing.Process(target=process_after_change,
                                     args=(commit, error_commits, first_rev, project_name, project_path, pytype_storage,
                                           total_commits,
                                           type_repo,))
        p2.start()
        p2.join()
        p2.close()
        del p2
        del manager
        del state
        gc.collect()
        # process_after_change(commit, error_commits, first_rev, project_name, project_path, pytype_storage, total_commits,
        #                      type_repo)


def process_after_change(commit, error_commits, first_rev, project_name, project_path, pytype_storage, total_commits,
                         type_repo):
    for mod in commit.modifications:
        if (mod.filename.endswith(".py")):
            file_path = project_path + '/' + mod.old_path
            save_name = type_repo + project_name + '/' + commit.hash + 'O/' + mod.old_path.replace('/', '_')[
                                                                              :-3] + '.json'
            dir = os.path.dirname(save_name)
            if not os.path.exists(dir):
                os.makedirs(dir)
            try:
                if (path.exists(save_name)):
                    print("already analyzed")
                    continue
                first_rev = generate_type_info(file_path, project_path, mod.old_path.replace('/', '.'), save_name,
                                               pytype_storage, type_repo)
            except UnicodeEncodeError as e:
                print(e)
                continue
    if first_rev is False:
        error_commits += 1
    print(str(total_commits) + " total commits " + str(error_commits) + " had errors")


def process_before_change(commit, first_rev, project_name, project_path, pytype_storage, total_commits, type_repo):
    for mod in commit.modifications:
        total_commits += 1
        # if (mod.filename.endswith(".py") and mod.old_path is not None and mod.change_type is not ModificationType.DELETE):
        if (mod.filename.endswith(".py")):
            file_path = project_path + '/' + mod.new_path
            save_name = type_repo + project_name + '/' + commit.hash + 'N/' + mod.new_path.replace('/', '_')[
                                                                              :-3] + '.json'
            dir = os.path.dirname(save_name)
            if not os.path.exists(dir):
                os.makedirs(dir)
            try:
                if (path.exists(save_name)):
                    print("already analyzed")
                    continue
                first_rev = generate_type_info(file_path, project_path, mod.new_path.replace('/', '.'), save_name,
                                               pytype_storage, type_repo)
            except UnicodeEncodeError as e:
                print(e)
                continue
    return first_rev, total_commits


def generate_type_info(file_path, project_path, file_name, save_name, pytype_storage, type_repo):
    generate_pytype_folder(project_path, file_path, pytype_storage, type_repo)
    try:
        with open(file_path, 'r') as f:
            src = f.read()
    except FileNotFoundError as e:
        return False
    except UnicodeDecodeError as e:
        return False
    first_empty_count = 0
    for line in src.split('\n'):
        if len(line) == 0:
            first_empty_count += 1
        else:
            break

    print(file_name[:-3] + 'imports')

    module = annotate(src, file_name[:-3] + '.imports', pytype_storage, type_repo)
    if module is None:
        return False

    dic_str = get_annotations_dict(module, first_empty_count)
    # print(dic_str)

    with open(save_name, 'w') as outfile:
        json.dump(dic_str, outfile)
    return True

if __name__ == '__main__':
    main1()
