#!/usr/bin/env python3
"""Generate 25 new skills SKILL.md files."""
from pathlib import Path
import textwrap

ROOT = Path("/workspace/skills-project")
SKILLS_DIR = ROOT / "skills"

SKILLS = []

def add(name, category, description, homepage, title, body):
    SKILLS.append({
        "name": name,
        "category": category,
        "description": description,
        "homepage": homepage,
        "title": title,
        "body": textwrap.dedent(body).strip() + "\n",
    })

add("npm-javascript", "dev-tools",
    "Work with npm, package.json scripts, dependency management, semver, publishing, and CI reproducibility",
    "https://docs.npmjs.com/",
    "npm and JavaScript Package Management",
    """
    # npm and JavaScript Package Management

    Use npm to install dependencies, run scripts, and publish Node.js packages.

    ## package.json and scripts

    Every Node.js project keeps metadata and a `scripts` object of named commands:

    ```json
    {
      "name": "my-app",
      "version": "1.0.0",
      "scripts": {
        "build": "tsc",
        "test": "vitest",
        "start": "node dist/index.js",
        "lint": "eslint src"
      },
      "dependencies": { "lodash": "^4.17.21" },
      "devDependencies": { "typescript": "~5.4.0" }
    }
    ```

    Run scripts with `npm run <name>` (the `run` is implicit for `npm start`, `npm test`, `npm restart`, and `npm stop`).

    ## Installing dependencies

    - `npm install` (or `npm i`) — install all deps, writing/updating `package-lock.json`.
    - `npm install <pkg>` — install a runtime dependency added to `dependencies`.
    - `npm install --save-dev <pkg>` — install as `devDependencies`.
    - `npm install --no-save <pkg>` — install without writing to `package.json`.
    - `npm ci` — clean install using exact versions from `package-lock.json`. Use this in CI for reproducible builds.
    - `npx <cmd>` — run a locally-installed or on-the-fly downloaded binary, e.g. `npx tsc --noEmit`, `npx create-vite@latest my-app`.

    ## Dependency lifecycle

    - `npm ls` — print dependency tree.
    - `npm outdated` — list packages with newer versions available.
    - `npm update` — update packages within semver ranges.
    - `npm uninstall <pkg>` — remove a package.

    ## Semver range operators in package.json

    - `^1.2.3` — compatible changes; `>=1.2.3 <2.0.0`. Default for new installs.
    - `~1.2.3` — patch only; `>=1.2.3 <1.3.0`.
    - `1.2.3` — exact version (no prefix pins to this exact version).
    - `>=1.2.3` — at least this version.
    - `*` or `""` — any version (not recommended in projects).

    ## Lockfile and CI reproducibility

    `package-lock.json` pins exact installed versions. Commit this file. In CI, prefer `npm ci` over `npm install` for deterministic installs.

    ## Publishing

    ```sh
    npm version patch
    npm publish --access public
    ```

    Before publishing, use `npm pack` to preview tarball locally.

    ## Security

    - `npm audit` — print known vulnerabilities.
    - `npm audit fix` — automatically install compatible updates to vulnerable dependencies.
    - `npm fund` — list funding information for installed packages.

    Best practice: commit `package-lock.json` and `.gitignore` `node_modules`, and run `npm ci` in CI for reproducibility.
    """)

add("javascript-linting", "code-quality",
    "ESLint flat config, Prettier formatting, editorconfig, and commit hooks",
    "https://eslint.org/",
    "JavaScript Linting and Formatting",
    """
    # JavaScript Linting and Formatting

    Use ESLint for linting and Prettier for formatting to keep JavaScript/TypeScript code consistent.

    ## ESLint flat config (eslint.config.mjs)

    New ESLint 9 uses flat config files (ESM JavaScript files) without JSON or YAML.

    ```mjs
    import js from "@eslint/js";
    import tseslint from "typescript-eslint";

    export default [
      js.configs.recommended,
      ...tseslint.configs.recommended,
      {
        files: ["**/*.{js,mjs,cjs,ts,mts,cts,jsx,tsx}"],
        languageOptions: { ecmaVersion: 2022, sourceType: "module" },
        rules: { "no-unused-vars": "warn", "no-console": "off", "prefer-const": "error" },
      },
      { ignores: ["dist/", "node_modules/"] },
    ];
    ```

    Install dependencies:

    ```sh
    npm install --save-dev eslint @eslint/js typescript-eslint
    ```

    Run with:

    ```sh
    npx eslint .
    npx eslint --fix .
    ```

    ## Prettier

    Prettier formats code. Keep ESLint for style rules and Prettier for formatting.

    ```sh
    npm install --save-dev --save-exact prettier
    npx prettier --write "src/**/*.ts"
    npx prettier --check "src/**/*.ts"
    ```

    Create `.prettierrc`:

    ```json
    { "semi": true, "singleQuote": false, "trailingComma": "all", "printWidth": 100, "tabWidth": 2 }
    ```

    ## EditorConfig

    `.editorconfig` standardizes editor defaults across editors:

    ```
    root = true

    [*]
    indent_style = space
    indent_size = 2
    end_of_line = lf
    charset = utf-8
    trim_trailing_whitespace = true
    insert_final_newline = true
    ```

    ## Ignore files

    - `.eslintignore` — paths ESLint skips (one per line).
    - `.prettierignore` — paths Prettier skips.

    Both default-ignore `node_modules/` and build output dirs.

    ## Commit hooks with simple-git-hooks + lint-staged

    ```sh
    npm install --save-dev simple-git-hooks lint-staged
    ```

    In `package.json` add:

    ```json
    {
      "scripts": { "prepare": "simple-git-hooks" },
      "simple-git-hooks": { "pre-commit": "npx lint-staged" },
      "lint-staged": {
        "*.{js,ts,jsx,tsx}": ["eslint --fix", "prettier --write"],
        "*.{json,md,yml}": ["prettier --write"]
      }
    }
    ```

    Then run `npm run prepare` once, and pre-commit hooks will run on future commits.
    """)

