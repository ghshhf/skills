#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml==6.0.3"]
# ///
"""Bulk-generate skill directories for common AI/developer tooling.

This script creates skill directories under skills/<name>/ each containing a
SKILL.md file. Designed to extend the Hugging Face skills repository with
high-value agent skills covering mainstream developer tools.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
MARKETPLACE_PATH = ROOT / ".claude-plugin" / "marketplace.json"

# ---------------------------------------------------------------------------
# Skill catalog
# ---------------------------------------------------------------------------
# Each entry: (name, description, homepage, body, category, depends)
# "body" is the main instructional markdown, written from the agent's POV.
# ---------------------------------------------------------------------------

SKILLS: list[dict[str, Any]] = [
    # --- 1. LLM / AI Platform APIs ------------------------------------------------
    {
        "name": "openai-api",
        "description": "Call OpenAI APIs using curl, Python SDK, or httpx. Covers chat completions, function/tool calling, embeddings, image generation, assistants, and streaming responses.",
        "homepage": "https://platform.openai.com/docs/introduction",
        "category": "ai-platforms",
        "depends": "",
        "body": """
# OpenAI API

You can call any OpenAI REST endpoint using `curl`, the official Python SDK (`openai`), or plain HTTP libraries. Always prefer the Python SDK when available; fall back to `curl` when minimal dependencies are required.

## Authentication

- Set `OPENAI_API_KEY` in the environment — never hard-code secrets.
- Example curl: `curl -s https://api.openai.com/v1/chat/completions -H "Authorization: Bearer $OPENAI_API_KEY" -H "Content-Type: application/json" -d '{...}'`.

## Python SDK quick reference

```python
from openai import OpenAI
client = OpenAI()

# Chat
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Say hi"}],
)
print(response.choices[0].message.content)

# Streaming
for chunk in client.chat.completions.create(model="gpt-4o", messages=..., stream=True):
    print(chunk.choices[0].delta.content or "", end="")

# Tool calling / JSON mode — use response_format={"type": "json_object"}
# Structured outputs — use `response_format=SomeModel` with pydantic classes.
```

## Common endpoints

| Goal | Endpoint |
|------|----------|
| Chat / reasoning | `POST /v1/chat/completions` |
| Embeddings | `POST /v1/embeddings` model `text-embedding-3-large` or `-small` |
| Images (DALL-E) | `POST /v1/images/generations` |
| Audio (Whisper) | `POST /v1/audio/transcriptions` |
| Batch (async bulk) | `POST /v1/batches` |
| Files upload | `POST /v1/files` |
| Fine-tuning jobs | `POST /v1/fine_tuning/jobs` |

## Tips

- Use `response_format={"type": "json_object"}` when you need guaranteed JSON.
- Prefer `gpt-4o-mini` for cost-sensitive tasks; use `gpt-4o` for complex reasoning.
- Rate-limit headers: `x-ratelimit-limit-requests`, `x-ratelimit-remaining-requests`, `x-ratelimit-reset-requests`.
- Always set a reasonable timeout (15-60s) for network calls.
""",
    },
    {
        "name": "anthropic-api",
        "description": "Call Anthropic Claude APIs. Covers messages API, streaming, tool/function calling, computer use (beta), prompt caching, and structured JSON output.",
        "homepage": "https://docs.anthropic.com/",
        "category": "ai-platforms",
        "depends": "",
        "body": """
# Anthropic API

Call the Anthropic Claude API using the official `anthropic` Python SDK, `@anthropic-ai/sdk` for JavaScript, or plain `curl`.

## Authentication

- Set `ANTHROPIC_API_KEY` in the environment.
- For beta features, add header `anthropic-beta: computer-use-2025-01-24` (or relevant beta tag).

## Python quick reference

```python
from anthropic import Anthropic

client = Anthropic()
message = client.messages.create(
    model="claude-4-5-sonnet-20251015",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hi"}],
)
print(message.content[0].text)

# Streaming
with client.messages.stream(model="claude-4-5-sonnet-20251015", max_tokens=1024, messages=...) as stream:
    for text in stream.text_stream:
        print(text, end="")
```

## Key capabilities

- **Tool use** — pass `tools=[...]` and `tool_choice={...}`; the model returns `stop_reason: "tool_use"`.
- **Computer use** — requires beta header; tools `computer_use` / `bash` / `text_editor`.
- **Prompt caching** — mark blocks with `cache_control={"type": "ephemeral"}` to reduce repeat-query cost.
- **Structured output** — use `response_format` with a JSON schema to guarantee typed JSON.

## Model names

- `claude-4-5-sonnet-20251015` (latest sonnet, best speed/quality)
- `claude-4-opus-20250219` (Opus, highest reasoning)
- `claude-4-haiku-20250307` (Haiku, fastest / cheapest)

## Tips

- Always set `max_tokens`; it is mandatory and has no default.
- System prompt goes in the `system` kwarg of `messages.create()`, not in `messages`.
- Output token caps: `max_tokens=8192` for most models.
""",
    },
    {
        "name": "deepseek-api",
        "description": "Call DeepSeek API (DeepSeek-V3 / DeepSeek-R1 for reasoning). Use for cost-effective chat completions and strong open-weight reasoning alternatives.",
        "homepage": "https://api.deepseek.com/",
        "category": "ai-platforms",
        "depends": "",
        "body": """
# DeepSeek API

OpenAI-compatible REST endpoints provided by DeepSeek.

## Authentication

- Set `DEEPSEEK_API_KEY` in the environment.
- Base URL: `https://api.deepseek.com`.

## Python usage (compatible with openai SDK)

```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "Hello"}],
    stream=False,
)
```

## Models

- `deepseek-chat` — DeepSeek-V3 general-purpose chat.
- `deepseek-reasoner` — DeepSeek-R1 reasoning model (produces `<think>…</think>` reasoning blocks in responses).

## Key differences from OpenAI

- `reasoning_effort` parameter available for reasoner: `low`, `medium`, `high`.
- JSON mode supported via `response_format={"type": "json_object"}`.
- Streaming supported natively via `stream=True`.
""",
    },
    {
        "name": "ollama",
        "description": "Run open-weight LLMs locally via Ollama. Covers common model management, chat completions API, embeddings, and model listing/pulling.",
        "homepage": "https://github.com/ollama/ollama",
        "category": "ai-platforms",
        "depends": "",
        "body": """
# Ollama

Run open-weight models locally using `ollama`. Default API server runs at `http://localhost:11434`.

## Install

- macOS / Linux: `curl -fsSL https://ollama.com/install.sh | sh`
- Windows: download from https://ollama.com/download

## CLI commands

- `ollama run llama3` — start a chat session with Llama 3
- `ollama pull <model>` — download a model
- `ollama list` — list installed models
- `ollama rm <model>` — delete a model
- `ollama serve` — start API server manually

