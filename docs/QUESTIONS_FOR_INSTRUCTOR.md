# Questions for the instructor

These two points in the brief affect the ingestion contract and should be clarified before freezing the implementation.

1. The brief says `case.json` contains five required string fields, but names only `source_url`, `focus`, and `audience`. What are the other two field names and meanings?
2. The brief says assessment network access is limited to OpenRouter, while the agent is expected to retrieve `source_url`. Will paper URLs remain reachable, will an excerpt be supplied in one of the missing fields, or will sources be preloaded another way?

Until clarified, the loader requires the three named fields, accepts additional string fields, and recognizes `excerpt`, `source_text`, or `paper_excerpt` as optional supplied source text.

