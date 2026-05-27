# Manual Verification Cases

These cases are executed by browser-manual-verifier during /sdd-verify.

## Browser tool preference

Default:
- agent-browser

Allowed alternatives:
- Playwright MCP
- Chrome DevTools MCP

## Required local environment

Document how the app should be running before verification.

Example:

```bash
docker compose up

or:

make start
Case V-01
Goal
Acceptance criteria covered
AC-__
URL

http://localhost:8080/...

Preconditions
local app is running
test/demo data exists
no real credentials or private data are used
Steps
Expected result
Evidence to collect
browser snapshot
screenshot
console/network notes if relevant
Should become E2E test?

yes | no | maybe

Status

not-run | pass | fail | blocked
