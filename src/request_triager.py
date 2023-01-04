import re

import global_constants
import alias_modifier


def parse_issue_body(issue_body):
    body_lines = issue_body.splitlines()

    phase = "none"

    alias_name = None
    query = None
    for line in body_lines:
        if line.startswith("### エイリアスの名前"):
            phase = "alias_name"
            continue
        elif line.startswith("### クエリ"):
            phase = "query"
            continue

        if line.isspace() or line == "":
            continue

        if phase == "alias_name":
            alias_name = line
        elif phase == "query":
            query = line

    return {
        "alias_name": alias_name,
        "query": query,
    }


def is_request_pending(issue):
    for label in issue.labels:
        if label.name == global_constants.PENDING_LABEL_NAME:
            return True
    return False


def permission_to_number(permission):
    if permission == "admin":
        return 3
    elif permission == "write":
        return 2
    elif permission == "read":
        return 1
    else:
        return 0


def check_author_authorized(issue):
    author = issue.user
    repo = issue.repository
    is_personal = repo.owner.type == "User"

    if not is_personal and global_constants.CHECK_USER_IN_ORG:
        org = repo.organization
        if not org.has_in_members(author):
            return "NOT_IN_ORGANIZATION"

    required_permission = permission_to_number(global_constants.PERMISSION_LEVEL)
    if permission_to_number(repo.get_collaborator_permission(author)) < required_permission:
        return "NO_PERMISSION"

    return "OK"


def close_issue(issue, is_approved):
    # issue.edit(state="closed", state_reason="completed" if is_approved else "not_planned")
    issue.edit(state="closed")
    if is_approved:
        issue.lock("resolved")
    else:
        issue.lock("off-topic")


def create_triage_approved(issue, alias_name):
    issue.remove_from_labels(global_constants.PENDING_LABEL_NAME)
    issue.add_to_labels(global_constants.APPROVED_LABEL_NAME)

    issue.create_comment(global_constants.APPROVED_ISSUE_COMMENT.format(alias_name=alias_name))


def create_added_comment(issue, alias_name):
    issue.create_comment(global_constants.ALIAS_ADDED_COMMENT.format(alias_name=alias_name))


def create_triage_denied(issue, alias_name, reason):
    issue.remove_from_labels(global_constants.PENDING_LABEL_NAME)
    issue.add_to_labels(global_constants.DENIED_LABEL_NAME)

    issue.create_comment(global_constants.DENIED_ISSUE_COMMENT.format(
        alias_name=alias_name, reason=global_constants.DENY_REASONS[reason], raw_reason=reason
    ))

    close_issue(issue, False)


def triage_request(issue):
    print("Request is now triaging...")

    print("Checking if request is pending...")
    if not is_request_pending(issue):
        print("Request is not pending.")
        return {
            "approved": False,
            "reason": "NOT_PENDING",
        }

    print("Parsing issue body...")
    issue_body = issue.body
    parsed_issue_body = parse_issue_body(issue_body)
    alias_name = parsed_issue_body["alias_name"]
    query = parsed_issue_body["query"]

    if alias_name is None or query is None:
        print("E: Unable to parse request.")
        create_triage_denied(issue, alias_name, "UNABLE_TO_PARSE_REQUEST")
        return {
            "approved": False,
            "reason": "UNABLE_TO_PARSE_REQUEST",
        }

    print("Checking if author is authorized...")
    auth_result = check_author_authorized(issue)
    if auth_result != "OK":
        print("E: Author is not authorized.")
        create_triage_denied(issue, alias_name, "UNAUTHORIZED::" + auth_result)
        return {
            "approved": False,
            "reason": "UNAUTHORIZED::" + auth_result,
        }

    if not re.match(global_constants.ALIAS_NAME_PATTERN, alias_name):
        print("E: Invalid alias name.")
        create_triage_denied(issue, alias_name, "INVALID_ALIAS_NAME")
        return {
            "approved": False,
            "reason": "INVALID_ALIAS_NAME",
        }

    if alias_modifier.is_alias_exists(alias_name):
        print("E: Duplicate alias name.")
        create_triage_denied(issue, alias_name, "DUPLICATE")
        return {
            "approved": False,
            "reason": "DUPLICATE",
        }

    print("Congratulations! The request is triaged and approved!")

    create_triage_approved(issue, alias_name)

    return {
        "approved": True,
        "alias_name": alias_name,
        "query": query,
    }
