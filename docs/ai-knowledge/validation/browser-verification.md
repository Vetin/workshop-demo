# Browser Verification Policy

Use this document during /sdd-verify.

## Purpose

Before giving code to user review, the harness must verify user-visible behavior in a real browser when the change affects:

- frontend UI,
- checkout flow,
- product browsing,
- cart behavior,
- forms,
- API behavior visible through the frontend,
- error/loading states,
- accessibility-relevant behavior,
- Figma/UI-kit mapped components.

## Preferred browser tool

Default:

- agent-browser CLI

Reason:
- simple CLI,
- works through Bash,
- no MCP setup required,
- supports snapshots with refs,
- supports screenshots,
- easy for agentic browser testing.

Optional alternatives:

- Playwright MCP
- Chrome DevTools MCP

Use Playwright MCP when:
- MCP tools are already configured,
- accessibility snapshots are preferred,
- the workflow should stay inside MCP.

Use Chrome DevTools MCP when:
- debugging console errors,
- debugging network requests,
- inspecting perfor- inspecting perfor- inspecting perfor- inspecting perfor- inspecs data.

## Verification order

DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDverification commaDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDverification commaDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDverification commaDDDDDDDDDDDDDDDDDDal verification reDDDDDDDDDDDDDDDnuDDDDDDDDDDDDDDDDoutpDDDDDDDDDDDDDDDs/DDDDDDDs/DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDverificaicaDDDDDDDDDDDDDDDDDDDDveriDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDst DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDool used,
- URL,
- steps executed,
- expected result,
- actual result,
- screenshots,
- console/network observations if available,
- pass/fail/blocked,
- follow-up tasks if failed.

## E## E## E## E## E## E## E## E## E manu## E## E## E## Epasses, the harness must decide whether the beha## E## E## E## E## E## ut## E## E## E## E## E## E## E## E##atures/{feature-area}/changes/{change-slug}## E## E## E## E## E## E## E## E## n ask## E## E## E## E## E## E#r upd## E## E## E## E## E##sts sh## E## E## E## E## E## E## Eha## E## E## E## E## E## E## E## E## E manu## E## E## E## Epasses, the harness must decide anua## E## E## E## E##  is ## E## E## E## E## E## E## E## E## E manu## E## E## E## Epasses, the harness must decide whether the beha## E## E## E## E## E## ut## E## E## E## E## E## E## E## E##atures/{feature-area}/changes/{change-slug}## E## E## E## E## E## E## E## E## n ask## E## E## E## E## E## E#r upd## E## E## E## E## E##sts sh## E## E## E## E## E## E## Eha## E## E## E## E## E## E## E## E## E manu## E## E## E## Epasses,RL## Este## E## E## E## Ees## E## E## E## E# o## E## E## napsho## E## E##,
- p- p- p- p- p- p- p- p- p- p- p- p- p- p- p-nd- p- p- p- p- p- p-rk- p- p- p- p- p- p- p- pagent-browser open http://localhost:8080

2. Capture page state:

   agent-browser snapshot -i

3. Interact by refs:

   agent-browser click @e1
   agent-browser fill @e2 "value"

4. Re-snapshot after page changes:

   agent-browser snapshot -i

5. Capture screenshot:

   agent-browser screenshot docs/features/{feature-area}/changes/{change-slug}/verification/screenshots/V-01.png

6. Close browser:

   agent-browser close

## Sensitive data rule

Do not enter real credentials, personal data, production tokens, or private customer data into browser automation.

Use local demo data only.
