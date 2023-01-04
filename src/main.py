import alias_modifier
import global_constants
import request_triager
from github import Github

gh = Github(global_constants.GITHUB_TOKEN)


def main():
    alias_modifier.init_file_if_not_exists()

    repo = gh.get_repo(f"{global_constants.ORG_NAME}/{global_constants.REPO_NAME}")
    issue = repo.get_issue(global_constants.ISSUE_NUMBER)

    print("Request #{} is now triaging...".format(global_constants.ISSUE_NUMBER))
    triage = request_triager.triage_request(issue)

    if not triage["approved"]:
        print("E: Request was denied with reason: {}".format(triage["reason"]))
        return

    alias_name, query = triage["alias_name"], triage["query"]

    print("Modifying aliases file...")
    alias_modifier.add_alias(alias_name, query)

    print("The alias was successfully added and pushed to the repo.")
    request_triager.create_added_comment(issue, alias_name)
    print("Closing issue...")
    request_triager.close_issue(issue, True)


if __name__ == '__main__':
    main()