## REST API

```bash
# Chat completion
curl http://localhost:11434/api/chat -d '{
  "model": "llama3",
  "messages": [{"role": "user", "content": "Hi"}]
}'

# Generate (single completion)
curl http://localhost:11434/api/generate -d '{"model": "llama3", "prompt": "Hi"}'

# Embeddings
curl http://localhost:11434/api/embeddings -d '{"model": "llama3", "prompt": "embed me"}'

# List models
curl http://localhost:11434/api/tags
```

## OpenAI-compatible endpoint

Ollama exposes an OpenAI-compatible chat endpoint: `http://localhost:11434/v1`. You can use any OpenAI SDK:

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
client.chat.completions.create(model="llama3", messages=[{"role": "user", "content": "Hi"}])
```

## Popular models

`llama3.3`, `qwen2.5`, `gemma3`, `mistral`, `mixtral`, `phi4`, `deepseek-r1`, `deepseek-v3`, `llava` (vision), `nomic-embed-text` (embeddings).
""",
    },

    # --- 2. Development tools ------------------------------------------------------
    {
        "name": "git-advanced",
        "description": "Advanced Git workflows: interactive rebase, cherry-picking, bisect, worktrees, submodules, blame, stash, partial commits, blame navigation, and safe force-push etiquette.",
        "homepage": "https://git-scm.com/docs",
        "category": "dev-tools",
        "depends": "",
        "body": """
# Git — Advanced Workflows

Use these patterns when the user's need goes beyond the basic add/commit/push cycle.

## Selective staging

- `git add -p <file>` — stage specific hunks.
- `git checkout -p <file>` — discard specific hunks.

## Rewriting history

- `git rebase -i HEAD~N` — interactively squash, reorder, edit, drop commits.
  - `p` pick, `r` reword, `e` edit, `s` squash, `f` fixup, `x` exec, `d` drop.
- `git commit --amend` — edit last commit message / content.
- `git reset --soft HEAD~N` — undo N commits but keep changes staged.

## Cherry-picking

- `git cherry-pick <commit-sha>` — apply a single commit from another branch.
- `git cherry-pick A..B` — cherry-pick range (A exclusive, B inclusive).
- `-x` records the source in the commit message.

## Bisect

```bash
git bisect start
git bisect good <good-commit>
git bisect bad <bad-commit>
# Git checks out a middle commit; you run your test and call:
# git bisect good / git bisect bad
# To script: git bisect run ./test.sh
git bisect reset
```

## Worktrees (multiple working copies, single .git)

- `git worktree add ../feature-branch feature-branch`
- `git worktree list`
- `git worktree prune`

## Submodules

- `git submodule update --init --recursive` — fetch and update.
- `git submodule add <url> <path>`
- `git submodule foreach 'git pull'`

## Blame

- `git blame -L 100,120 <file>` — blame specific lines.
- `git blame -w <file>` — ignore whitespace changes.
- `git log -p -S "text" <file>` — find commits touching a string.

## Stash

- `git stash push -m "my description"`
- `git stash list` / `git stash pop [stash@{n}]` / `git stash drop` / `git stash apply`

## Safe force-push

- **Never `git push --force`** on a shared branch others are using.
- Prefer `git push --force-with-lease` — refuses to overwrite commits pushed by others since your last fetch.

## Other

- `git diff --word-diff` / `git diff --staged`
- `git diff main...HEAD` — diff since branch point (triple-dot).
- `git log --oneline --graph --decorate --all` — repo map.
- `git reflog` — recover lost commits.
""",
    },
    {
        "name": "docker",
        "description": "Use Docker for building, running, inspecting, and managing containers. Covers Dockerfile best practices, images, volumes, networks, and container lifecycle.",
        "homepage": "https://docs.docker.com/",
        "category": "dev-tools",
        "depends": "",
        "body": """
# Docker

## Container lifecycle

- `docker run [options] <image> [cmd]` — create + start container.
  - `-d` detached, `-it` interactive tty, `--rm` auto remove on stop, `--name N`, `-p host:container`, `-v host:container`, `-e VAR=value`, `--network N`.
- `docker ps [-a]` — list running (or all) containers.
- `docker exec -it <container> <cmd>` — run command inside a running container (`bash` / `sh` for shell).
- `docker logs [-f] [--tail N] <container>`
- `docker stop <container>` / `docker restart` / `docker rm [-f] <container>`
- `docker cp <src> <container>:<dest>` / reverse for copying files.

## Images

- `docker build -t myimg:v1 .`
- `docker build -t myimg:v1 -f path/to/Dockerfile .`
- `docker build --platform linux/amd64 ...` (cross-platform build).
- `docker pull <image>` / `docker push <image>`
- `docker images` / `docker rmi <image>`
- `docker tag <source> <target>`

## Dockerfile best practices

- Order instructions by frequency of change — put `RUN apt-get install` before copying code.
- Multi-stage: `FROM <base> AS builder` … `COPY --from=builder /out /app`.
- Use `--mount=type=cache` for package-manager caches.
- Use specific base image tags, avoid vague `:latest`.
- `USER nonroot` / expose via `EXPOSE` docs only (use `-p` at runtime).
- `.dockerignore` excludes node_modules, .git, __pycache__.

## Volumes & networks

- `docker volume create mydata` / `ls` / `rm`
- `docker network create --driver bridge mynet`
- `docker network connect mynet mycontainer`

## Housekeeping

- `docker system df` — show disk usage.
- `docker system prune -f` — remove stopped containers, dangling images, unused networks.
- `docker system prune -a --volumes` — CAREFUL: also removes unused images + volumes.

## Inspecting

- `docker inspect <container-or-image>` — returns big JSON; pipe to `jq`.
- `docker top <container>` — process list inside.
- `docker stats` — live CPU/memory/IO.
""",
    },
    {
        "name": "docker-compose",
        "description": "Manage multi-container applications with docker compose. Covers compose.yaml syntax, services, volumes, networks, profiles, environment files, and common commands.",
        "homepage": "https://docs.docker.com/compose/",
        "category": "dev-tools",
        "depends": "docker",
        "body": """
# Docker Compose

Use `docker compose` (modern, plugin-based) rather than the legacy `docker-compose`.

## File structure (compose.yaml)

```yaml
services:
  web:
    build: .          # path to a Dockerfile context
    image: nginx:alpine
    ports:
      - "8080:80"
    environment:
      DB_HOST: db
      DB_USER: ${DB_USER:-app}
    env_file: .env
    volumes:
      - ./src:/app/src              # bind mount
      - static:/app/static           # named volume
    depends_on:
      - db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-fsSL", "http://localhost/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '1.5'
          memory: 1G

  db:
    image: postgres:17-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_pass
    secrets:
      - db_pass

volumes:
  static:
  pgdata:

