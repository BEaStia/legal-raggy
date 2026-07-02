---
card_type: "architecture_pattern"
architecture_type: "internal_service"
---

# Internal service

## Description

An internal corporate service or tool used by employees within an organization. Not exposed to the public internet.

## Typical data

- employee personal data
- internal business documents
- commercial secrets
- internal analytics and reports

## Common regulatory triggers

- employee personal data processing
- commercial secret protection (98-ФЗ)
- internal access control requirements
- information system security (149-ФЗ)

## Common red flags

- service accessible from internet without need
- no role-based access control
- no audit logging
- shared credentials
- no data classification

## Recommended controls

- restrict access to internal network or VPN
- implement RBAC
- enable audit logging
- classify sensitive data
- regular access reviews
