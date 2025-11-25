from fastapi import FastAPI
from fastmcp import FastMCP
import requests
import os

app = FastMCP("jira-mcp")
api = FastAPI()

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


@app.tool()
def get_acceptance_criteria(issue_id: str):
    data = get_jira_issue(issue_id)
    if "error" in data:
        return data
    fields = data.get("fields", {})
    return {
        "issue": issue_id,
        "acceptance_criteria": fields.get(AC_FIELD)
    }


# ---- HTTP Wrapper for Render ----
@api.get("/")
def root():
    return {"status": "Jira MCP running"}


@api.post("/run")
def run_tool(tool: str, issue_id: str):
    if tool == "get_acceptance_criteria":
        return get_acceptance_criteria(issue_id)
    return {"error": "Unknown tool"}