secrets:
  db_pass:
    file: ./secrets/db_pass.txt
```

## Common commands

- `docker compose up [-d] [--build] [service...]` — start services.
- `docker compose down [-v]` — stop & remove; `-v` also removes named volumes.
- `docker compose logs [-f] [--tail=N] [service]`
- `docker compose exec <service> <cmd>` — run command inside service container.
- `docker compose ps`
- `docker compose restart <service>`
- `docker compose build [--no-cache] [service]`
- `docker compose pull` — refresh all images to the tag's latest.
- `docker compose config` — render final merged YAML (great for debugging includes).

## Environment

- `env_file:` — include `.env` files.
- `${VAR:-default}` / `${VAR:?must-set}` — interpolation with defaults/required checks.

## Profiles — optional services

```yaml
services:
  worker:
    profiles: ["dev"]
    # ...
```
- Start: `docker compose --profile dev up`

## Tips

- **Named volumes survive `down`** — use `-v` only if you want a fresh state.
- Use `depends_on` + `healthcheck` for real readiness waiting (simple `depends_on` only waits for the container to start).
- `docker compose -f a.yaml -f b.yaml config` merges multiple compose files.
""",
    },
    {
        "name": "uv-python",
        "description": "Use uv for fast Python package management and project tooling: create venvs, install packages, pin dependencies, run scripts, and manage Python versions.",
        "homepage": "https://docs.astral.sh/uv/",
        "category": "dev-tools",
        "depends": "",
        "body": """
# uv — fast Python tooling

Replaces `pip`, `pipx`, `virtualenv`, `pip-tools`, and parts of `poetry`/`pdm`. Written in Rust.

## Install

- `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Or via package manager: `brew install uv`

## Project commands

- `uv init [--package] [dir]` — new project (produces `pyproject.toml`).
- `uv add <pkg>` — add dependency (adds to `[project] dependencies`).
- `uv add --dev <pkg>` — add dev dependency.
- `uv remove <pkg>`
- `uv sync` — synchronize the virtual environment with `pyproject.toml` + lockfile.
- `uv lock` — re-pin to `uv.lock`.
- `uv run <cmd>` — run a command inside the venv. Example: `uv run python -c "print(1)"`.
- `uv run --with requests:latest myscript.py` — ad-hoc dependency injection for one script.

## Virtual envs

- `uv venv [--python 3.12] [./.venv]` — explicit venv creation.
- Environment variables: `VIRTUAL_ENV`, `UV_PYTHON` (pin the interpreter).

## Managing Python versions

- `uv python install 3.12` / `uv python install 3.11.9`
- `uv python list`
- `uv python find 3.12`

## Script running (the `# /// script` block)

Embed dependencies in a script comment. Example `myscript.py`:

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests==2.32.0",
# ]
# ///
import requests
print(requests.get("https://httpbin.org/get").text)
```

Run: `uv run myscript.py` — uv auto-installs dependencies in a cached env.

## Publishing

- `uv build` — produces wheel + sdist in `dist/`.
- `uv publish --token $PYPI_TOKEN`

## Common flags

- `--no-cache` — ignore cache when resolving/installing.
- `--reinstall` — force reinstall even if present.
- `--frozen` — only use lockfile, fail if it needs updating.
- `--quiet` — suppress most output.
""",
    },
    {
        "name": "shell-scripting",
        "description": "Write reliable Bash/sh scripts. Covers set options, error handling, quoting, pipelines, command substitution, arrays, and common pitfalls.",
        "homepage": "https://www.gnu.org/software/bash/manual/",
        "category": "dev-tools",
        "depends": "",
        "body": """
# Shell Scripting Best Practices

## Safety header

Start every script with:

```bash
#!/usr/bin/env bash
set -euo pipefail
```

- `set -e` — exit on any command failure (but see caveats below).
- `set -u` — fail on undefined variable references.
- `set -o pipefail` — a pipeline fails if any component fails (not just the last).
- Use `set -x` for debug tracing.

## Quoting

- **Always double-quote variable expansions**: `"$file"` — prevents word splitting and glob expansion of spaces, `*`, `?`, etc.
- Single quotes: `'$no_expansion'` — literal text.
- `"${var}"` — explicit variable boundary: `"${foo}_suffix"`.

## Command substitution

- Prefer `$(cmd)` over backticks (nestable).
- `x=$(find . -type f)` — trailing newlines are stripped by the shell.

## Error handling

```bash
# Allow a command to fail without triggering -e
maybe_fail || true

# Capture and branch on failure
if output=$(fragile_cmd); then
  echo "ok: $output"
else
  code=$?
  echo "failed with exit $code" >&2
  exit $code
fi
```

## Log / timestamp helpers

```bash
log()  { printf '%s [INFO] %s\n' "$(date -u +%FT%TZ)" "$*" >&2; }
die()  { printf '%s [ERROR] %s\n' "$(date -u +%FT%TZ)" "$*" >&2; exit 1; }
```

## Arrays

```bash
files=("file one.txt" "file two.txt")
for f in "${files[@]}"; do   # note the quoting — expands to one word per element
  echo "-- $f"
done
echo "count: ${#files[@]}"
```

## Arguments

- `$0` script name, `$1`…`$9` positional args, `$#` count, `$@` all args as separate words, `$*` all args joined by IFS.
- `while [[ $# -gt 0 ]]; do case "$1" in ...` pattern for flag parsing.
- `getopts` for simple `-x` style flags; `getopt` or `argparse`-style libraries for long options.

## Conditionals

```bash
[[ -f "$path" ]]   # regular file exists
[[ -d "$path" ]]   # directory exists
[[ -s "$path" ]]   # file exists and non-empty
[[ -r "$path" ]]   # readable
[[ "$a" == "$b" ]] # string equality (use == with [[ ]])
[[ "$a" != "$b" ]]
[[ $n -lt 10 ]]    # arithmetic: -lt, -le, -eq, -ne, -ge, -gt
```

## Heredocs

```bash
cat > out.txt <<'EOF'   # quoted 'EOF' prevents $ expansion inside
literal $variables and `commands`
EOF
```

## Portability

- Use `#!/usr/bin/env bash` over hardcoded `/bin/bash`.
- Use `/usr/bin/env python3` to run the first `python3` on `$PATH`.
- For Alpine containers (no bash by default), use `#!/bin/sh` + POSIX features only (no `[[ ]]`, arrays, `local`).

## Common pitfalls

- `cd somewhere && ls` — use `&&` to avoid running `ls` in the original dir if `cd` fails.
- `rm -rf /important/$dir` — if `$dir` is empty, you wipe `/important`! Guard: `: "${dir:?}"`.
- Parsing `ls` output — never do; use `find ... -print0 | xargs -0` or `while read -r` loops.
- Comparing versions — `printf '%s\n%s' "1.10" "1.9" | sort -V` gives correct order.
""",
    },

    # --- 3. Code analysis & quality -------------------------------------------------
    {
        "name": "code-review",
        "description": "Patterns for reviewing code: readability, correctness, error handling, test coverage, performance clues, security flags, and actionable comments.",
        "homepage": "https://github.com/goldbergyoni/javascript-testing-best-practices",
        "category": "code-quality",
        "depends": "",
        "body": """
