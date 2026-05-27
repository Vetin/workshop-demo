# Rejected Knowledge Updates

Updates that were proposed but not accepted, with reasons recorded for future reference.

| Date | Proposing Agent | Target File | Reason Rejected | Reviewer | Proposal Summary |
|------|----------------|-------------|-----------------|----------|-----------------|

---

*(No rejected proposals yet.)*

---

## Rejection reasons (taxonomy)

Use one of these standard reasons when rejecting a proposal:

- **contradicts-source**: The proposed text conflicts with what the source code actually does
- **already-accurate**: The current doc already correctly describes the behavior
- **out-of-scope**: The proposed change is outside the permitted update targets
- **needs-human-review**: The change affects machine-readable files or agent definitions
- **insufficient-evidence**: The proposal lacks a source file:line citation
- **speculation**: The proposed text describes intended future behavior, not current state
- **duplicate**: A pending or accepted proposal already covers this change

## Rejection entry format

```markdown
## [REJECTED] {YYYY-MM-DD} — {proposing-agent}

**Target file:** ...
**Reason:** {taxonomy code above}
**Reviewer:** {reviewing agent or human}
**Detail:** One sentence explaining the specific rejection reason.

**Original proposal:**
> (paste the proposal text)
```
