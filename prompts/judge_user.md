Review the idea below on the dimension **{{ dimension.name }}** (`{{ dimension.id }}`) only.

Topic ID: {{ topic.id }}
Idea ID: {{ idea.idea_id }}

To re-check anything, call load_topic / load_budget / load_idea / load_rubric.

## Topic (including budget)

{{ topic.to_markdown() }}

## Idea

{{ idea.to_markdown() }}