# Code Review — Agent Instructions

When asked to review code, produce focused, actionable feedback organized by
severity (must-fix / should-fix / nit). For each issue, quote the specific
code location.

## Checklist framework

1. **Correctness & edge cases**
   - Are empty inputs / null / NaN / negative sizes handled?
   - Does the code handle concurrent access / re-entrancy?
   - Are off-by-one errors possible in loops / slices / ranges?
   - What happens on network failure, disk full, permission denied?

2. **Error handling**
   - Is every error checked (return codes, exceptions, Promise rejections)?
   - Are swallowed exceptions (`except: pass`, `.catch(()=>{})`) present? Flag them.
   - Is user-facing error text clear and specific?

3. **Security**
   - Do shell/command invocations use untrusted input? Prefer argument lists over shell strings.
   - Are secrets logged, committed, or placed in URLs?
   - Look for unsanitized user input flowing into SQL, HTML, shell, or filesystem paths.

4. **Testing**
   - Does the PR add tests for new behavior?
   - Are tests readable? Do they assert on the right things, not just "didn't crash"?

5. **Readability & conventions**
   - Do names describe intent?
   - Is the function size manageable (split if > 80 lines)?
   - Are deep nesting and boolean pyramids simplified with early returns?

6. **Performance**
   - Any hidden O(n²) loops over collections that may grow?
   - Unnecessary copies, string concat in hot loops?
   - Are caches / memoization correct and bounded in size?

7. **Maintainability**
   - Is there a TODO/FIXME with a tracking issue or at least an explanation?
   - Are public functions documented with parameters and return semantics?

## Comment tone

- Be specific, reference exact lines / functions.
- Offer a concrete alternative when flagging an issue.
- Avoid bike-shedding on style unless it violates project conventions.

## Reviewing diffs

When reading `git diff` / PR diff, focus on the changed regions first, but read enough context to validate correctness. When something is unclear, ask — don't guess.
""",
    },
    {
        "name": "refactoring-patterns",
        "description": "Common refactoring recipes: extract function, rename, replace magic numbers with constants, split long functions, extract classes, convert conditionals to polymorphism, and safe refactoring workflow.",
        "homepage": "https://refactoring.com/catalog/",
        "category": "code-quality",
        "depends": "",
        "body": """
# Common Refactoring Patterns

Refactor in small, test-verified steps. Keep each commit focused on one
refactoring so it is mechanically reviewable.

## Extract function / method

When a block of code does one thing and has a name: pull it out.

```ts
// Before
function printInvoice(user) {
  const total = user.orders.reduce((s, o) => s + o.amount, 0);
  const tax = total * 0.2;
  console.log(`${user.name} — total: ${total + tax}`);
}

// After
function invoiceTotal(orders) { return orders.reduce((s, o) => s + o.amount, 0); }
function withTax(amount, rate) { return amount * (1 + rate); }
function printInvoice(user) {
  const total = withTax(invoiceTotal(user.orders), 0.2);
  console.log(`${user.name} — total: ${total}`);
}
```

## Rename for clarity

- `process()` → `validateAndStoreUser()`
- `data` → `rawServerResponse`
- `x`, `i`, `tmp` — acceptable as loop variables only; otherwise rename.

## Replace magic numbers / strings with named constants

```python
# Before
if size > 1024 * 1024: ...

# After
MAX_BYTES = 1024 * 1024
if size > MAX_BYTES: ...
```

## Replace nested conditionals with guard clauses / early returns

```python
# Before
if user:
    if user.active:
        if has_paid(user):
            ship()
        else: return "no payment"
    else: return "inactive"
else: return "no user"

# After
if not user: return "no user"
if not user.active: return "inactive"
if not has_paid(user): return "no payment"
ship()
```

## Replace conditional with polymorphism / strategy

```python
class Square: def area(self): return self.side**2
class Circle: def area(self): return math.pi * self.r**2
# instead of if/elif/else over a "type" field
```

## Compose methods / compose functions

```python
# Before
out = step3(step2(step1(input)))

# After
out = pipe(input, step1, step2, step3)
```

## Data structure refactor

- Parallel arrays `names[i], ages[i]` → array of objects/records.
- Stringly-typed data: `"user:42:active"` → parse into `{user, id, status}` once.

## Safe workflow

1. Ensure tests exist and pass on base.
2. Make a small refactor; run tests.
3. Commit.
4. Repeat. Don't refactor + change behavior in the same commit.
""",
    },

    # --- 4. Web / networking --------------------------------------------------------
    {
        "name": "http-requests",
        "description": "Make HTTP requests from agents/ scripts. Covers curl flags, Python requests/httpx, timeouts, retries, proxies, TLS, and JSON handling.",
        "homepage": "https://curl.se/docs/manpage.html",
        "category": "web",
        "depends": "",
        "body": """
# HTTP Requests

## curl — one-line swiss knife

```bash
# GET with JSON output + headers visible
curl -fsSL -H "Accept: application/json" -H "Authorization: Bearer $TOKEN" \
  "https://api.example.com/v1/things?id=42"

# POST JSON
curl -fsSL -X POST -H "Content-Type: application/json" \
  -d '{"name":"a","value":1}' https://api.example.com/v1/things

# POST form fields
curl -fsSL -F "file=@local.csv" -F "name=data" https://example.com/upload

# Save response body to file, show progress only
curl -fsSL -o out.bin https://example.com/large.bin
```

Flags: `-f` fail silently on HTTP errors, `-s` silent, `-S` show errors, `-L` follow redirects, `-v` verbose (show request/response wire), `-I` headers-only, `-H "Name: value"`, `--connect-timeout 5`, `--max-time 30`, `-A "MyAgent/1.0"`.

## Python with `httpx` (modern)

```python
import httpx

with httpx.Client(timeout=30.0, follow_redirects=True) as client:
    r = client.get("https://api.example.com/v1/things", params={"id": 42})
    r.raise_for_status()
    data = r.json()

# Async
async with httpx.AsyncClient(timeout=30.0) as client:
    r = await client.post(url, json=payload, headers=headers)
```

## Python with `requests`

```python
import requests
r = requests.get(url, timeout=30, params={"id": 42})
r.raise_for_status()
data = r.json()
```

**Always pass a `timeout`** — without it, requests can hang forever.

## Retry with backoff (tenacity)

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10),
       retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.NetworkError)))
