from fastmcp import FastMCP
from fastmcp.http import FastMCPHttp
import requests
import os

app = FastMCP("jira-mcp")

# Load environment variables
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")


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
    ac_field = os.getenv("AC_FIELD")

    ac_value = fields.get(ac_field)
    if ac_value is None:
        return {"message": f"AC field '{ac_field}' not found in this issue."}

    return {
        "issue": issue_id,
        "acceptance_criteria": ac_value
    }


# --- HTTP transport wrapper ---
mcp_http = FastMCPHttp(app)

if __name__ == "__main__":
    # Default port Render uses is $PORT
    import os
    port = int(os.getenv("PORT", 8000))
    mcp_http.run(host="0.0.0.0", port=port)