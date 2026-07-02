---
card_type: "architecture_pattern"
architecture_type: "payment_service"
---

# Payment service

## Description

A service that processes payments, subscriptions, or financial transactions, either directly or through a payment provider.

## Typical data

- payment card details (if not tokenized)
- billing information
- transaction history
- user account and personal data

## Common regulatory triggers

- payment regulation (161-ФЗ)
- Bank of Russia requirements
- PCI DSS compliance
- personal data processing (152-ФЗ)

## Common red flags

- storing raw payment card data
- no PCI DSS compliance
- payment data in logs
- no transaction audit trail
- unclear liability for payment failures

## Recommended controls

- use payment provider tokenization
- never store raw card data
- implement transaction logging
- regular PCI DSS compliance checks
- clear refund and dispute procedures
- separate payment processing from core application