def call(): ...
```

## Status code quick reference

- `200` / `201` / `204` — success family.
- `301` / `302` / `307` / `308` — redirection; curl and libraries follow them automatically.
- `400` your input is malformed; `401` missing / bad auth; `403` authenticated but forbidden; `404` not found; `422` valid syntax but failed validation; `429` rate-limited (check `Retry-After`).
- `500` / `502` / `503` / `504` — server-side issues, retry with backoff.

## Tips

- Never embed secrets in curl URL — use headers or `-H "Authorization: Bearer $TOKEN"`.
- Use `.netrc` for long-term credentials to avoid leaking them to shell history.
- Set a `User-Agent` when scraping / automated usage.
- Respect `Retry-After` and `rate-limit-*` response headers.
- For large downloads: `curl -C - -o file URL` resumes partial transfers.
""",
    },
    {
        "name": "websocket",
        "description": "Use WebSocket clients in Python and shell. Covers handshake, sending/receiving JSON, heartbeats, reconnecting, and the `wscat` CLI.",
        "homepage": "https://websockets.readthedocs.io/",
        "category": "web",
        "depends": "",
        "body": """
# WebSockets

## CLI with `wscat`

Install: `npm install -g wscat`

Interactive session:
```bash
wscat -c wss://echo.websocket.events
# (type a line, Enter to send)
```

One-shot: pipe messages via stdin with `-x`:
```bash
wscat -c wss://example.com/socket -x '{"type":"ping"}'
```

## Python — websockets (async)

```python
import asyncio, json
from websockets.sync.client import connect

with connect("wss://example.com/socket", additional_headers={"Authorization": f"Bearer {TOKEN}"}) as ws:
    ws.send(json.dumps({"type": "hello"}))
    while True:
        msg = json.loads(ws.recv())
        print(msg)
        if msg.get("type") == "done": break
```

Async variant:

```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("wss://example.com/socket") as ws:
        await ws.send(json.dumps({"ping": 1}))
        while True:
            print(await ws.recv())

asyncio.run(main())
```

## Python — requests-like with `websocket` (older)

```python
import websocket, json
ws = websocket.create_connection("wss://example.com/socket")
ws.send(json.dumps({"hi": 1}))
ws.recv()
ws.close()
```

## Reconnect with exponential backoff

```python
import time, random
def run():
    backoff = 1
    while True:
        try:
            with connect("wss://example.com/socket") as ws:
                backoff = 1
                for message in ws:
                    print(message)
        except Exception as e:
            print(f"disconnected: {e}; retry in {backoff}s")
            time.sleep(backoff + random.uniform(0, 0.5))
            backoff = min(backoff * 2, 60)
```

## Tips

- Keep message payloads under ~32KB to avoid fragmentation surprises.
- Ping/pong frames are handled by libraries; you rarely need to send them manually.
- TLS termination: endpoints starting `wss://` use TLS (443 common); `ws://` is plaintext (rare).
- Always set a connection/overall timeout.
""",
    },
    {
        "name": "rest-api-design",
        "description": "Design pragmatic REST/JSON HTTP APIs. Covers resource naming, HTTP verbs, status codes, pagination, filtering, idempotency, versioning, and error shapes.",
        "homepage": "https://en.wikipedia.org/wiki/REST",
        "category": "web",
        "depends": "",
        "body": """
# REST API Design Guide

## Nouns, not verbs — resources

| Method | Path | Purpose |
|--------|------|---------|
| GET    | `/orders` | list |
| GET    | `/orders/:id` | fetch by id |
| POST   | `/orders` | create (returns `201 Created` with `Location: /orders/:id`) |
| PUT    | `/orders/:id` | full replace / upsert |
| PATCH  | `/orders/:id` | partial update (use JSON Merge Patch or JSON Patch) |
| DELETE | `/orders/:id` | remove |

POST is also acceptable for RPC-style actions that don't map to CRUD: `POST /orders/:id/ship`.

## Status codes, correctly

- `200 OK` — success with body.
- `201 Created` — entity created; include `Location` header.
- `202 Accepted` — async work kicked off; return a job URL.
- `204 No Content` — success, no body (PUT / DELETE often).
- `400 Bad Request` — malformed input.
- `401 Unauthorized` — no / invalid credentials (despite the name).
- `403 Forbidden` — authenticated but not allowed.
- `404 Not Found` — resource does not exist.
- `409 Conflict` — state conflict (e.g. unique key violation, optimistic lock).
- `422 Unprocessable Content` — well-formed but fails validation rules.
- `429 Too Many Requests` — rate limited; include `Retry-After`.
- `5xx` — server-side. Return a stable error shape; never leak stack traces.

## Pagination

Two reasonable options:

1. **Offset / limit**: `GET /orders?limit=50&offset=100` — simple, bad for large offsets.
2. **Cursor / keyset**: `GET /orders?limit=50&after=<base64-encoded-cursor>` — stable across inserts; response includes `next_cursor`.

Response envelope:

```json
{
  "items": [ {"id": "a", ...}, ... ],
  "page_info": { "has_next": true, "next_cursor": "eyJpZCI6ImEifQ" },
  "total": 1024
}
```

## Filtering & sorting

- `GET /orders?status=paid&customer_id=42&sort=-created_at` — query parameters.
- `-field` prefix convention for descending; `+field` or bare for ascending.
- Validate unknown parameters: reject (fail loudly) or log + ignore with warning.

## Idempotency

- `GET`, `PUT`, `DELETE`, `PATCH`, `HEAD`, `OPTIONS` are required to be safe / idempotent by RFC.
- For `POST` that creates resources, support `Idempotency-Key: <uuid>` header: same key + same body → same response, no double-creation.

## Versioning

Choose one and stick with it:
- Path: `/v1/orders` — simplest, most common.
- Header: `Accept: application/vnd.myapi.v1+json` — purest REST but heavier client.

## Error shape

```json
{ "error": { "code": "validation_failed", "message": "email is required", "request_id": "req_xyz", "field_errors": [{"field":"email","message":"required"}] } }
```

## Tips

- Use plural resource names consistently.
- Date/times: ISO 8601 UTC: `2025-06-22T14:30:00Z`.
- IDs: opaque strings (UUID, snowflake, etc.) — avoid leaking integers as IDs.
- Accept / return only JSON unless the API explicitly serves files.
- Document with OpenAPI 3.x; use a UI like Swagger UI or Redoc.
""",
    },

    # --- 5. Databases ---------------------------------------------------------------
    {
        "name": "sql-patterns",
        "description": "Pragmatic SQL patterns: joins, CTEs, window functions, upsert, pagination with keysets, EXPLAIN, indexes, transaction isolation, and N+1 avoidance.",
        "homepage": "https://www.postgresql.org/docs/",
        "category": "databases",
        "depends": "",
        "body": """
# SQL Patterns

## JOINs

