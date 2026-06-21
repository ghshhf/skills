---
TERMUX_PKG_NAME: json-yaml-processing
TERMUX_PKG_DESCRIPTION: "Pretty-print, query, and convert JSON and YAML with python, jq, and yq"
TERMUX_PKG_HOMEPAGE: https://stedolan.github.io/jq/
TERMUX_PKG_MAINTAINER: "@agent-skills"
TERMUX_PKG_VERSION: 1.0.0
TERMUX_PKG_LICENSE: MIT
TERMUX_PKG_DEPENDS: ""
TERMUX_PKG_CATEGORY: text
---

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

