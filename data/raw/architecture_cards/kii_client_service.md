---
card_type: "architecture_pattern"
architecture_type: "unknown"
---

# KII client or supplier service

## Description

A service that is supplied to or operates on behalf of a critical information infrastructure (КИИ) subject, such as banks, energy companies, transport, healthcare, or government organizations.

## Typical data

- operational data of critical systems
- employee personal data of КИИ subject
- system configuration and topology
- incident and security event data

## Common regulatory triggers

- КИИ regulation (187-ФЗ)
- significant object categorization
- GosSOPKA integration requirements
- enhanced security requirements

## Common red flags

- no КИИ categorization performed
- no incident reporting to GosSOPKA
- insufficient security controls for КИИ level
- no security assessment of the service
- unclear responsibility boundaries

## Recommended controls

- determine if service is a КИИ object
- categorize by significance level
- implement required security controls
- integrate with GosSOPKA
- regular security assessments
- document responsibility boundaries with КИИ subject
