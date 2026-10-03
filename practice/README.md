# Practice material

`specs/entropy.json` and `specs/attention.json` are hand-written reference specs for the two public mechanisms in the brief. They let the team test the renderer and checker before spending model calls. Production code must not branch on these papers.

`cases/` contains four additional small mechanisms. All six linked sources are currently readable through the agent fetch path. The `excerpt` fields are explicitly labeled paraphrases: Bayes uses a modern conjugate-model extension, and the other cases simplify equations from the cited papers. They are stress-test inputs, not quotations or claims that the toy examples reproduce experimental results. Keep that distinction visible in generated pages.

`oracles/core_identities.json` records small calculations for all six cases independently of generated spec tests. During browser review, enter the listed inputs and compare intermediate values as well as final results; this catches a page that passes its own self-tests while teaching the wrong calculation.

