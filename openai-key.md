
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