add("json-yaml-processing", "text",
    "Pretty-print, query, and convert JSON and YAML with python, jq, and yq",
    "https://stedolan.github.io/jq/",
    "JSON and YAML Processing",
    """
    # JSON and YAML Processing

    Pretty-print, query, and convert JSON and YAML.

    ## Pretty-printing JSON

    ```sh
    python -m json.tool data.json
    python -m json.tool --indent 2 file.json
    cat file.json | python -m json.tool
    ```

    ## jq basics

    `jq` is a lightweight JSON processor and highlighter.

    ```sh
    jq '.name' data.json                        # extract a field
    jq '.user.name' data.json                   # nested field
    jq '.items[]' data.json                     # iterate an array
    jq '.users[] | select(.active == true) | {id, name}' data.json
    ```

    Output formatting:

    ```sh
    jq --tab . file.json         # use tab indentation
    jq -r .name file.json        # --raw-output prints plain strings without quotes
    jq -c . file.json            # compact, one JSON per line
    ```

    Piping from curl:

    ```sh
    curl -s https://api.github.com/users/octocat/repos | jq '.[].full_name'
    ```

    Filtering with map, sort_by, length, and select:

    ```sh
    jq '.data | map(select(.age > 30)) | sort_by(.name)' file.json
    jq '[.items[] | {name, id}] | length' file.json
    ```

    ## yq for YAML

    `yq` is a `jq` wrapper for YAML, using similar syntax.

    ```sh
    yq '.' file.yaml                                # pretty-print YAML
    yq -o=json file.yaml > file.json                 # YAML to JSON
    yq -P file.json > file.yaml                      # JSON to YAML
    yq '.spec.containers[0].image' k8s.yaml          # query a field
    ```

    ## Converting in Python

    ```python
    import json, yaml

    with open("data.json") as f:
        data = json.load(f)

    with open("data.yaml", "w") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)

    with open("data.yaml") as f:
        data = yaml.safe_load(f)

    print(json.dumps(data, indent=2))
    ```

    ## Common pitfalls

    - YAML numbers: `0755` is parsed as octal (leading zero triggers octal interpretation). Quote strings like `"0755"` to force strings.
    - YAML booleans: `true`, `false`, `yes`, `no`, `on`, `off`, and `null` are parsed as bool/null without quotes.
    - YAML strings containing `:` or `#` need to be quoted.
    - YAML is indentation-sensitive (2 spaces typical). Mixing tabs and spaces breaks parsing.
    - JSON has no comments; YAML has `#` comments.
    """)

# Write first batch
for s in SKILLS:
    d = SKILLS_DIR / s["name"]
    d.mkdir(parents=True, exist_ok=True)
    content = f"""---
TERMUX_PKG_NAME: {s["name"]}
TERMUX_PKG_DESCRIPTION: "{s["description"]}"
TERMUX_PKG_HOMEPAGE: {s["homepage"]}
TERMUX_PKG_MAINTAINER: "@agent-skills"
TERMUX_PKG_VERSION: 1.0.0
TERMUX_PKG_LICENSE: MIT
TERMUX_PKG_DEPENDS: ""
TERMUX_PKG_CATEGORY: {s["category"]}
---

{s["body"]}
"""
    (d / "SKILL.md").write_text(content, encoding="utf-8")
    print(f"wrote {s['name']}")

print(f"Total: {len(SKILLS)} skills written.")
