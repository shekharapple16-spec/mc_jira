from fastmcp import FastMCP
from fastapi import FastAPI
import requests
import os

app_mcp = FastMCP("jira-mcp")     # MCP logic
app = FastAPI()                   # HTTP server wrapper

# Load env vars
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
AC_FIELD = os.getenv("AC_FIELD")


def get_jira_issue(issue_id: str):
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_id}"
    response = requests.get(url, auth=(JIRA_EMAIL, JIRA_TOKEN))
    if response.status_code != 200:
        return {"error": f"Failed: {response.status_code}", "details": response.text}
    return response.json()


@app_mcp.tool()
def get_acceptance_criteria(issue_id: str):
    data = get_jira_issue(issue_id)
    if "error" in data:
        return data
    fields = data["fields"]
    ac_value = fields.get(AC_FIELD)
    return {"issue": issue_id, "acceptance_criteria": ac_value}


# --------- HTTP ENDPOINT TO LET VS CODE CALL MCP ----------
@app.post("/mcp")
async def mcp_handler(request: dict):
    """Wrap FastMCP for HTTP transport"""
    response = await app_mcp.dispatch(request)
    return response


# ------------- Root health check ----------------
@app.get("/")
def health():
    return {"status": "running MCP JIRA server on Render"}
