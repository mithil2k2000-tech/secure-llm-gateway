# AI incident response

An AI incident is any event where the assistant:
- discloses data a user should not see;
- follows injected instructions;
- produces harmful or materially wrong guidance that someone relied on;
- is abused for cost or availability.

| Step | Action | Who |
|---|---|---|
| 1. Contain | Set `GATEWAY_DISABLED=true` (returns 503 for all questions without redeploying code). Quarantine any suspect document by removing it from `data/docs/`. | On-call engineer |
| 2. Preserve | Run `GET /v1/audit/verify` (admin) and copy the audit log to write-once storage. Note request IDs. | On-call engineer |
| 3. Assess | Find affected requests in the audit log by user, time and reasons. Decide whether personal data was disclosed. If so, the DPO decides within 72 hours whether to report it to the ICO. | Security, DPO |
| 4. Fix | Add the attack as a new case in `eval/cases.json`, fix the control, and confirm the CI gate passes. | Engineering |
| 5. Recover | Re-enable, monitor blocked-request reasons for a week. | Product owner |
| 6. Learn | Blameless review within five working days; update the risk register and system card. | Product owner |
