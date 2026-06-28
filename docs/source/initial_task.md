# Handoff: Russian IT Compliance Architecture Agent

## 1. Project Summary

We are building a production-style **Agentic RAG system for preliminary IT architecture compliance review under Russian regulation**.

The product is not a legal-advice chatbot. It is an assistant for CTOs, architects, team leads, product owners, and security engineers who want to pre-check an IT system architecture before handing it to legal/security review.

The assistant should analyze a text description of an IT system, extract architecture and data-flow facts, detect possible regulatory triggers, retrieve relevant legal/security requirements, and return a structured assessment with citations and clarification questions.

Working title:

```text
russian-it-compliance-agent
```

Core idea:

```text
Architecture description
  -> structured architecture profile
  -> deterministic rule-based trigger detection
  -> retrieval over legal/security corpus
  -> structured risk assessment
  -> clarification questions
  -> recommended controls
```

The first implementation should prioritize a reliable deterministic MVP over a complex autonomous agent.

---

## 2. Product Goal

The system should answer questions like:

```text
У нас B2B SaaS. Пользователи регистрируются по email и телефону.
База хранится в российском облаке. Логи уходят во внешний observability-сервис.
Админка доступна из интернета, MFA пока нет. Есть интеграция с платежным провайдером.
Что тут проверить с точки зрения законодательства и ИБ?
```

Expected output:

* detected architecture type;
* detected data categories;
* possible regulatory triggers;
* red flags;
* missing information;
* recommended controls;
* legal/security basis with citations;
* need for human legal/security review.

---

## 3. Important Product Boundaries

The system must not claim to provide final legal advice.

Every generated assessment must include a disclaimer:

```text
Ответ носит информационный характер и предназначен для предварительной архитектурной проверки. Он не является юридическим заключением, аудитом ИБ или заменой консультации профильного специалиста.
```

The assistant should use cautious language:

* “возможно применимо”;
* “требует проверки”;
* “нужно уточнить”;
* “может возникать обязанность”;
* “следует передать на проверку ИБ/юристам”.

Avoid categorical claims unless directly supported by a rule and retrieved source.

---

## 4. MVP Scope

### 4.1 In scope

The MVP should support these domains:

1. **Personal data / 152-ФЗ**

   * personal data processing;
   * websites collecting email/phone/name;
   * user accounts;
   * admin access to personal data;
   * logs containing personal data;
   * external processors;
   * possible cross-border transfer;
   * ИСПДн / personal data information system;
   * security measures under ПП РФ №1119 and ФСТЭК №21.

2. **Information / IT systems / 149-ФЗ**

   * information systems;
   * information protection;
   * public websites;
   * access control;
   * information owner/operator concepts.

3. **Electronic signature / 63-ФЗ**

   * legally significant user actions;
   * electronic document signing;
   * simple electronic signature;
   * enhanced electronic signature;
   * EDI-like flows.

4. **Commercial secret / 98-ФЗ**

   * internal business data;
   * customer databases;
   * source code;
   * technical documentation;
   * analytics and reports;
   * trade secret protection triggers.

5. **Critical information infrastructure / 187-ФЗ**

   * only preliminary detection;
   * if the system belongs to or is supplied to a КИИ subject;
   * flag as requiring human review.

6. **Finance/payment domain**

   * detect if payment flows exist;
   * flag possible 161-ФЗ / Bank of Russia / financial regulation relevance;
   * do not deeply implement finance compliance in MVP.

### 4.2 Out of scope for MVP

Do not implement full legal reasoning for:

* medical information systems;
* state information systems;
* banking compliance in depth;
* ГОСТ/СТО compliance scoring;
* full threat modeling;
* certification/attestation workflow;
* production authentication;
* UI frontend;
* automatic downloading of official laws;
* automatic legal updates.

These can be added later.

---

## 5. Recommended Stack

Use:

* Python 3.12+
* FastAPI
* Pydantic v2
* Qdrant
* Docker Compose
* pytest
* Ruff
* mypy or pyright if convenient
* LangGraph later, not required for first milestone
* Pydantic AI later, not required for first milestone

For the first milestone, keep the LLM integration optional and mockable.

The deterministic rule engine is more important than LLM generation at the start.

---

## 6. Repository Structure

Create this structure:

