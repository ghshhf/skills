---
TERMUX_PKG_NAME: npm-javascript
TERMUX_PKG_DESCRIPTION: "Work with npm, package.json scripts, dependency management, semver, publishing, and CI reproducibility"
TERMUX_PKG_HOMEPAGE: https://docs.npmjs.com/
TERMUX_PKG_MAINTAINER: "@agent-skills"
TERMUX_PKG_VERSION: 1.0.0
TERMUX_PKG_LICENSE: MIT
TERMUX_PKG_DEPENDS: ""
TERMUX_PKG_CATEGORY: dev-tools
---

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

