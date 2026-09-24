# Agent Guidelines

## 💬 Code Comments & Docstrings
- Use common English (ASD-STE100 is prefered) for all code comments and docstrings.
- Keep comments and docstrings minimal: they answer *why*, not *what*. Skip any docstring that paraphrases the signature or restates what well-named code already shows.
- No module-level docstrings - the module name is sufficient. Document only non-obvious contracts, constraints invisible in the signature, or deliberately surprising behavior.
- Comments must stand on their own in the codebase: never reference internal planning artifacts (task IDs, design docs), other projects/repos, or specific tests as justification. External reference links (GitHub issues, upstream docs) on non-trivial code are fine.
- Write comments as short lower-case phrases, ideally one line. Drop orienting/narrative comments.

## 🗣 Communication
- When reporting information to me, be extremely concise and sacrifice grammar for the sake of concision.

## 🏛 Architecture & Infrastructure
- When making technical decisions, do not give much weight to development cost. Instead, prefer quality, simplicity, robustness, scalability, and long-term maintainability.
- For local development, prefer natively installed services (brew services) over Docker for infrastructure dependencies such as RabbitMQ, Redis, and Postgres.

## 🧵 Multi-Agent Workflows
- Choose each agent’s model and reasoning effort with quality first, then cost and latency. State both and briefly justify why they are sufficient without being excessive. Do not default to `inherit`; justify inherited settings the same way.
- Before launching a multi-agent workflow, present the pipeline and obtain my explicit approval for that run.
- Present the plan for approval as a compact pipeline only: phases in order, agent count per phase, and model + effort per agent (state "inherit session model" explicitly when that is the choice), with a one-line rationale for each choice.

## 🧹 The "Boy Scout" Rule (Engineering Excellence)
- **UI/UX:** When end-to-end testing a product, be picky about the UI you see and be obsessed with pixel perfection. If something clearly looks off, even if it is not directly related to what you are doing, try to get it fixed along or at least mention it.
- **Codebase Health:** Apply that same high standard to engineering excellence: lint, test failures, and test flakiness. If you see one, even if it is not caused by what you are working on right now, still get it fixed.