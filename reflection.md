## Week 5 Reflection

1. The system prompt defines the assistant's role, tone, and boundaries, while the user message contains the specific request for that turn. The separation matters because the system prompt creates consistent behavior across the whole conversation, and the user message should not have to restate the rules every time.

2. When I changed the system prompt, the same question produced noticeably different answers in tone, structure, and specificity. What surprised me most was how strongly a short instruction could change the assistant from a casual movie guide into a structured recommender with a very different voice.

3. One harmful situation would be an AI app giving overconfident or misleading advice and presenting it like fact. I would mitigate that by limiting the scope of the assistant, keeping responses concise, grounding recommendation prompts in the user's saved data, and showing a clear note that AI suggestions may be imperfect.

4. If I had unlimited Claude API credits, I would add an AI feature that generates personalized "what to watch next" queues every time the movie library changes. Technically, I would trigger a backend job after movie or review updates, summarize the user's preferences from ratings, genres, directors, and reviews, then store an AI-generated recommendation queue in PostgreSQL so the frontend could load it instantly.
