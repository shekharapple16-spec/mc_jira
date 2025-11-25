from fastmcp import FastMCP
from fastmcp.serve import FastMCPHTTPServer   # ✅ Correct import
import requests
import os

app = FastMCP("jira-mcp")

# Load env vars
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
AC_FIELD = os.getenv("AC_FIELD")


def get_jira_issue(issue_id: str):
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_id}"
    response = requests.get(url, auth=(JIRA_EMAIL, JIRA_TOKEN))
    if response.status_code != 200:
        return {
            "error": f"Failed: {response.status_code}",
            "details": response.text
        }
    return response.json()


@app.tool()
def get_acceptance_criteria(issue_id: str):
    data = get_jira_issue(issue_id)

    if "error" in data:
        return data

    fields = data["fields"]
    ac_value = fields.get(AC_FIELD)

    return {
        "issue": issue_id,
        "acceptance_criteria": ac_value
    }


if __name__ == "__main__":
    server = FastMCPHTTPServer(app)
    server.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
