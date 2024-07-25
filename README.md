Installation guide can be found [here](https://wincom-plm.atlassian.net/wiki/spaces/WK/pages/104005637/How+to+install+git+client-side+hooks)


How Jira Ticket Check Hook Works:
  * Initiate logging file at ../.git/hooks/JiraApiErrs.log
  * Load local config containing Jira API credentials
  * Load [online config](https://github.com/wincomplm/infr-git-hooks-config/blob/main/permissions.json) containing the blacklisted Jira issue states
  * Find commit message and detect Jira ticket using Regex r"\b[A-Z]+-\d+\b"
  * If no ticket in commit message, error and exit
  * Connect to Jira API and check issue status
  * If we fail to get ticket issue status, log the error, and give detailed error message
  * If issue status is 'closed,' 'done,' or 'resolved,' error and exit
  * If we have gotten to this point without errors, there is a valid Jira ticket and the hook will pass.

How File Permission Check Hook Works:
  * Load local and [online config](https://github.com/wincomplm/infr-git-hooks-config/blob/main/permissions.json) containing Git API credentials and the restricted files and their authorized users.
  * Check permissions by looping through each restricted file and their authorized groups.
  * For each restricted file, check it against all uploaded file names.
  * If user tries to commit a change to a restricted file, get the authorized team members through git api.
  * If the user is not authorized, add the unauthorized file to a list.
  * After finding all unauthorized files, error and print out each file the user is unauthorized to change.
  * If we reach this point without errors, the user is either permitted or they are not altering a restricted file
