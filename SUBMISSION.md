# Submission handoff

Repository: https://github.com/AmzBG/agentic-systems-hackathon

Run with Python3.11 and the pinned requirements:

```text
python agent.py --input case.json --output out --model deepseek/deepseek-v4.1-flash
```

No separate server, compiler or system-package setup. Set OPENROUTER_API_KEY securely.
Single flow, reasoning auto resolves low; bounded truncation recovery may disable
reasoning. Hard limits: ten requests, thirty thousand completion tokens including
reasoning, ten minutes per run. Prompt tokens count toward measured efficiency.

Both public examples have tracked input/HTML/trace pairs and generation provenance.
Original failures and repair costs remain in evidence. Five live runs at production
14a5eaafc472a65b619e44db3db17016e57b0d0b passed validator and91 independent numerical
trials; this is historical evidence for the final prompt correction, not a fresh
generation claim. FINAL_RELEASE.md records actual browser scope and residual defects.

Final five-minute correction removes a contradictory prompt instruction that
discarded the learning brief alongside untrusted source commands. Scientific brief
requirements now remain binding within schema/safety rules, while source injection
and any request to override those rules remain rejected. Generation, planning and
repair use the same distinction. Focused regressions verify the message contract;
the effect on live generated prose is **unmeasured**, with no new paid calls.

Technically prepared for submission with documented limitations, not certified
free of scientific prose errors. Fully network-disabled verification remains
unverified for User3's latest fresh pages; separate U2offline evidence remains
scoped to its recorded renderer/artifacts. No claim of guaranteed grade.

Use the final full commit SHA reported after the clean verification and push;
do not submit an earlier evidence-producing SHA as the current implementation.
