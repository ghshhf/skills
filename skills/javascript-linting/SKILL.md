---
TERMUX_PKG_NAME: javascript-linting
TERMUX_PKG_DESCRIPTION: "ESLint flat config, Prettier formatting, editorconfig, and commit hooks"
TERMUX_PKG_HOMEPAGE: https://eslint.org/
TERMUX_PKG_MAINTAINER: "@agent-skills"
TERMUX_PKG_VERSION: 1.0.0
TERMUX_PKG_LICENSE: MIT
TERMUX_PKG_DEPENDS: ""
TERMUX_PKG_CATEGORY: code-quality
---

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

