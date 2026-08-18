---
name: draft
description: Draft a design yourself - research the facts, make the technical calls, explain each one, and put to the user only what they alone can answer. Use when the user wants the design worked out for them instead of being interviewed about it.
disable-model-invocation: true
---

# Draft

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
Ask through the structured question tool (in Claude Code: `AskUserQuestion`), recommended answer first.

## Report

Present the draft as a decision log. For each decision:

- **What** you settled on, in one line.
- **Why** - the trade-off, and what you rejected.
- **How to undo it** if it turns out wrong, and what would later make it expensive.

Inventory every call you made, not only the interesting ones: full entries for the consequential ones, a single line each for the rest.
A decision that felt obvious to you is exactly where the owner's model may differ from yours.
For the decisions that carry the design, show them working on one real case, with real values, rather than describing them in the abstract.

Flag the decisions you are least sure about - that is where the user should push back first.
List the assumptions the draft rests on: the things you were confident enough not to ask about.
Then state what you deliberately left open, and why it is cheaper to decide later.

Close by asking whether these decisions should outlive the session.
On yes, apply the `domain-modeling` skill: terms into `CONTEXT.md`, hard-to-reverse decisions into ADRs.
On no, leave nothing behind - it was a draft.
