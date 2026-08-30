from alphaideabench.core.jsonutil import extract_json_object


def test_plain_object():
    assert extract_json_object('{"score": 4}') == {"score": 4}


def test_fenced_and_prose():
    text = """Here is the judgment.

```json
{"dimension_id": "testability", "score": 2, "reasoning": "no metric"}
```
thanks
"""
    parsed = extract_json_object(text)
    assert parsed is not None
    assert parsed["score"] == 2


def test_invalid():
    assert extract_json_object("no json here") is None
