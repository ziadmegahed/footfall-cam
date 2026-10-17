# Contributing to Footfall AI

Thank you for contributing to Footfall AI.

Footfall AI is a Computer Vision-based retail analytics platform currently in the Proof of Concept (PoC) stage. Our goal is to build a reliable system for person detection, tracking, entry/exit counting, and retail analytics.

This document defines how our team collaborates, writes code, tests changes, and reviews pull requests.

## 1. Team Responsibilities

Each team member owns their primary area while collaborating through shared interfaces and documented contracts.

| Role | Main Responsibilities |
|---|---|
| Computer Vision Engineer | Person detection, tracking, video processing, entry/exit event generation, and CV evaluation |
| Backend Engineer | FastAPI endpoints, event ingestion, validation, database integration, and API tests |
| Frontend Engineer | Dashboard UI, analytics visualization, API integration, and loading/error states |
| MLOps Engineer | Development environment, CI/CD, code quality checks, reproducibility, model evaluation workflows, and deployment readiness |

Responsibilities may overlap, but changes affecting another component must be discussed with its owner.

## 2. Git Workflow

We use GitHub Flow.

- `main` is the stable branch.
- Do not push directly to `main`.
- Create a feature branch for each task.
- Open a Pull Request (PR) when the work is ready for review.
- Merge only after required checks pass and the PR is approved.

### Branch Naming

Use descriptive branch names:

- `feat/person-detection`
- `feat/entry-exit-counting`
- `feat/event-ingestion-api`
- `feat/analytics-dashboard`
- `fix/tracking-id-logic`
- `test/event-schema`
- `docs/update-architecture`
- `chore/backend-ci`

Use lowercase words separated by hyphens.

### Start a New Task

Update your local `main` branch first:

```bash
git switch main
git pull origin main
```

Create a feature branch:

```bash
git switch -c feat/your-feature-name
```

Make changes only related to that task whenever practical.

## 3. Commit Messages

Use clear commit messages with a type prefix:

- `feat:` New functionality
- `fix:` Bug fixes
- `test:` Add or update tests
- `docs:` Documentation changes
- `refactor:` Code restructuring without intended behavior changes
- `chore:` Maintenance and tooling
- `ci:` CI/CD changes

Examples:

```bash
git add .
git commit -m "feat: add person detection pipeline"
git commit -m "test: add entry event validation tests"
git commit -m "fix: prevent duplicate crossing events"
git commit -m "ci: add backend quality checks"
```

Keep commits focused and avoid committing unrelated changes.

## 4. Pull Request Process

Before opening a PR:

1. Ensure your branch contains the latest relevant changes from `main`.
2. Run the applicable tests locally.
3. Run the configured linting and formatting checks.
4. Update documentation if behavior or interfaces have changed.
5. Remove temporary files, local datasets, and generated artifacts that should not be committed.
6. Confirm that no secrets or credentials are included.

Every PR should include:

- A clear title and description.
- The problem being solved.
- A summary of the changes.
- Tests performed and their results.
- Screenshots or sample outputs when relevant.
- Known limitations or follow-up tasks.

Keep PRs focused and reasonably small.

## 5. Code Quality and Testing

All code should be readable, maintainable, and testable.

### Python

- Follow PEP 8 conventions.
- Use type hints where appropriate.
- Use meaningful variable and function names.
- Prefer small functions with clear responsibilities.
- Handle errors explicitly.
- Avoid hardcoded credentials, machine-specific paths, and unexplained constants.
- Use the project's configured tools instead of introducing new tooling without discussion.

### Testing

Add or update tests for new functionality and bug fixes.

Examples include:

- Person detection and tracking behavior.
- Entry/exit event generation.
- Event schema validation.
- API request validation and error responses.
- Analytics calculations.
- Edge cases such as missing timestamps, invalid events, and repeated event submissions.

Tests should be deterministic where possible and should not depend on external services unless explicitly configured.

For Computer Vision changes, document the video or dataset used, evaluation method, and relevant metrics. Do not claim accuracy or FPS improvements without measured evidence.

## 6. Shared Event Contract

The Computer Vision and Backend components communicate through a documented event contract.

An illustrative entry event:

