---
card_type: "architecture_pattern"
architecture_type: "public_saas"
---

# Public SaaS

## Description

A software-as-a-service product available to the general public, typically with self-registration and freemium or subscription model.

## Typical data

- user email
- phone number
- full name
- payment information
- usage data
- user-generated content

## Common regulatory triggers

- personal data processing
- information system of personal data (ИСПДн)
- payment regulation (if payments accepted)
- public offer requirements

## Common red flags

- admin panel accessible from internet
- no MFA for administrative accounts
- personal data in error logs
- no data export mechanism
- unclear data retention

## Recommended controls

- MFA for all admin accounts
- restrict admin access by IP or VPN
- mask personal data in logs
- implement data export and deletion
- publish data retention policy
- regular security audits
