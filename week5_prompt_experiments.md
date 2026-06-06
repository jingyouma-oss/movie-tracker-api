## Week 5 Prompt Engineering Notes

### Experiment 1: More opinionated assistant
System prompt idea:

```text
You are Marcus, a passionate and opinionated film professor with strong views about movies. You are enthusiastic, sharp, and a little dramatic.
```

Observed effect:
- Responses felt more expressive and more personality-driven.
- Recommendations sounded bolder, but sometimes less neutral.

### Experiment 2: More structured output
System prompt idea:

```text
When recommending movies, always format your response as:
**Title** by Director
Why: One sentence explaining why it fits the user's taste.

Give exactly 3 recommendations unless asked for a different number.
```

Observed effect:
- Responses became easier to read and compare.
- The structure was better for screenshots and grading.

### Experiment 3: More constrained assistant
System prompt idea:

```text
You are a movie assistant. You ONLY discuss movies and watching recommendations.
If asked about anything else, politely redirect the user back to movies.
```

Observed effect:
- The assistant stayed on-topic and was less likely to drift.
- This worked best for a focused app experience.

### Final choice
The final prompt kept a friendly but concise assistant because it felt most natural for a personal movie tracker while still giving clear, useful answers.
