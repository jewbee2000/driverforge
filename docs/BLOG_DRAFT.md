# Making an instrument driver earn my trust

Unpublished prospective draft. Implementation and results are pending.


There is something funny about instrument software: getting a number back can feel like success long before you know whether it is the right number. A temperature of 643.02 is a perfectly respectable floating-point value. It is less respectable if the device meant -12.34.

My work has involved enough hardware interfaces that this seemed like an interesting place to experiment with AI coding agents. The initial appeal is obvious. A protocol manual contains a lot of tedious information that needs to become code. But the tedious parts are also where the mistakes hide: a signed register, a unit conversion, an acknowledgment that never arrives.

I want to build a small tool called DriverForge around this problem. The first version uses two fictional instruments, so the entire example can live in a public repository. One speaks a simple text protocol, and the other exposes a few registers. The interesting part is the loop between the written specification, the generated driver, and a separate program that checks what actually goes across the wire.

I am deliberately making the checking program a little annoying. It will return negative temperatures, truncate responses, delay acknowledgments, and tell the driver that something went wrong. If a command changes an output and the acknowledgment disappears, sending the command again is a decision with consequences. I want that decision to appear in the specification instead of being hidden in a generic retry decorator.

This gives the coding agent a useful kind of feedback. A failed check should point to an actual disagreement about behavior. The agent can then propose a repair, but the definition of success stays outside the code it is repairing.

I am interested in how much of the work this makes easier, and in what still requires judgment. My guess is that generating the happy path will be the least interesting part. Knowing when the manual is ambiguous may turn out to matter more than producing another hundred lines of plausible Python.

The intended result is a small repository that someone can clone and run without owning either instrument or buying access to an AI service. A recorded example will show the checking loop; any live model results will be reported separately. Once the implementation exists, I will add the actual failures, the fixes, and the cases where the agent needed help. Those seem more useful than a screenshot of code that looks correct.
