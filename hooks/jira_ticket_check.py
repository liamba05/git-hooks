import json
import re
import sys
import requests
from jira import JIRA, JIRAError

JIRA_TICKET = r"\b[A-Z]+-\d+\b"
JIRA_API_URL = 'https://wincom-plm.atlassian.net/'
CONFIG_URL = "https://raw.githubusercontent.com/liamba05/hooksConfig/main/permissions.json"
YOUR_PATH = "../infr-git-hooks-clientside/hooks/config/local_config.json"


def load_config(file_path=YOUR_PATH, url=CONFIG_URL):
    with open(file_path, 'r') as f:
        config = json.load(f)
    response = requests.get(url)
    response.raise_for_status()
    permissions = response.json()
    badStates = permissions['disallowed_issue_states']
    # Get config data
    return config, badStates


def main():
    config, disallowed_states = load_config()
    jira_info = config['jira_info']
    api_token = jira_info['api_token']
    email = jira_info['personal_email']
    # Load config and set values
    commit_filepath = sys.argv[1]
    # Access temporary filepath git creates containing commit message
    with open(commit_filepath, 'r') as file:
        commit_message = file.read()
    # Read message

    jira_ticket = re.search(JIRA_TICKET, commit_message)
    # Find jira project ID within commit message, is None if no ticket
    if not jira_ticket:
        print("ERROR: Commit message must contain a JIRA ticket ID")
        sys.exit(1)

    jira_ticket = jira_ticket.group(0)
    # Refine jira_ticket to only hold the jira ticket id from the match object

    jira_options = {'server': JIRA_API_URL}
    jira_auth = JIRA(options=jira_options, basic_auth=(email, api_token))
    try:
        issue = jira_auth.issue(jira_ticket)
        status = issue.fields.status.name
    except JIRAError as e:
        print(f"ERROR: Failed to get issue status for {jira_ticket}. Issue does not exist or you do not have "
              f"permission to see it.")
        sys.exit(1)

    if status in disallowed_states:
        print(f"ERROR: Ticket {jira_ticket} is either closed, done, or resolved.")
        sys.exit(1)
    # If status is closed, cancelled, or resolved (unable to change) then give error and exit.

    sys.exit(0)
    # Only get to this point if nothing goes wrong.


if __name__ == "__main__":
    main()
