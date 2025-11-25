from fastmcp import FastMCP
import requests
import os

# IMPORTANT: enable HTTP mode
app = FastMCP("jira-mcp", transport="http")

# Load env vars
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")


def get_jira_issue(issue_id: str):
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_id}"
    response = requests.get(url, auth=(JIRA_EMAIL, JIRA_TOKEN))
    if response.status_code != 200:
        return {"error": response.status_code, "details": response.text}
    return response.json()


@app.tool()
def get_acceptance_criteria(issue_id: str):
    data = get_jira_issue(issue_id)
    if "error" in data:
        return data

    fields = data["fields"]
    ac_field = os.getenv("AC_FIELD")

    ac_value = fields.get(ac_field, None)
    if ac_value is None:
        return {"message": f"AC field '{ac_field}' not found in this issue."}

    return {
        "issue": issue_id,
        "acceptance_criteria": ac_value
    }

# HTTP server entry for Render
if __name__ == "__main__":
    # Render sets PORT automatically
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