```sql
-- inner join — only matching rows
SELECT u.name, o.total FROM users u JOIN orders o ON o.user_id = u.id;

-- left join — all rows from left, NULL fills from right when no match
SELECT u.name, SUM(o.total) FROM users u LEFT JOIN orders o ON o.user_id = u.id GROUP BY u.id;

-- anti-join — users with zero orders
SELECT u.id FROM users u LEFT JOIN orders o ON o.user_id = u.id WHERE o.id IS NULL;
```

## CTEs (Common Table Expressions) — composable subqueries

```sql
WITH monthly AS (
  SELECT user_id, date_trunc('month', created_at) m, SUM(amount) AS total
  FROM orders GROUP BY 1, 2
)
SELECT m, AVG(total) FROM monthly GROUP BY m ORDER BY m;
```

## Window functions — per-group ranking / running totals

```sql
SELECT user_id, amount, created_at,
       ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) AS nth_order,
       SUM(amount)  OVER (PARTITION BY user_id ORDER BY created_at) AS running_total
FROM orders;
```

Useful functions: `ROW_NUMBER()`, `RANK()`, `DENSE_RANK()`, `LAG()/LEAD()`, `FIRST_VALUE()`.

## Upsert (PostgreSQL)

```sql
INSERT INTO kv(key, value, updated_at) VALUES ($1, $2, NOW())
ON CONFLICT (key) DO UPDATE
SET value = EXCLUDED.value, updated_at = NOW()
RETURNING *;
```

MySQL: `INSERT ... ON DUPLICATE KEY UPDATE`. SQLite: `INSERT ... ON CONFLICT DO UPDATE SET ...`.

## Pagination — keyset / "seek" method (avoid `OFFSET`)

```sql
-- page 1
SELECT id, title FROM posts ORDER BY id DESC LIMIT 20;
-- page 2 — last_seen_id is the smallest id from page 1
SELECT id, title FROM posts WHERE id < last_seen_id ORDER BY id DESC LIMIT 20;
```

## EXPLAIN ANALYZE

- `EXPLAIN (ANALYZE, BUFFERS) <query>;` — plan + actual run + buffer stats.
- Look for `Seq Scan` on large tables → missing index.
- Look for rows-actual vs rows-estimate discrepancies → stale statistics → `ANALYZE tbl;`.

## Indexes

- Index columns used in `WHERE`, `JOIN ON`, `ORDER BY`.
- Multi-column indexes are ordered; use most-selective column first.
- `CREATE INDEX CONCURRENTLY` (Postgres) to avoid taking a write lock.
- Avoid indexing low-cardinality columns (e.g. booleans) alone — combine.
- Partial indexes: `CREATE INDEX idx_open_orders ON orders(user_id) WHERE status = 'open'`.

## Transactions & isolation

- Default in Postgres is `READ COMMITTED`; use `BEGIN ISOLATION LEVEL REPEATABLE READ; ... COMMIT;` when you need repeatable reads or serializable.
- Keep transactions short — long tx blocks VACUUM and hold locks.
- `SELECT ... FOR UPDATE` — explicit row locking to prevent lost updates.

## Avoiding N+1 queries

Instead of `for user in users: for order in db.orders(user) ...`, do one query with `WHERE user_id = ANY ($1)` or use a JOIN.

## Parameterized queries — NEVER concatenate user input

```python
# GOOD
cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# BAD — SQL injection!
cur.execute(f"SELECT * FROM users WHERE id = {user_id}")
```
""",
    },
    {
        "name": "postgresql",
        "description": "PostgreSQL commands & patterns: psql basics, creating users/databases, JSONB, arrays, full-text search, common extensions, and backup/restore.",
        "homepage": "https://www.postgresql.org/docs/",
        "category": "databases",
        "depends": "sql-patterns",
        "body": """
# PostgreSQL

## psql one-liners

```bash
psql -U user -d dbname -h localhost -c "SELECT 1"
psql -U user -d dbname -f query.sql
psql postgres://user:pass@host:5432/dbname
```

Inside psql: `\l` list databases, `\dt` list tables, `\d+ tbl` table details, `\i file.sql` run file, `\timing on` show query time, `\x` expanded display, `\o out.txt` redirect output, `\e` edit query in $EDITOR, `\?` help.

## Create database & user

```sql
CREATE USER app WITH PASSWORD 'change-me' LOGIN;
CREATE DATABASE app_db OWNER app;
GRANT ALL ON DATABASE app_db TO app;
\c app_db
GRANT ALL ON SCHEMA public TO app;  -- for PG15+
```

## JSONB

```sql
-- Create
CREATE TABLE events (id uuid PRIMARY KEY, payload jsonb NOT NULL, created_at timestamptz DEFAULT NOW());

-- Index common keys
CREATE INDEX idx_events_payload ON events USING GIN (payload);

-- Query
SELECT payload->>'name' AS name FROM events WHERE payload @> '{"type":"signup"}'::jsonb;
SELECT payload #> '{address, city}' FROM events;

-- Update
UPDATE events SET payload = payload || '{"status":"ok"}'::jsonb WHERE id = $1;
```

## Arrays

```sql
SELECT ARRAY[1,2,3];
SELECT string_to_array('a,b,c', ',');
SELECT unnest(ARRAY['x','y']); -- expand to rows
SELECT * FROM t WHERE tags && ARRAY['urgent']; -- overlap (any match)
```

## Full-text search

```sql
SELECT id, title FROM docs
WHERE to_tsvector('english', body) @@ plainto_tsquery('english', 'postgres search')
ORDER BY ts_rank(to_tsvector('english', body), plainto_tsquery('postgres search')) DESC;

-- Materialize as column + GIN index for speed:
ALTER TABLE docs ADD COLUMN vec tsvector GENERATED ALWAYS AS (to_tsvector('english', body)) STORED;
CREATE INDEX idx_docs_vec ON docs USING GIN(vec);
```

