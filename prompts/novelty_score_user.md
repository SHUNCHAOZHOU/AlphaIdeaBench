Score the four novelty facets from the extracted reviewer remarks below.

Paper ID: {{ paper_id }}
{% if n_reviewers > 1 %}
These remarks come from {{ n_reviewers }} independent reviewers, named on each remark. Points
that several reviewers raised separately were kept separate on purpose.
{% else %}
These remarks come from a single reviewer.
{% endif %}
{% for facet in facets %}
## {{ facet.dimension_id }}

{% if facet.remarks -%}
{% for r in facet.remarks %}
{{ loop.index }}. [{{ r.reviewer }}] [{{ r.stance }}]
   Quote: "{{ r.quote }}"
   {% if r.note %}Note: {{ r.note }}{% endif %}
{% endfor %}
{%- else -%}
(no remarks — the reviewers did not speak to this facet)
{%- endif %}
{% endfor %}
{% if disagreement %}
## Noted disagreement between reviewers

{{ disagreement }}
{% endif %}
{% if overall_notes %}
## Notes from the extraction step

{{ overall_notes }}
{% endif %}