```text
russian-it-compliance-agent/
  app/
    api/
      __init__.py
      main.py
      routes/
        __init__.py
        health.py
        analyze.py
        search.py
        documents.py

    core/
      __init__.py
      config.py
      logging.py

    models/
      __init__.py
      architecture.py
      compliance.py
      documents.py
      retrieval.py

    ingestion/
      __init__.py
      loaders.py
      chunking.py
      metadata.py
      pipeline.py

    retrieval/
      __init__.py
      qdrant_store.py
      dense.py
      sparse.py
      hybrid.py

    rules/
      __init__.py
      engine.py
      data_categories.py
      architecture_patterns.py
      regulatory_triggers.py
      controls.py

    generation/
      __init__.py
      prompts.py
      renderer.py

    agents/
      __init__.py
      state.py
      graph.py
      nodes.py

    evaluation/
      __init__.py
      datasets.py
      metrics.py
      run_eval.py

  data/
    raw/
      laws/
      architecture_cards/
    processed/
    eval/

  tests/
    test_health.py
    test_architecture_extraction.py
    test_rule_engine.py
    test_chunking.py

  docs/
    architecture.md
    corpus.md
    roadmap.md

  docker-compose.yml
  pyproject.toml
  README.md
  handoff.md
  .env.example
```

---

## 7. Core Data Models

Implement Pydantic models first. These models are the contract of the system.

### 7.1 ArchitectureProfile

```python
from enum import Enum
from pydantic import BaseModel, Field


class Exposure(str, Enum):
    public_internet = "public_internet"
    vpn = "vpn"
    internal_network = "internal_network"
    closed_contour = "closed_contour"
    hybrid = "hybrid"
    unknown = "unknown"


class ArchitectureType(str, Enum):
    public_website = "public_website"
    public_saas = "public_saas"
    b2b_saas = "b2b_saas"
    internal_service = "internal_service"
    mobile_backend = "mobile_backend"
    integration_api = "integration_api"
    dwh_bi = "dwh_bi"
    ml_ai_pipeline = "ml_ai_pipeline"
    payment_service = "payment_service"
    edo_signature_service = "edo_signature_service"
    unknown = "unknown"


class DataCategory(str, Enum):
    personal_data = "personal_data"
    special_personal_data = "special_personal_data"
    biometric_personal_data = "biometric_personal_data"
    authentication_secret = "authentication_secret"
    payment_data = "payment_data"
    commercial_secret = "commercial_secret"
    telemetry_logs = "telemetry_logs"
    behavioral_data = "behavioral_data"
    documents = "documents"
    source_code = "source_code"
    unknown = "unknown"


class StorageLocation(str, Enum):
    russia = "russia"
    foreign = "foreign"
    mixed = "mixed"
    unknown = "unknown"


class IntegrationType(str, Enum):
    payment_provider = "payment_provider"
    email_provider = "email_provider"
    sms_provider = "sms_provider"
    analytics = "analytics"
    observability = "observability"
    llm_provider = "llm_provider"
    crm = "crm"
    edo = "edo"
    government_system = "government_system"
    unknown = "unknown"


class Integration(BaseModel):
    name: str | None = None
    type: IntegrationType = IntegrationType.unknown
    sends_personal_data: bool | None = None
    location: StorageLocation = StorageLocation.unknown
    notes: str | None = None


class AdminAccess(BaseModel):
    exists: bool | None = None
    exposed_to_internet: bool | None = None
    mfa_enabled: bool | None = None
    audit_log_enabled: bool | None = None
    role_based_access: bool | None = None


class ArchitectureProfile(BaseModel):
    source_description: str

    architecture_type: ArchitectureType = ArchitectureType.unknown
    exposure: Exposure = Exposure.unknown

    users: list[str] = Field(default_factory=list)
    data_categories: list[DataCategory] = Field(default_factory=list)
    raw_data_items: list[str] = Field(default_factory=list)

    storage_location: StorageLocation = StorageLocation.unknown
    integrations: list[Integration] = Field(default_factory=list)

    admin_access: AdminAccess = Field(default_factory=AdminAccess)

    has_payments: bool | None = None
    has_electronic_signature: bool | None = None
    has_ml_or_ai_processing: bool | None = None
    has_logs_or_observability: bool | None = None
    has_backups: bool | None = None
    serves_kii_subject: bool | None = None
    serves_government: bool | None = None

    unknowns: list[str] = Field(default_factory=list)
```

### 7.2 ComplianceAssessment

