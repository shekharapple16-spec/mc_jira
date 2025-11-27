from fastmcp import FastMCP
import os
import requests
from fastapi import FastAPI

# Create MCP app
app = FastMCP("jira-mcp")

# Load environment variables
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
AC_FIELD = os.getenv("AC_FIELD", "description")


def get_jira_issue(issue_id: str):
    """Internal helper to fetch Jira issue details."""
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
    """Returns Acceptance Criteria from a Jira issue."""
    data = get_jira_issue(issue_id)

    if "error" in data:
        return data

    fields = data.get("fields", {})
    ac_value = fields.get(AC_FIELD, None)

    return {
        "issue": issue_id,
        "acceptance_criteria": ac_value
    }


# =========================
# Health-check route
# =========================
@app.app.get("/")
async def root():
    """Simple health-check endpoint for browser/monitoring."""
    return {
        "status": "MCP server 'jira-mcp' is running!",
        "mcp_endpoint": "/mcp"
    }


# =========================
# Server start
# =========================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port, transport="http")
