---
card_type: "architecture_pattern"
architecture_type: "integration_api"
---

# Integration API

## Description

An API service that integrates with external systems, webhooks, or third-party providers.

## Typical data

- API keys and secrets
- webhook payloads
- user identifiers
- possibly personal data in transit

## Common regulatory triggers

- data transfer to third parties
- cross-border data transfer risk
- API security requirements
- personal data in transit

## Common red flags

- no API authentication or rate limiting
- secrets stored in plain text
- no logging of API access
- personal data sent to foreign services
- no data processing agreements with partners

## Recommended controls

- API key rotation policy
- secret management system
- API access logging
- data minimization in integrations
- data processing agreements
- encryption in transit (TLS)