```python
from enum import Enum
from pydantic import BaseModel, Field


class Confidence(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Severity(str, Enum):
    info = "info"
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class RegulatoryTrigger(BaseModel):
    id: str
    title: str
    description: str
    basis: list[str] = Field(default_factory=list)
    confidence: Confidence = Confidence.medium
    reason: str | None = None


class RedFlag(BaseModel):
    id: str
    title: str
    description: str
    severity: Severity = Severity.medium
    reason: str | None = None


class RecommendedControl(BaseModel):
    id: str
    title: str
    description: str
    priority: Severity = Severity.medium
    related_triggers: list[str] = Field(default_factory=list)


class ClarificationQuestion(BaseModel):
    id: str
    question: str
    reason: str
    related_triggers: list[str] = Field(default_factory=list)


class LegalCitation(BaseModel):
    document_title: str
    document_type: str | None = None
    article: str | None = None
    part: str | None = None
    point: str | None = None
    quote: str | None = None
    source: str | None = None
    chunk_id: str | None = None


class ComplianceAssessment(BaseModel):
    architecture_profile: ArchitectureProfile

    summary: str
    regulatory_triggers: list[RegulatoryTrigger] = Field(default_factory=list)
    red_flags: list[RedFlag] = Field(default_factory=list)
    recommended_controls: list[RecommendedControl] = Field(default_factory=list)
    clarification_questions: list[ClarificationQuestion] = Field(default_factory=list)
    citations: list[LegalCitation] = Field(default_factory=list)

    needs_human_security_review: bool = True
    needs_human_legal_review: bool = True

    disclaimer: str
```

---

## 8. Deterministic Rule Engine

Implement a simple rule engine before implementing RAG.

File:

```text
app/rules/engine.py
```

The rule engine should accept an `ArchitectureProfile` and return partial `ComplianceAssessment`.

### 8.1 Required MVP Rules

#### Rule: personal data detected

If data contains:

* email;
* phone;
* ФИО;
* name;
* address;
* passport;
* IP;
* cookie;
* device id;
* user account;
* support messages tied to user;

then add:

```text
data_category: personal_data
trigger: personal_data_processing
basis: 152-ФЗ
```

#### Rule: public SaaS with users

If architecture is public SaaS or B2B SaaS and personal data is detected:

Add triggers:

```text
personal_data_processing
possible_ispdn
privacy_policy_required
security_measures_required
```

Add clarification questions:

```text
Где физически хранятся персональные данные?
Уведомлялся ли Роскомнадзор об обработке ПДн?
Какие цели обработки определены?
Есть ли политика обработки персональных данных?
Какие роли имеют доступ к ПДн?
```

#### Rule: external integrations

If integrations include email provider, sms provider, analytics, observability, CRM, LLM provider:

Add red flags if sends_personal_data is true or unknown:

```text
external_processor_or_transfer_unknown
possible_cross_border_transfer
personal_data_in_third_party_services
```

Add questions:

```text
Передаются ли персональные данные во внешний сервис?
Где расположен внешний сервис?
Есть ли договор/поручение обработки?
Можно ли отключить передачу ПДн?
```

#### Rule: observability/logging

If logs/observability exists:

Add red flag:

```text
possible_personal_data_in_logs
```

Add controls:

```text
mask_personal_data_in_logs
restrict_observability_access
set_log_retention_policy
```

#### Rule: admin panel exposed

If admin access exists and exposed_to_internet is true:

Add red flag:

```text
internet_exposed_admin_panel
```

If MFA is false or unknown:

Add red flag:

```text
admin_mfa_missing_or_unknown
```

Add controls:

```text
enable_mfa
restrict_admin_by_vpn_or_ip
enable_admin_audit_log
role_based_access_control
```

#### Rule: payments

If has_payments is true:

Add trigger:

```text
payment_regulation_possible
basis: 161-ФЗ / Bank of Russia / payment provider requirements
```

Add question:

```text
Кто является платёжным провайдером?
Хранит ли сервис платёжные данные или только получает статусы платежей?
```

#### Rule: electronic signature

If has_electronic_signature is true:

Add trigger:

```text
electronic_signature_regulation
basis: 63-ФЗ
```

Add questions:

```text
Какой тип электронной подписи используется?
Есть ли юридически значимые действия?
Как фиксируется волеизъявление пользователя?
```

#### Rule: commercial secret

If raw data or description contains:

* customer database;
* internal analytics;
* source code;
* financial reports;
* business reports;
* technical documentation;
* коммерческая тайна;

Add trigger:

```text
commercial_secret_possible
basis: 98-ФЗ
```

Add controls:

