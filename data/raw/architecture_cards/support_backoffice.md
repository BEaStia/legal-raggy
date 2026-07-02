---
card_type: "architecture_pattern"
architecture_type: "internal_service"
---

# Support and backoffice system

## Description

An internal support system or backoffice tool used by customer support, operations, or management teams to handle user requests, manage accounts, and process internal workflows.

## Typical data

- user support tickets with personal data
- customer account details
- internal notes and decisions
- communication history with users

## Common regulatory triggers

- personal data processing by support staff
- access to personal data by non-technical staff
- commercial secret in internal notes
- data retention for support records

## Common red flags

- support staff has unrestricted access to personal data
- no access logging for backoffice systems
- personal data exported to spreadsheets
- no data retention policy for closed tickets
- support tools accessible from internet

## Recommended controls

- role-based access for support staff
- audit all access to personal data
- mask personal data in support UI where possible
- set retention policy for closed tickets
- restrict backoffice access to internal network or VPN
- regular access reviews for support roles
