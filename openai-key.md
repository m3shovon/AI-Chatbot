
```
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
```

```
pip install openai
```

```
from openai import OpenAI

client = OpenAI(
  api_key="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"
)

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": "write a haiku about ai"}
  ]
)

print(completion.choices[0].message);

```