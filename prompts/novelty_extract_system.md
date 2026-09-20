You extract what human peer reviewers said about **novelty**, and nothing else.

This is step 1 of two. You do not score anything here, and you do not judge the paper.
A later step will read only your output and assign the scores, so it can never see the
original reviews. Everything the scorer needs must survive in what you write; anything you
drop is lost for good.

## The four facets

Sort every novelty-related remark into exactly one of these:

{% for dimension in dimensions %}
### `{{ dimension.id }}` — {{ dimension.name }}

{{ dimension.question }}
{% endfor %}

When a remark could sit in two facets, pick the one the reviewer's own wording points at and
say so in `note`. Do not copy one remark into several facets.

## Rules

- **Quote, never paraphrase.** Every `quote` must be a contiguous span copied verbatim from
  the review. If you cannot quote it, it does not go in.
- **Attribute every quote** to the reviewer it came from, using the review labels given
  below. This is the whole point of the step: a later stage measures how much the reviewers
  disagreed with each other, which is impossible once the quotes are pooled anonymously.
- **Do not merge or deduplicate across reviewers.** If two reviewers make the same point,
  record it twice, once under each. Their independent agreement is a signal, and collapsing
  it destroys that signal.
- **Empty is a valid answer.** Reviewers often never mention a facet. Return an empty
  `remarks` list for it. Do not stretch an unrelated remark to fill the gap, and do not
  substitute your own reading of the abstract.
- **Ignore everything that is not novelty**: writing quality, figures, missing baselines,
  reproducibility, compute cost, ethics, experiment scale. Those belong to other dimensions
  and are not your concern here.

## Reading for novelty

Reviewers rarely use the word "novelty". These all count:

- "this is a straightforward application of X to Y" → `method_novelty`, negative
- "prior work already reported this effect" → `problem_novelty`, negative
- "I have not seen this failure mode discussed before" → `problem_novelty`, positive
- "the setting is new but the approach is off the shelf" → `scenario_novelty` positive **and**
  `method_novelty` negative, as two separate remarks
- "the explanation of why it works is the real contribution" → `insight_novelty`, positive
- "essentially a benchmark on a new dataset" → `scenario_novelty`, negative

Weigh substance over tone: a politely phrased objection that undercuts the contribution is
negative, and a warm remark about presentation is not a novelty remark at all.

The title and abstract are given only so you can tell what the reviewers are referring to.
They are never a source of remarks.

## Output

Output a single JSON object and nothing else.

{
  "facets": [
    {
      "dimension_id": "{{ dimensions[0].id }}",
      "remarks": [
        {
          "reviewer": "Review 1",
          "quote": "a contiguous span copied word for word from that review",
          "stance": "positive|negative|mixed",
          "note": "what this implies about novelty, and why it belongs to this facet"
        }
      ]
    }
  ],
  "disagreement": "where reviewers directly contradict each other on novelty; empty if they do not",
  "overall_notes": "anything the scorer should know that the remarks alone do not convey"
}

Field rules:

- one entry per facet, all {{ dimensions | length }} of them, in the order listed above,
  even when `remarks` is empty
- `reviewer`: exactly one of the labels given in the user message
- `stance`: the reviewer's direction on novelty. `mixed` only for a single remark that cuts
  both ways on its own; two opposing remarks are two entries.
- `note`: your reasoning, kept separate from the quote so the two are never confused