## Useful extensions

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;    -- gen_random_uuid(), crypt()
CREATE EXTENSION IF NOT EXISTS citext;       -- case-insensitive text
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;  -- top queries
```

## Backup & restore

```bash
pg_dump -d "postgres://user:pwd@host/db" -Fc -f db.dump
pg_restore -d "postgres://user:pwd@host/newdb" db.dump -j 4
```

## Performance heuristics

- Long-running query? Start with `EXPLAIN (ANALYZE, BUFFERS)`.
- `pg_stat_statements` — `SELECT query, calls, total_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;`.
- `VACUUM ANALYZE tablename;` — when bloat or stale stats are suspected.
- Connection poolers like PgBouncer are recommended for any real traffic.

## Reliability tips

- Use UUID primary keys where clients need to create IDs.
- Prefer `timestamptz` (with timezone) over `timestamp` for anything absolute.
- `NOW()` / `CURRENT_TIMESTAMP` are stable within a transaction — use `clock_timestamp()` for wall-clock.
""",
    },
    {
        "name": "sqlite",
        "description": "Use SQLite as a zero-config local relational store. Covers CLI (`sqlite3`), Python `sqlite3` module, WAL mode, performance pragmas, and backup.",
        "homepage": "https://www.sqlite.org/docs.html",
        "category": "databases",
        "depends": "sql-patterns",
        "body": """
# SQLite

## CLI

```bash
sqlite3 file.db                    # open interactive shell
sqlite3 file.db < query.sql        # run script
sqlite3 file.db ".schema"          # print schema
sqlite3 file.db ".tables"
sqlite3 file.db ".mode box"
sqlite3 file.db ".headers on"
sqlite3 file.db ".output out.csv"  ".mode csv"  "SELECT * FROM t;"
```

## Python

```python
import sqlite3
with sqlite3.connect("file.db") as con:
    con.execute("PRAGMA journal_mode = WAL;")          # best for concurrent reads + single writer
    con.execute("PRAGMA foreign_keys = ON;")            # enforce FKs
    con.execute("CREATE TABLE IF NOT EXISTS t(id INTEGER PRIMARY KEY, name TEXT NOT NULL);")
    con.executemany("INSERT INTO t(name) VALUES (?)", [("a",), ("b",)])
    for row in con.execute("SELECT id, name FROM t WHERE id > ?", (0,)):
        print(row)
```

Use `?` placeholders — **never** f-string SQL.

## Performance pragmas

```sql
PRAGMA journal_mode = WAL;       -- readers don't block writers
PRAGMA synchronous = NORMAL;     -- safer than OFF, faster than FULL
PRAGMA busy_timeout = 5000;      -- wait up to 5s on lock contention (ms)
PRAGMA temp_store = MEMORY;
PRAGMA cache_size = -20000;      -- ~20 MB of page cache
PRAGMA mmap_size = 30000000000;  -- up to 30GB of mmap I/O
PRAGMA foreign_keys = ON;
```

## Backup

```sql
VACUUM INTO 'backup.db';         -- atomic, online, on-disk copy
```

Or from shell: `sqlite3 live.db ".backup backup.db"`.

## Tips

- SQLite is **single-writer, multi-reader**; WAL mode removes most read/write contention.
- `INTEGER PRIMARY KEY` becomes an alias for `rowid` — 64-bit autoinc, fastest.
- Avoid `SELECT *` in hot paths.
- `CREATE INDEX` / `CREATE UNIQUE INDEX` on columns used in `WHERE` / `JOIN`.
- For bulk insert, wrap in `BEGIN; … COMMIT;` — otherwise each row is a transaction.
- `sqlite3_analyzer` / `sqlite3 file.db "SELECT name, SUM(pgsize) FROM dbstat GROUP BY name ORDER BY 2 DESC;"` — size breakdown.
""",
    },
    {
        "name": "redis",
        "description": "Redis command patterns: key/value, hashes, lists, sets, sorted sets, streams, pub/sub, pipelines, transactions, and Lua scripting.",
        "homepage": "https://redis.io/commands/",
        "category": "databases",
        "depends": "",
        "body": """
# Redis

## CLI one-liners

```bash
redis-cli -h localhost -p 6379 -a $REDIS_PASSWORD PING
redis-cli SET key value EX 3600          # with TTL
redis-cli GET key
redis-cli DEL key
redis-cli KEYS "prefix:*"                 # O(n), do NOT use in prod — use SCAN
redis-cli SCAN 0 MATCH "prefix:*" COUNT 100
redis-cli TTL key
redis-cli EXPIRE key 60
redis-cli INFO memory | grep used_memory_human
```

## Data structure cheatsheet

| Structure | Commands | Use case |
|-----------|----------|----------|
| String    | GET/SET/DEL/INCR/SETNX | cache, counters, locks (`SET lock 1 NX EX 30`) |
| Hash      | HSET/HGET/HGETALL/HDEL/HINCRBY | object fields |
| List      | LPUSH/RPUSH/LPOP/RPOP/LRANGE/LTRIM | queues, stacks, recent-items |
| Set       | SADD/SREM/SISMEMBER/SMEMBERS/SINTER/SUNION | unique members, intersections |
| Sorted set| ZADD/ZRANGE/ZREVRANGE/ZRANK/ZINCRBY | leaderboards, time-series |
| Stream    | XADD/XREAD/XGROUP ... | append-log, consumer groups |

## Python

```python
import redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)
r.set("k", "v", ex=300)
print(r.get("k"))

# Pipeline (round-trip batching)
with r.pipeline(transaction=False) as pipe:
    pipe.set("a", "1").incr("counter").zadd("board", {"alice": 100})
    results = pipe.execute()

# Simple lock
if r.set("lock:job", "me", nx=True, ex=30):
    try:
        do_work()
    finally:
        r.delete("lock:job")
```

## Pub/sub

```bash
redis-cli SUBSCRIBE channel_name
redis-cli PUBLISH channel_name "msg"
```

```python
pubsub = r.pubsub()
pubsub.subscribe("channel_name")
for m in pubsub.listen():
    print(m)
```

## Transactions (MULTI/EXEC) — note Lua is usually more ergonomic

```python
with r.pipeline(transaction=True) as pipe:
    pipe.multi()
    pipe.incr("counter")
    pipe.execute()
```

## Lua script for atomic compound operations

```python
script = """
local v = redis.call("GET", KEYS[1])
if not v then redis.call("SET", KEYS[1], ARGV[1]); return ARGV[1] end
return v
"""
print(r.eval(script, 1, "counter", "1"))
```

## Reliability tips

- `EX` seconds, `PX` milliseconds, `EXAT` unix-second-timestamp, `PXAT` ms-timestamp for TTL.
- Never use `KEYS` on production — use `SCAN 0 MATCH pattern COUNT 200`.
- Keep keys small; use a naming convention with colons: `app:user:42:profile`.
- `INFO stats` / `INFO memory` / `INFO replication` — health checks.
- Redis 7+: `FUNCTION` / `FCALL` replace ad-hoc EVAL for reusable Lua.
""",
    },

    # --- 6. Testing -----------------------------------------------------------------
    {
        "name": "pytest-python",
        "description": "Write Python tests with pytest. Covers fixtures (session/module/function), parametrize, tmp_path, capsys, monkeypatch, mocking with unittest.mock, and pytest plugins.",
        "homepage": "https://docs.pytest.org/",
        "category": "testing",
        "depends": "",
        "body": """
# pytest

## Run tests

```bash
pytest tests/
pytest tests/test_x.py -v -k "keyword"         # filter by name substring
pytest --tb=short                                # shorter traceback
pytest -x                                        # stop on first failure
pytest --pdb                                     # drop into debugger on failure
pytest --co                                      # collect / list tests only
pytest tests/ --cov=src --cov-report=term-missing  # coverage.py via pytest-cov
```

## Simple test

```python
def add(a, b): return a + b

