---
card_type: "architecture_pattern"
architecture_type: "edo_signature_service"
---

# EDO and electronic signature service

## Description

A service that handles electronic document signing, verification, and exchange using electronic signatures (ЭП, УКЭП, НЭП, ПЭП).

## Typical data

- signed electronic documents
- electronic signature certificates
- user identity verification data
- document metadata and audit trail

## Common regulatory triggers

- electronic signature regulation (63-ФЗ)
- legal significance of electronic actions
- certificate management requirements
- document integrity verification

## Common red flags

- using simple e-signature for legally significant actions
- expired or invalid certificates
- no audit trail of signing events
- document tampering possible after signing
- no user consent for electronic actions

## Recommended controls

- use qualified electronic signature (УКЭП) for legal documents
- implement document integrity checks
- maintain signing audit trail
- verify certificate validity before signing
- obtain explicit user consent for electronic actions
- store signed documents with signature verification data
