import anthropic


client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=256,
    messages=[
        {
            "role": "user",
            "content": "Recommend one science fiction movie to someone who loved Interstellar.",
        }
    ],
)

print(response.content[0].text)
