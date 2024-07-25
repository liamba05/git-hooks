import fnmatch
import re
import subprocess
import sys
import requests
import json

CONFIG_URL = "https://raw.githubusercontent.com/liamba05/hooksConfig/main/permissions.json"
YOUR_PATH = "../infr-git-hooks-clientside/hooks/config/local_config.json"


def fetch_permissions_json(path=YOUR_PATH, url=CONFIG_URL):
    with open(path, 'r') as f:
        config = json.load(f)
    response = requests.get(url)
    response.raise_for_status()
    permissions = response.json()
    # Get config data
    return config, permissions


def get_user():
    name = subprocess.run(['git', 'config', 'user.name'], capture_output=True, text=True)
    return name.stdout.strip()
    # Get current user by using git config (assume committing user has git config --global user.name set)


def get_file_names():
    files = subprocess.run(['git', 'diff', '--cached', '--name-only'], capture_output=True, text=True)
    filesLists = []

    for i in files.stdout.splitlines():
        tempList = i.split("/")
        filesLists.append(tempList)
    return filesLists
    # Get names of files by using git diff command line prompts


def get_users_from_group(group):
    users = []
    for sublist in group:
        for user in sublist:
            users.append(user['username'])
    return users


def open_perms(perms):
    restricted_files = []
    for restricted_file, _ in perms.items():
        restricted_files.append(restricted_file)
    return restricted_files


def check_permissions(user, uploaded_filenames, perms, git_token):
    restricted_files = open_perms(perms)
    unauthorized_files = []
    unauthorized_dirs = []
    for uploaded_file_path in uploaded_filenames:
        dirJustAdded = False
        # Loop through each filename trying to be committed
        for uploaded_file in uploaded_file_path:
            if uploaded_file in restricted_files:
                # Check if committed file matches a restricted file
                authorized_group = perms[uploaded_file]
                auth_users_map = get_team_members(authorized_group, git_token)
                auth_users = get_users_from_group(auth_users_map)
                if user not in auth_users:
                    if uploaded_file != uploaded_file_path[-1]:
                        unauthorized_dirs.append(uploaded_file)
                        dirJustAdded = True
                        break
                    unauthorized_files.append(uploaded_file)
                    # Check if committing user is authorized to alter file/dir
                    # If they are not authorized, add the files the user attempted to alter to a list
        if dirJustAdded:
            pass
    if unauthorized_files:
        print(f"ERROR: User {user} is not authorized to alter the following files:")
        for file in unauthorized_files:
            print(f" - {file}")
        print("And directories: ")
        for dir in unauthorized_dirs:
            print(f" - {dir}")
        return False
    # If the list of rejected files is not empty, return false and print out the rejected files
    return True
    # If the list of rejected files is empty, return true.


def slugify(slug):
    slug = slug.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = re.sub(r'^-+|-+$', '', slug)
    return slug


def get_team_members(team_slugs, git_token):
    headers = {
        'Authorization': f'token {git_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    all_members = []

    for team_slug in team_slugs:
        slug = slugify(team_slug)
        url = f"https://api.github.com/orgs/wincomplm/teams/{slug}/members"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            members = response.json()
            all_members.append([{'username': member['login']} for member in members])
        else:
            print(f"Failed to fetch team members for team {slug}: {response.status_code}, {response.text}")
    return all_members


def main():
    config, files = fetch_permissions_json()
    restricted_files = files['files']
    git_token = config['git_token']

    commit_files = get_file_names()
    user = get_user()

    if not check_permissions(user, commit_files, restricted_files, git_token):
        sys.exit(1)
    else:
        sys.exit(0)
    # initialize and run everything...


if __name__ == "__main__":
    main()