```json
{
  "event_id": "evt_001",
  "store_id": "store_001",
  "camera_id": "cam_001",
  "event_type": "entry",
  "timestamp": "2026-10-16T10:30:00Z",
  "track_id": 17,
  "source": "computer_vision"
}
```

This example is illustrative, not a finalized production schema.

Before changing event fields, types, or semantics:

1. Discuss the change with the CV and Backend owners.
2. Update the canonical schema in `contracts/events/`.
3. Update validation and tests.
4. Update documentation and dependent components.
5. Include the contract change in the PR.

Use UTC timestamps in ISO 8601 format. `event_id` should uniquely identify an event, and the ingestion layer should handle retries safely to prevent duplicate counting.

A tracker ID is temporary and must not be treated as a persistent identity for a person.

## 7. Development Environment

Footfall Cam uses **uv** for Python dependency management, **Ruff** for linting and formatting, and **pytest** for automated testing where configured.

- **Install uv:** Follow the [official installation guide](https://docs.astral.sh/uv/getting-started/installation/) and verify the installation using `uv --version`.
- **Set up the project:** After cloning the repository, run `uv sync --locked` from the directory containing `pyproject.toml` and `uv.lock` to create or synchronize the local virtual environment and install the project's dependencies.
- **Run Python commands:** Use `uv run <command>` to execute commands within the project environment without manually activating `.venv`.
- **Manage dependencies:** Use `uv add <package>` for runtime dependencies and `uv add --dev <package>` for development dependencies. Review and commit changes to `pyproject.toml` and `uv.lock` whenever dependencies change.
- **Code quality:** Run `uv run ruff check .` to check linting rules and `uv run ruff format --check .` to verify formatting before submitting a Pull Request.
- **Testing:** Run `uv run pytest` to execute the configured test suite. Add or update tests when introducing new functionality or fixing bugs.
- **Python compatibility:** Use a Python version supported by the project's `requires-python` setting and the relevant component's configuration.
- **Environment isolation:** Each contributor must maintain their own local virtual environment. Never commit `.venv/` or other generated environment directories.
- **Dependency discipline:** Do not introduce unnecessary dependencies. Do not manually edit `uv.lock`; use uv commands to manage dependency changes and review the resulting lockfile updates.
- **Environment variables and secrets:** Never commit API keys, access tokens, passwords, local `.env` files, or private datasets. Document required environment variables and provide safe placeholder values in `.env.example`.
- **Consistency with CI:** Ensure your changes pass the relevant local checks. GitHub Actions will run the checks configured for the affected workflow, but local validation helps identify problems before opening a Pull Request.

For components that do not use Python, follow the dependency management and development instructions documented for that component.

## 8. Security and Data Privacy

- Never commit passwords, API keys, tokens, or cloud credentials.
- Never upload real customer footage or personally identifiable information without explicit authorization.
- Use approved public datasets or authorized test footage.
- Check dataset licensing and usage restrictions before using data in a commercial demo.
- Avoid logging sensitive video content or personal information.
- Report exposed credentials immediately so they can be revoked and rotated.

## 9. Continuous Integration

Pull Requests should pass the configured automated checks before merging.

Depending on the component, CI may include:

- Dependency installation and lockfile validation.
- Ruff linting and formatting checks.
- pytest unit and integration tests.
- API or schema validation.
- Build checks for affected components.

Do not bypass failing checks without agreement from the team. If a check fails, investigate and fix the root cause or document an approved temporary exception.

## 10. Definition of Done

A task is considered complete when:

- The implementation matches the agreed scope.
- Relevant tests pass.
- Code quality checks pass.
- Documentation and shared contracts are updated when needed.
- No secrets or unauthorized data are committed.
- The PR has received the required review.
- The change is merged into `main`.

For performance-related work, include reproducible measurements and the test environment.

## 11. Questions and Collaboration

Discuss architectural decisions, shared API changes, model choices, and cross-component dependencies with the relevant team members before implementation.

When opening an issue, include the problem, expected behavior, acceptance criteria, and any relevant logs or examples.

Our priority is a working, measurable, and maintainable Proof of Concept—not unnecessary complexity.

Thank you for helping build Footfall Cam.