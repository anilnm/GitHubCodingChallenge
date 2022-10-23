import requests
import json
import time
import os
import git
import subprocess
import logging
user = "anilnm"
timestr = time.strftime("%Y%m%d-%H%M%S")
RepositoryName = "git_flow_task-"+timestr
local_dir = "C:\\Users\\AnilNM\\PycharmProjects\\pythonProject\\venv"
token = "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"
new_branch_name = "git_flow_feature"
file_name = "sample.txt"
read_me_file = "README.md"

def test_login_and_create_repo():
    '''
    This method checks that given user login to GitHub using basic
    authentication and creates repository with name specific name
    :return: None
    '''
    url = "https://api.github.com/user/repos"
    headers = {"Authorization": "token {}".format(token)}
    data = {"name": "{}".format(RepositoryName)}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    assert response.ok, "Creating Repo failed with status code: {}".format(response.status_code)
    logging.info("\n Successfully created repository: {}".format(RepositoryName))

def test_push_readme_file_for_new_repo():
    '''
    This method create a new repository on the command line using below
    echo "# Dummy_file" >> README.md
    git init
    git add README.md
    git commit -m "first commit"
    git branch -M main
    git remote add origin https://github.com/anilnm/Dummy_file.git
    git push -u origin main
    :return: None
    '''
    if not (os.getcwd() == local_dir):
        os.chdir(local_dir)
    try:
        with open(read_me_file, 'w') as f:
            f.write('# {}'.format(RepositoryName))
    except FileNotFoundError:
        print("The file does not exist")
    subprocess.call(['git', 'init'])
    subprocess.call(['git', 'add', read_me_file])
    subprocess.call(['git', 'commit', '-m', 'first commit'])
    subprocess.call(['git', 'branch', '-M', 'main'])
    subprocess.call(['git', 'remote', 'add', 'origin', 'https://github.com/{}/{}.git'.format(user, RepositoryName)])
    subprocess.call(['git', 'push', 'https://{}@github.com/{}/{}.git'.format(token, user, RepositoryName)])
    logging.info("\n Successfully pushed readme file to repository: {}".format(RepositoryName))

def test_create_new_branch():
    '''
    This method checks that user creates new branch on GitHub
    :return: None
    '''
    url = "https://api.github.com/repos/{}/{}/git/refs/heads".format(user, RepositoryName)
    ssh_key = requests.get(url)
    res = ssh_key.json()
    for i in res:
        if i['ref'] == 'refs/heads/main':
            key = i['object']['sha']
    post_url = "https://api.github.com/repos/{}/{}/git/refs".format(user, RepositoryName)
    headers = {"Authorization": "token {}".format(token)}
    data = {"ref": "refs/heads/{}".format(new_branch_name), "sha": key}
    response = requests.post(post_url, data=json.dumps(data), headers=headers)
    assert response.ok, "Creating branch failed with status code: {}".format(response.status_code)
    logging.info("\n Successfully created new branch {} for repository: {}".format(new_branch_name, RepositoryName))

def test_commit_new_file_and_create_pull_to_master():
    '''
    This method does the following steps
    1. Clone the repository from GitHub using python git
    2. chdir to cloned repo directory
    3. Checkout to already created branch for the repo
    4. Create a new file
    5. Add, Commit and push the new file to created branch
    6. user creates pull request to main branch
    :return: None
    '''
    if not (os.getcwd() == local_dir):
        os.chdir(local_dir)
    git.Git(os.getcwd()).clone('https://github.com/{}/{}.git'.format(user, RepositoryName))
    os.chdir(os.getcwd() + '\\{}'.format(RepositoryName))
    repo = git.Repo()
    repo.git.checkout(new_branch_name)
    try:
        with open(file_name, 'w') as f:
            f.write('Create a new text file!')
    except FileNotFoundError:
        print("The file does not exist")
    subprocess.call(['git', 'add', file_name])
    subprocess.call(['git', 'commit', '-m', 'Committing {} to {}'.format(file_name, new_branch_name)])
    subprocess.call(['git', 'push', 'https://{}@github.com/{}/{}.git'.format(token, user, RepositoryName)])
    headers = {
        "Authorization": "token {}".format(token),
        "Accept": "application/vnd.github.sailor-v-preview+json"
    }
    data = {
        "title": "PullRequest-Using-GithubAPI",
        "body": "pull request from {} to master branch".format(new_branch_name),
        "head": new_branch_name,
        "base": "main"
    }
    url = "https://api.github.com/repos/{}/{}/pulls".format(user, RepositoryName)
    response = requests.post(url, data=json.dumps(data), headers=headers)
    assert response.ok, "Creating pull request to main branch failed with status code: {}".format(response.status_code)
    logging.info("\n Successfully completed pull request to main branch for repository: {}".format(RepositoryName))