```text
classify_sensitive_business_data
restrict_access_to_commercial_secret
audit_access_to_sensitive_documents
```

#### Rule: KII

If serves_kii_subject is true or description mentions:

* КИИ;
* critical infrastructure;
* банк;
* энергетика;
* связь;
* транспорт;
* госорган;
* промышленность;
* healthcare infrastructure;

Add trigger:

```text
kii_relevance_possible
basis: 187-ФЗ
```

Add:

```text
needs_human_security_review = true
```

And question:

```text
Является ли заказчик субъектом КИИ? Является ли система значимым объектом КИИ или частью такого объекта?
```

---

## 9. Architecture Extraction

For MVP, implement a heuristic extractor first.

File:

```text
app/rules/architecture_patterns.py
```

Function:

```python
def extract_architecture_profile(description: str) -> ArchitectureProfile:
    ...
```

It should detect basic keywords in Russian and English.

### 9.1 Keyword examples

Personal data keywords:

```text
email, e-mail, почта, телефон, ФИО, имя, фамилия, паспорт, адрес, ip, cookie, куки, device id, пользователь, аккаунт, личный кабинет
```

Architecture keywords:

```text
SaaS, B2B, личный кабинет, админка, публичный сайт, интернет, VPN, закрытый контур, DMZ, API, webhook, мобильное приложение
```

Integration keywords:

```text
Sentry, Grafana, Prometheus, ELK, Datadog, observability, аналитика, Метрика, Google Analytics, email provider, SMS, CRM, LLM, OpenAI, YandexGPT, платежный провайдер
```

Security keywords:

```text
MFA, 2FA, аудит, audit log, RBAC, роли, шифрование, backup, резервные копии, секреты
```

Payment keywords:

```text
оплата, платежи, эквайринг, чек, касса, банк, перевод, платёжный провайдер
```

Electronic signature keywords:

```text
электронная подпись, ЭП, УКЭП, НЭП, ПЭП, ЭДО, подписывает документ, юридически значимый
```

KII keywords:

```text
КИИ, критическая информационная инфраструктура, значимый объект, субъект КИИ
```

### 9.2 Do not over-optimize

This extractor can be imperfect. It is a bootstrap layer.

Later it can be replaced or improved with LLM structured extraction.

---

## 10. API Endpoints

### 10.1 Health

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

### 10.2 Analyze Architecture

```http
POST /analyze
```

Request:

```json
{
  "description": "У нас B2B SaaS. Пользователи регистрируются по email и телефону. База в РФ. Логи уходят в Sentry. Админка доступна из интернета, MFA пока нет."
}
```

Response:

```json
{
  "architecture_profile": {
    "architecture_type": "b2b_saas",
    "exposure": "public_internet",
    "data_categories": ["personal_data", "telemetry_logs"],
    "raw_data_items": ["email", "phone"],
    "storage_location": "russia",
    "has_logs_or_observability": true
  },
  "summary": "...",
  "regulatory_triggers": [],
  "red_flags": [],
  "recommended_controls": [],
  "clarification_questions": [],
  "citations": [],
  "needs_human_security_review": true,
  "needs_human_legal_review": true,
  "disclaimer": "..."
}
```

### 10.3 Search Corpus

```http
POST /search
```

Request:

```json
{
  "query": "требования к защите персональных данных в ИСПДн",
  "top_k": 5
}
```

For the first milestone this can return stubbed results or results from local Markdown documents.

### 10.4 Ingest Documents

```http
POST /documents/ingest
```

This can be implemented later. For MVP, it is acceptable to have a CLI ingestion command instead.

---

## 11. Legal / Security Corpus

Create initial local Markdown files in:

```text
data/raw/laws/
```

Do not scrape the internet in the first milestone.

Use manually prepared short excerpts or summaries with metadata.

Recommended files:

```text
data/raw/laws/152fz_personal_data.md
data/raw/laws/149fz_information.md
data/raw/laws/63fz_electronic_signature.md
data/raw/laws/98fz_commercial_secret.md
data/raw/laws/187fz_kii.md
data/raw/laws/pp1119_personal_data_security.md
data/raw/laws/fstec21_personal_data_controls.md
data/raw/laws/fsb378_crypto_personal_data.md
```

Each file should have frontmatter:

```markdown
---
document_title: "Федеральный закон 152-ФЗ «О персональных данных»"
document_type: "federal_law"
domain: "personal_data"
source: "official"
version_note: "manual excerpt for MVP"
---

# ...
```

For MVP, the system can retrieve from these local files.