def test_add_basic():
    assert add(1, 2) == 3

def test_add_raises_on_non_number():
    import pytest
    with pytest.raises(TypeError):
        add("a", 1)
```

## Parametrize — data-driven tests

```python
import pytest
@pytest.mark.parametrize("a,b,expected", [(1,2,3), (0,0,0), (-1, 1, 0)])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

## Fixtures

```python
import pytest, tempfile, json

@pytest.fixture
def sample_data():
    return {"name": "alice", "age": 30}

@pytest.fixture(scope="session")
def shared_db():
    # setup
    db = SomeDB()
    yield db
    db.close()  # teardown

@pytest.fixture
def tmp_json_file(tmp_path, sample_data):
    p = tmp_path / "data.json"
    p.write_text(json.dumps(sample_data))
    return p

def test_load(tmp_json_file):
    assert json.loads(tmp_json_file.read_text())["name"] == "alice"
```

## Useful built-in fixtures

- `tmp_path` — unique temp dir per test (pathlib.Path).
- `tmp_path_factory` — create temps at wider scopes.
- `capsys` / `capfd` — capture stdout/stderr.
- `caplog` — capture logging records.
- `monkeypatch` — setattr/env/item patches that are undone after the test.
- `request` — access test metadata.

## Mocking with `unittest.mock`

```python
from unittest.mock import patch, MagicMock

def test_remote_call():
    with patch("mymodule.urllib.request.urlopen") as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = b'{"ok":true}'
        result = mymodule.remote_call("https://x")
    assert result == {"ok": True}

# Or decorator form
@patch("mymodule.urllib.request.urlopen")
def test_another(mock_open): ...
```

## Markers — tagging / skipping

```python
@pytest.mark.skipif(sys.platform == "win32", reason="unix only")
def test_linux_only(): ...

@pytest.mark.slow
def test_long_running(): ...
# then run: pytest -m "not slow"
```

## Useful plugins

- `pytest-cov` — coverage.
- `pytest-mock` — convenience `mocker` fixture.
- `pytest-asyncio` — `@pytest.mark.asyncio` / async fixtures.
- `pytest-xdist` — `-n auto` parallel execution across cores.
- `hypothesis` — property-based testing.

## Tips

- Keep tests independent; let fixtures provide state.
- Avoid `assert True` / no-op tests.
- Prefer real implementations when cheap; mock at service / external boundaries.
- Name tests for intent: `test_<behavior>_<condition>`.
""",
    },
    {
        "name": "testing-patterns",
        "description": "General testing patterns: AAA (Arrange-Act-Assert), given/when/then, test pyramid, property-based testing, golden files, fakes vs mocks, and reproducibility.",
        "homepage": "https://martinfowler.com/articles/mocksArentStubs.html",
        "category": "testing",
        "depends": "",
        "body": """
# Testing Patterns

## Test structure: AAA / Given-When-Then

```python
def test_order_total_with_discount():
    # Arrange / Given
    order = Order(items=[Item(price=100, qty=2)], discount=10)

    # Act / When
    total = order.total()

    # Assert / Then
    assert total == 180
```

Split large tests into multiple tests when there are multiple independent claims.

## Test pyramid

- **Unit tests** — fast, in-process, no IO; exercise functions/classes. Many, cheap.
- **Integration tests** — exercise real boundaries (HTTP, DB, message bus). Fewer.
- **End-to-end tests** — real user workflows across services. Fewest, brittle, expensive.

## Fakes vs Mocks vs Stubs

| Type | Role |
|------|------|
| **Fake** | Working implementation simplified for tests (e.g. `InMemoryPaymentGateway`). |
| **Stub** | Returns canned answers; no assertions made about calls. |
| **Mock** | Records calls; test verifies "was called N times with these args". |

Use fakes by default; use mocks only when you need to assert on interaction *shape*, not just *result*.

## Golden-file / snapshot tests

For large, stable outputs (CLI, rendered HTML, generated JSON), save the expected output to a committed file and diff against it:

```python
def test_render(tmp_path, snapshot):
    out = render()
    assert out == Path("fixtures/rendered.json").read_text()
# or pytest plugins: syrupy, pytest-regressions
```

## Property-based testing (hypothesis)

```python
from hypothesis import given
from hypothesis.strategies import integers

@given(integers(), integers())
def test_add_is_commutative(a, b):
    assert add(a, b) == add(b, a)
```

## Determinism tips

- Freeze time: `freezegun.freeze_time("2025-01-01")` / `datetime.now` monkey-patching.
- Use `random.seed(42)` inside tests if randomness is used.
- Sort unordered collections before assertion — or use sets.
- Prefer `tmp_path` / fixture-managed directories over hard-coded paths.

## Test doubles for external APIs

- Record-replay: `vcr.py` (Python) / `Polly.js` (JS) tape-record HTTP traffic and replay it.
- Provide a `--live` flag to your test suite to opt in to real-network tests.

## Code coverage hygiene

- Run coverage; don't chase 100% religiously, but investigate drops from a known baseline.
- Exclude generated / glue code.
- `--cov-report=term-missing` shows uncovered lines.

## Reproducibility

- Pin test dependencies (lock files for JS/Python).
- Store seed / RNG state for flaky failures; report it.
""",
    },

    # --- 7. DevOps / CI -------------------------------------------------------------
    {
        "name": "github-actions",
        "description": "Write GitHub Actions workflows: triggers, jobs, steps, runners, caching, secrets, matrix builds, reusable workflows, and common security checks.",
        "homepage": "https://docs.github.com/actions",
        "category": "devops",
        "depends": "",
        "body": """
# GitHub Actions

## File location

Workflows live in `.github/workflows/<name>.yaml`.

## Minimal example — lint + test on push/PR

```yaml
name: CI
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with: { python-version: "3.12" }

      - name: Install deps
        run: python -m pip install -e .[test]

      - name: Run tests
        run: python -m pytest tests/ -q
```

## Common triggers

```yaml
on:
  push: { branches: [main], tags: ['v*'] }
  pull_request:
  schedule: [{ cron: "30 6 * * 1" }]       # UTC, every Monday 06:30
  workflow_dispatch:                          # manual via UI / API
  release: { types: [published] }
  workflow_call:                              # reusable — inputs + secrets
```

## Matrix builds

```yaml
jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.10", "3.11", "3.12"]
    runs-on: ${{ matrix.os }}
    steps: [...]
```

## Caching

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml', '**/requirements*.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

For node: cache `node_modules` via `**/package-lock.json` hash; for uv: cache `~/.cache/uv`.

## Secrets & environment

- Reference secrets via `${{ secrets.MY_TOKEN }}` — never log, never echo.
- Repository secrets: repo → Settings → Secrets