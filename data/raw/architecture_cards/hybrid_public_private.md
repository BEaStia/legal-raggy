---
card_type: "architecture_pattern"
architecture_type: "hybrid"
---

# Hybrid public-private architecture

## Description

An architecture with both public-facing components and internal/private components, typically with a DMZ or API gateway separating them.

## Typical data

- personal data in public services
- internal business data in private services
- authentication tokens crossing boundaries
- API keys and service credentials

## Common regulatory triggers

- personal data processing (public side)
- data flow between public and private zones
- network segmentation requirements
- cross-zone access control

## Common red flags

- no clear network segmentation
- direct database access from public zone
- secrets shared between zones
- no monitoring of cross-zone traffic
- personal data flowing to less-protected zones

## Recommended controls

- implement DMZ or API gateway
- separate databases per zone
- use service mesh for internal communication
- encrypt data crossing zone boundaries
- monitor and audit cross-zone access
- regular penetration testing