Later we will add official source downloading and version tracking.

---

## 12. Architecture Cards Corpus

Create local architecture knowledge cards:

```text
data/raw/architecture_cards/public_website.md
data/raw/architecture_cards/public_saas.md
data/raw/architecture_cards/b2b_saas.md
data/raw/architecture_cards/internal_service.md
data/raw/architecture_cards/hybrid_public_private.md
data/raw/architecture_cards/integration_api.md
data/raw/architecture_cards/observability_stack.md
data/raw/architecture_cards/support_backoffice.md
data/raw/architecture_cards/ml_ai_pipeline.md
data/raw/architecture_cards/payment_service.md
data/raw/architecture_cards/edo_signature_service.md
data/raw/architecture_cards/kii_client_service.md
```

Example card:

```markdown
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
```

---

## 13. Retrieval MVP

Implement a simple local retrieval first.

Preferred first step:

* load Markdown files;
* split by headings;
* store chunks in memory;
* keyword score using simple matching or BM25 library if easy;
* return top-k chunks.

Qdrant can be added in the next milestone.

Do not block the MVP on embeddings.

### 13.1 Chunk model

```python
class DocumentChunk(BaseModel):
    chunk_id: str
    document_title: str
    document_type: str | None = None
    source_path: str
    heading: str | None = None
    text: str
    metadata: dict = Field(default_factory=dict)
```

### 13.2 Retriever interface

```python
class Retriever(Protocol):
    def search(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        ...
```

### 13.3 RetrievedChunk

```python
class RetrievedChunk(BaseModel):
    chunk: DocumentChunk
    score: float
    match_reason: str | None = None
```

---

## 14. Generation MVP

For the first milestone, do not require an LLM.

Implement a deterministic renderer:

```text
app/generation/renderer.py
```

It should turn `ComplianceAssessment` into a readable Markdown report.

Function:

```python
def render_assessment_markdown(assessment: ComplianceAssessment) -> str:
    ...
```

Output sections:

```markdown
# Preliminary IT Compliance Assessment

## Summary

## Detected architecture profile

## Regulatory triggers

## Red flags

## Recommended controls

## Clarification questions

## Sources / citations

## Disclaimer
```

Later this renderer can be replaced or augmented with LLM generation.

---

## 15. Testing Requirements

Add tests for:

### 15.1 Health endpoint

```text
GET /health returns {"status": "ok"}
```

### 15.2 Architecture extraction

Input:

```text
У нас B2B SaaS, пользователи регистрируются по email и телефону. Админка доступна из интернета. MFA нет. Логи уходят в Sentry.
```

Expected:

* architecture_type = b2b_saas
* exposure = public_internet
* data_categories contains personal_data
* raw_data_items contains email and phone
* has_logs_or_observability = true
* admin_access.exists = true
* admin_access.exposed_to_internet = true
* admin_access.mfa_enabled = false

### 15.3 Rule engine

Same input should produce:

* personal_data_processing trigger
* possible_ispdn trigger
* possible_personal_data_in_logs red flag
* internet_exposed_admin_panel red flag
* admin_mfa_missing_or_unknown red flag
* enable_mfa recommended control
* mask_personal_data_in_logs recommended control

### 15.4 Renderer

Renderer should include:

* Summary
* Red flags
* Recommended controls
* Disclaimer

---

## 16. First Milestone Tasks

Implement in this order.

### Task 1: Project skeleton

Create:

* `pyproject.toml`
* FastAPI app
* `/health`
* Docker Compose with API service
* basic README

Acceptance:

```bash
docker compose up
curl localhost:8000/health
```

returns:

```json
{"status":"ok"}
```

### Task 2: Core models

Create Pydantic models:

* `ArchitectureProfile`
* `ComplianceAssessment`
* all enums and nested models.

Acceptance:

```bash
pytest
```

passes model import tests.

### Task 3: Heuristic architecture extractor

Implement:

```python
extract_architecture_profile(description: str) -> ArchitectureProfile
```

Acceptance:

* test case from section 15.2 passes.

### Task 4: Rule engine

Implement:

```python
analyze_profile(profile: ArchitectureProfile) -> ComplianceAssessment
```

Acceptance:

* test case from section 15.3 passes.

### Task 5: `/analyze` endpoint

Implement:

```http
POST /analyze
```

Acceptance:

* endpoint returns valid `ComplianceAssessment`.

### Task 6: Markdown renderer

Implement:

