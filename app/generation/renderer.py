"""Deterministic Markdown renderer for ComplianceAssessment."""

from app.models import ComplianceAssessment


def render_assessment_markdown(assessment: ComplianceAssessment) -> str:
    """Render a ComplianceAssessment as a readable Markdown report.

    No LLM required — pure string formatting.
    """
    sections: list[str] = []

    sections.append("# Preliminary IT Compliance Assessment\n")
    sections.append(_render_summary(assessment))
    sections.append(_render_profile(assessment))
    sections.append(_render_triggers(assessment))
    sections.append(_render_red_flags(assessment))
    sections.append(_render_controls(assessment))
    sections.append(_render_questions(assessment))
    sections.append(_render_citations(assessment))
    sections.append(_render_human_review(assessment))
    sections.append(_render_disclaimer(assessment))

    return "\n".join(sections)


def _render_summary(a: ComplianceAssessment) -> str:
    return f"## Summary\n\n{a.summary}\n"


def _render_profile(a: ComplianceAssessment) -> str:
    p = a.architecture_profile
    lines = ["## Detected architecture profile\n"]
    lines.append(f"- **Architecture type**: {p.architecture_type.value}")
    lines.append(f"- **Exposure**: {p.exposure.value}")
    lines.append(f"- **Storage location**: {p.storage_location.value}")

    if p.data_categories:
        cats = ", ".join(c.value for c in p.data_categories)
        lines.append(f"- **Data categories**: {cats}")

    if p.raw_data_items:
        items = ", ".join(p.raw_data_items)
        lines.append(f"- **Raw data items**: {items}")

    if p.users:
        lines.append(f"- **Users**: {', '.join(p.users)}")

    admin = p.admin_access
    if admin.exists is not None:
        lines.append(f"- **Admin panel**: {'yes' if admin.exists else 'no'}")
        if admin.exists:
            if admin.exposed_to_internet is not None:
                lines.append(
                    f"  - Exposed to internet: {'yes' if admin.exposed_to_internet else 'no'}"
                )
            if admin.mfa_enabled is not None:
                lines.append(f"  - MFA: {'enabled' if admin.mfa_enabled else 'disabled'}")

    if p.integrations:
        lines.append("- **Integrations**:")
        for integration in p.integrations:
            name = integration.name or integration.type.value
            lines.append(f"  - {name} ({integration.type.value})")

    lines.append("")
    return "\n".join(lines)


def _render_triggers(a: ComplianceAssessment) -> str:
    if not a.regulatory_triggers:
        return "## Regulatory triggers\n\nNo regulatory triggers detected.\n"

    lines = ["## Regulatory triggers\n"]
    for trigger in a.regulatory_triggers:
        lines.append(f"### {trigger.id}")
        lines.append(f"- **Title**: {trigger.title}")
        lines.append(f"- **Description**: {trigger.description}")
        lines.append(f"- **Basis**: {', '.join(trigger.basis)}")
        lines.append(f"- **Confidence**: {trigger.confidence.value}")
        if trigger.reason:
            lines.append(f"- **Reason**: {trigger.reason}")
        lines.append("")

    return "\n".join(lines)


def _render_red_flags(a: ComplianceAssessment) -> str:
    if not a.red_flags:
        return "## Red flags\n\nNo red flags detected.\n"

    lines = ["## Red flags\n"]
    for flag in a.red_flags:
        lines.append(f"### {flag.id}")
        lines.append(f"- **Title**: {flag.title}")
        lines.append(f"- **Description**: {flag.description}")
        lines.append(f"- **Severity**: {flag.severity.value}")
        if flag.reason:
            lines.append(f"- **Reason**: {flag.reason}")
        lines.append("")

    return "\n".join(lines)


def _render_controls(a: ComplianceAssessment) -> str:
    if not a.recommended_controls:
        return "## Recommended controls\n\nNo recommended controls.\n"

    lines = ["## Recommended controls\n"]
    for control in a.recommended_controls:
        lines.append(f"### {control.id}")
        lines.append(f"- **Title**: {control.title}")
        lines.append(f"- **Description**: {control.description}")
        lines.append(f"- **Priority**: {control.priority.value}")
        if control.related_triggers:
            lines.append(f"- **Related triggers**: {', '.join(control.related_triggers)}")
        lines.append("")

    return "\n".join(lines)


def _render_questions(a: ComplianceAssessment) -> str:
    if not a.clarification_questions:
        return "## Clarification questions\n\nNo clarification questions.\n"

    lines = ["## Clarification questions\n"]
    for question in a.clarification_questions:
        lines.append(f"### {question.id}")
        lines.append(f"- **Question**: {question.question}")
        lines.append(f"- **Reason**: {question.reason}")
        if question.related_triggers:
            lines.append(f"- **Related triggers**: {', '.join(question.related_triggers)}")
        lines.append("")

    return "\n".join(lines)


def _render_citations(a: ComplianceAssessment) -> str:
    if not a.citations:
        return "## Sources / citations\n\nNo citations available.\n"

    lines = ["## Sources / citations\n"]
    for citation in a.citations:
        lines.append(f"- **{citation.document_title}**")
        if citation.document_type:
            lines.append(f"  - Type: {citation.document_type}")
        if citation.article:
            lines.append(f"  - Article: {citation.article}")
        if citation.part:
            lines.append(f"  - Part: {citation.part}")
        if citation.point:
            lines.append(f"  - Point: {citation.point}")
        if citation.quote:
            lines.append(f"  - Quote: {citation.quote}")
        lines.append("")

    return "\n".join(lines)


def _render_human_review(a: ComplianceAssessment) -> str:
    lines = ["## Human review\n"]
    lines.append(
        f"- **Human security review required**: {'yes' if a.needs_human_security_review else 'no'}"
    )
    lines.append(
        f"- **Human legal review required**: {'yes' if a.needs_human_legal_review else 'no'}"
    )
    lines.append("")
    return "\n".join(lines)


def _render_disclaimer(a: ComplianceAssessment) -> str:
    return f"## Disclaimer\n\n{a.disclaimer}\n"
