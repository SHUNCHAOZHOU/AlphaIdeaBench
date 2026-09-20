Extract the novelty-related remarks from the {{ reviews | length }} review{{ "s" if reviews | length > 1 else "" }} below.

Paper ID: {{ paper_id }}

{% if reviews | length > 1 -%}
These are {{ reviews | length }} independent reviews of the same paper. Keep them apart:
attribute every quote to its own reviewer, and do not merge points that several reviewers
happen to share.
{%- else -%}
This is the only review you are given. Extract what this one reviewer said; the absence of
other reviews is not a reason to speculate.
{%- endif %}

## Title

{{ title }}

## Abstract

{{ abstract }}

## Review{{ "s" if reviews | length > 1 else "" }}

{% for r in reviews %}
### {{ r.label }}
{% if r.rating is not none %}
Rating: {{ r.rating }} (venue scale) — Reviewer confidence: {{ r.confidence }}
{% endif %}
#### Summary

{{ r.summary | default("(none)", true) }}

#### Strengths

{{ r.strengths | default("(none)", true) }}

#### Weaknesses

{{ r.weaknesses | default("(none)", true) }}
{% if r.body %}
#### Further comments

{{ r.body }}
{% endif %}
{% endfor %}

Use exactly these reviewer labels: {{ reviews | map(attribute="label") | join(", ") }}.
