---
card_type: "architecture_pattern"
architecture_type: "unknown"
---

# Observability and logging stack

## Description

A centralized logging, monitoring, and observability infrastructure that collects logs, metrics, and traces from multiple services.

## Typical data

- application logs (may contain personal data)
- error traces with user identifiers
- performance metrics
- infrastructure telemetry

## Common regulatory triggers

- personal data in logs (152-ФЗ)
- log retention requirements
- access to logs with personal data
- external observability provider risk

## Common red flags

- personal data (email, phone, IP) in plain-text logs
- logs sent to external service without agreement
- no log access controls
- indefinite log retention
- no log masking or anonymization

## Recommended controls

- mask personal data in logs
- structured logging with PII filters
- restrict log access by role
- set log retention policy
- use internal log aggregation where possible
- encrypt logs at rest