```python
render_assessment_markdown(assessment: ComplianceAssessment) -> str
```

Optional endpoint:

```http
POST /analyze/markdown
```

Acceptance:

* returns readable Markdown report.

### Task 7: Local corpus loader

Implement Markdown loading from:

```text
data/raw/laws/
data/raw/architecture_cards/
```

Acceptance:

* chunks are loaded;
* simple search returns relevant chunks by keyword.

### Task 8: Add citations to assessment

Use retrieval results to attach relevant citations for triggers.

Acceptance:

* if trigger is `personal_data_processing`, include citation from 152-ФЗ local Markdown file;
* if trigger is `electronic_signature_regulation`, include citation from 63-ФЗ local Markdown file;
* if trigger is `commercial_secret_possible`, include citation from 98-ФЗ local Markdown file.

---

## 17. Example Input and Expected Output

### Input

```json
{
  "description": "У нас B2B SaaS для клиентов. Пользователи регистрируются по email и телефону. Есть личный кабинет и админка. Админка доступна из интернета, MFA пока нет. База данных находится в российском облаке. Логи ошибок отправляются в Sentry, туда может попадать email пользователя. Есть платежный провайдер для оплаты подписки."
}
```

### Expected high-level output

```json
{
  "architecture_profile": {
    "architecture_type": "b2b_saas",
    "exposure": "public_internet",
    "data_categories": [
      "personal_data",
      "telemetry_logs",
      "payment_data"
    ],
    "raw_data_items": [
      "email",
      "phone"
    ],
    "storage_location": "russia",
    "has_payments": true,
    "has_logs_or_observability": true,
    "admin_access": {
      "exists": true,
      "exposed_to_internet": true,
      "mfa_enabled": false
    }
  },
  "regulatory_triggers": [
    {
      "id": "personal_data_processing",
      "basis": ["152-ФЗ"]
    },
    {
      "id": "possible_ispdn",
      "basis": ["152-ФЗ", "ПП РФ №1119", "Приказ ФСТЭК №21"]
    },
    {
      "id": "payment_regulation_possible",
      "basis": ["161-ФЗ", "Bank of Russia requirements"]
    }
  ],
  "red_flags": [
    {
      "id": "possible_personal_data_in_logs"
    },
    {
      "id": "internet_exposed_admin_panel"
    },
    {
      "id": "admin_mfa_missing_or_unknown"
    }
  ],
  "recommended_controls": [
    {
      "id": "enable_mfa"
    },
    {
      "id": "mask_personal_data_in_logs"
    },
    {
      "id": "restrict_admin_by_vpn_or_ip"
    },
    {
      "id": "enable_admin_audit_log"
    }
  ],
  "needs_human_security_review": true,
  "needs_human_legal_review": true
}
```

---

## 18. Coding Style

Prefer:

* small pure functions;
* typed Pydantic models;
* deterministic tests;
* no hidden network calls;
* no scraping in MVP;
* no hard dependency on paid LLM API;
* readable code over clever abstractions.

Avoid:

* implementing complex LangGraph agent before deterministic MVP;
* mixing legal corpus parsing with architecture extraction;
* putting all logic in FastAPI routes;
* returning unstructured strings where a model is expected;
* making strong legal claims without citations.

---

## 19. Future Milestones

After the deterministic MVP works:

### Milestone 2: Qdrant retrieval

* add Qdrant to Docker Compose;
* add embeddings;
* index law and architecture cards;
* implement dense retrieval;
* implement hybrid retrieval later.

### Milestone 3: LLM structured extraction

* replace heuristic extractor with LLM-based structured extraction;
* keep heuristic extractor as fallback;
* validate LLM output against Pydantic schema.

### Milestone 4: Agentic workflow

Add LangGraph:

```text
description
  -> extract_profile
  -> detect_triggers
  -> retrieve_legal_basis
  -> generate_assessment
  -> check_grounding
  -> ask_clarification_or_finalize
```

### Milestone 5: Evaluation

Build a small golden dataset:

* 20 architecture descriptions;
* expected data categories;
* expected triggers;
* expected red flags;
* expected controls.

Measure:

* trigger precision;
* trigger recall;
* citation coverage;
* false positive rate;
* false negative rate.

---

## 20. Current Priority

Start with Milestone 1 only.

Do not implement LangGraph, Qdrant, or LLM integration until the following works:

```text
description -> ArchitectureProfile -> RuleEngine -> ComplianceAssessment -> Markdown report
```

The first useful demo should run locally without any external API keys.
