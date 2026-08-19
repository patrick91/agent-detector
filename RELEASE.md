---
release type: minor
---

This release adds `parse_invoking_agent` for parsing an explicit coding-agent
identity propagated through a `User-Agent` value of the form
`<product>/<version> AI-Agent/<agent>`. It returns a `DetectionResult` with the
new `"user-agent"` detection source, and callers can optionally require an
expected client product while continuing to use the package's shared agent
allowlist.
