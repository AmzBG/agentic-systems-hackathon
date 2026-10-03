# Practice material

`specs/entropy.json` and `specs/attention.json` are hand-written reference specs for the two public mechanisms in the brief. They let the team test the renderer and checker before spending model calls. Production code must not branch on these papers.

`cases/` contains four additional small mechanisms. Some `excerpt` fields are explicitly labeled mathematical paraphrases because the linked historical source is not fully accessible in the development environment. These are stress-test inputs, not verified quotations from the papers. Keep that distinction visible in generated pages.

`oracles/core_identities.json` records small calculations made independently of the generated spec tests. Use those identities during browser review to catch a page that passes its own self-tests while teaching the wrong calculation.

