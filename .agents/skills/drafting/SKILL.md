---
name: drafting
description: Draft a design yourself - research the facts, make the technical calls, explain each one, and put to the user only what they alone can answer. Use when the user wants the design worked out for them instead of being interviewed about it.
---

# Drafting

Work the design out yourself and present it.
The user is the owner, not the domain expert - do not interview them as if the knowledge were theirs to supply.
Nothing is canon when the session ends unless they say so.

## Own the work

Find the facts yourself: the codebase, `CONTEXT.md`, the ADRs, and primary sources (use the `research` skill for anything that needs reading outside the repo).
Never ask the user for something you could look up.
If what you find kills the premise - the codebase already solves this another way, or a fact makes the approach impossible - stop and report that, instead of designing around it.

Then make the calls you are more competent to make: libraries and tools, file layout, schema and interface details, error handling, test strategy, naming inside the code, algorithms, the order of the work.
Design it twice before you settle - carry the option you rejected into the report, not only the one you picked.

## Escalate only what is theirs

Put a question to the user only when the answer is theirs as the accountable owner, never as an expert:

- money, vendor lock-in, anything with a bill attached
- legal, regulatory and personal-data exposure
- who the product is for, and what you are deliberately NOT building
- the quality bar - latency, uptime, audit trail, what is allowed to fail
- anything expensive to reverse once real data or a partner depends on it
- genuine ties, where the options are equal and it comes down to their taste

The test is the ADR test: hard to reverse, surprising without context, the result of a real trade-off.
Hard to reverse is theirs; cheap to reverse is yours.

Also escalate the calls where your own confidence is genuinely low.
If you would flag a decision in the report as "least sure, push back here", ask about it instead - before the report, so the answer shapes the draft rather than amending it.
Reaching the report without having asked a single question is a warning sign: check whether you silently settled calls that were the owner's, or papered over your own uncertainty.

Ask through the structured question tool (in Claude Code: `AskUserQuestion`), recommended answer first.

## Report

Present the draft as a decision log. For each decision:

- **What** you settled on, in one line.
- **Why** - the trade-off, and what you rejected.
- **How to undo it** if it turns out wrong, and what would later make it expensive.
  When the reversal is genuinely free, write "trivial" - never invent a cost - and ask whether the decision belongs in the log at all.

These are three separate labeled lines in every language the conversation runs in: translate the labels when the chat is not in English, but never collapse an entry into one running sentence.
Order the decisions by consequence, the weightiest first - the reader stops reading when it stops mattering.
Report only the decisions that carry the design; leave the minor calls out entirely - the report is for reading, not for the record.
Show the load-bearing decisions working on one real case, with real values, rather than describing them in the abstract.

List the assumptions the draft rests on: the things you were confident enough not to ask about.
Then state what you deliberately left open, and why it is cheaper to decide later.
