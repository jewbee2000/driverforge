# Blog brief and release criteria

Working title: **Making an instrument driver earn my trust**

Target length after implementation: 600–900 words. Audience: a technically curious reader who enjoys building things; not a job application reviewer addressed directly. Use first person, concrete engineering details, and mild humor when natural. Walter's bicycle-parts and couch-riser posts begin with a practical motivation and describe constraints plainly. Avoid a generic thought-leadership essay, copied phrases from other writers, inflated AI claims, or invented autobiographical stories.

The current draft is prospective. It is suitable as a starting point, not a finished retrospective. Convert future tense to past tense only when the referenced work exists. Preserve the honest distinction between Walter choosing/directing the project and an agent doing implementation work. The user has authorized first-person drafting, but personal beliefs or anecdotes beyond the supplied context remain suggestions for his review.

## Evidence to add after implementation

- One real screenshot or diagram of the project's result, with an explanatory caption.
- One specific failed candidate, what the independent check found, and the actual repair.
- One decision Walter or the agent made, its tradeoff, and whether it worked.
- The real command a reader can run, verified repository URL, and a link to the evidence report.
- What the project establishes and what remains untested. Any reported number must link to a recorded result.

Do not require a paid live-model campaign to write an honest post about building with Codex. Development evidence is meaningful in its own right. A replay demonstrates the evaluation mechanism, not model success. If live trials are added, include the denominator and failed attempts.

## Editorial handoff

Canonical editorial copy for this setup is the Jekyll file `_drafts/driverforge.md` in the accompanying website-drafts checkout. `docs/BLOG_DRAFT.md` is a convenience copy; after implementation, update the website draft and then sync this copy. Keep `published: false` until the actual project, links, and article are ready and publication is authorized. Set the article's publication date at that point, not in advance.

## Current draft


There is something funny about instrument software: getting a number back can feel like success long before you know whether it is the right number. A temperature of 643.02 is a perfectly respectable floating-point value. It is less respectable if the device meant -12.34.

My work has involved enough hardware interfaces that this seemed like an interesting place to experiment with AI coding agents. The initial appeal is obvious. A protocol manual contains a lot of tedious information that needs to become code. But the tedious parts are also where the mistakes hide: a signed register, a unit conversion, an acknowledgment that never arrives.

I want to build a small tool called DriverForge around this problem. The first version uses two fictional instruments, so the entire example can live in a public repository. One speaks a simple text protocol, and the other exposes a few registers. The interesting part is the loop between the written specification, the generated driver, and a separate program that checks what actually goes across the wire.

I am deliberately making the checking program a little annoying. It will return negative temperatures, truncate responses, delay acknowledgments, and tell the driver that something went wrong. If a command changes an output and the acknowledgment disappears, sending the command again is a decision with consequences. I want that decision to appear in the specification instead of being hidden in a generic retry decorator.

This gives the coding agent a useful kind of feedback. A failed check should point to an actual disagreement about behavior. The agent can then propose a repair, but the definition of success stays outside the code it is repairing.

I am interested in how much of the work this makes easier, and in what still requires judgment. My guess is that generating the happy path will be the least interesting part. Knowing when the manual is ambiguous may turn out to matter more than producing another hundred lines of plausible Python.

The intended result is a small repository that someone can clone and run without owning either instrument or buying access to an AI service. A recorded example will show the checking loop; any live model results will be reported separately. Once the implementation exists, I will add the actual failures, the fixes, and the cases where the agent needed help. Those seem more useful than a screenshot of code that looks correct.
