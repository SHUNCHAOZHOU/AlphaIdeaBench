Map the human review{{ "s" if reviews | length > 1 else "" }} below onto the AlphaIdeaBench dimensions.

Paper ID: {{ paper_id }}
{% if reviews | length > 1 -%}
You are given {{ reviews | length }} independent reviews of this paper. Produce one merged
judgement per dimension. Where the reviewers disagree, weigh the better-argued position and
record the split in `disagreement`.
{%- else -%}
You are given a single review. Judge only what this one reviewer expressed; the other reviews
of this paper are not your concern, and their absence is not a reason to guess.
{%- endif %}

The paper's title and abstract are context for reading the reviews. They tell you what the
reviewers are talking about. They are not evidence on their own: do not score a dimension
from the abstract alone.

## Title

{{ title }}

## Abstract

{{ abstract }}

## Review{{ "s" if reviews | length > 1 else "" }}

{% for r in reviews %}
{% if reviews | length > 1 %}
### {{ r.label }}
{% endif %}
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
