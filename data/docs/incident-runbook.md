---
id: incident-runbook
title: Production incident runbook
labels: engineering
---
Severity 1 incidents require the on-call engineer to acknowledge the page within 15 minutes and open an incident channel.

Roll back the last deployment first if the incident started within an hour of a release. The rollback command is documented in the deployment pipeline README.

After resolution, write a blameless post-incident review within five working days.
