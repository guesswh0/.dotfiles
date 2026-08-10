# Agent Guidelines

## 📝 Formatting & Documentation
- Never use the em dash "—". Use plain en dash "-" instead.
- When writing or substantially editing long Markdown files, put each full sentence on its own line. Preserve normal Markdown structure, but avoid wrapping multiple sentences onto one physical line.

## 💬 Code Comments & Docstrings
- Keep comments and docstrings minimal: they answer *why*, not *what*. Skip any docstring that paraphrases the signature or restates what well-named code already shows.
- No module-level docstrings - the module name is sufficient. Document only non-obvious contracts, constraints invisible in the signature, or deliberately surprising behavior.
- Comments must stand on their own in the codebase: never reference internal planning artifacts (task IDs, design docs), other projects/repos, or specific tests as justification. External reference links (GitHub issues, upstream docs) on non-trivial code are fine.
- Write comments as short lower-case phrases, ideally one line. Drop orienting/narrative comments.

## 🗣 Communication
- Lead with the outcome: the first lines of a reply answer the question or state what changed. Put mechanism and detail into artifacts (files, commits, docs) and reference them, instead of retelling in chat.

## 🐙 Git & Workflow
- When writing commit messages, NEVER auto-add your agent name as co-author.
- Never manually modify CHANGELOG.md files or any files that are marked as auto-generated.

## 🏛 Architecture & Infrastructure
- When making technical decisions, do not give much weight to development cost. Instead, prefer quality, simplicity, robustness, scalability, and long-term maintainability.
- For local development, prefer natively installed services (brew services) over Docker for infrastructure dependencies such as RabbitMQ, Redis, and Postgres. Do not suggest docker compose for these.
- Personal workflow preferences (like the brew rule above) are for the agent only: never write them into team-shared files (README, project CLAUDE.md, runbooks). Shared docs state requirements neutrally - what must be running, ports, credentials - not how to run it.

## 🐛 Bug Fixing & Testing
- When doing bug fixes, always start with reproducing the bug in an E2E setting as closely aligned with how an end user would experience it as possible. This makes sure you find the real problem so your fix will actually solve it.

## 🧹 The "Boy Scout" Rule (Engineering Excellence)
- **UI/UX:** When end-to-end testing a product, be picky about the UI you see and be obsessed with pixel perfection. If something clearly looks off, even if it is not directly related to what you are doing, try to get it fixed along or at least mention it.
- **Codebase Health:** Apply that same high standard to engineering excellence: lint, test failures, and test flakiness. If you see one, even if it is not caused by what you are working on right now, still get it fixed.