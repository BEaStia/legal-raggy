---
card_type: "architecture_pattern"
architecture_type: "b2b_saas"
---

# B2B SaaS with client workspaces

## Description

A multi-tenant SaaS product used by business customers. Each customer may have its own workspace, users, roles, and data.

## Typical data

- user email
- phone
- full name
- company name
- support messages
- activity logs
- uploaded documents

## Common regulatory triggers

- personal data processing
- personal data information system
- external processor risk
- commercial secret risk
- access control requirements

## Common red flags

- tenant data isolation is not described
- admin panel is publicly exposed
- MFA is missing
- personal data is logged
- support team has excessive access

## Recommended controls

- tenant isolation
- RBAC
- MFA for admins
- audit logs
- masking personal data in logs
- data retention policy
- backup encryption
