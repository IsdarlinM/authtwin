# CLI Reference — authtwin v0.2.0

Generated from the registered command surface. Every registered command below uses the same Click/Typer command tree used at runtime.

## Root help

```text
Usage: authtwin [OPTIONS] COMMAND [ARGS]...

  Authorization Digital Twin — evidence-native authorization modeling.

Options:
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.
  -h, --help            Show this message and exit.

Commands:
  version
  doctor            Check runtime, SRIC integration, plugin registry and...
  init
  workspace         Manage isolated investigation workspaces.
  config            Inspect configuration and explain where a value comes...
  actor
  resource
  observe
  invariant
  import
  model
  matrix
  state-machine     Show observed resource-state transitions; missing...
  compare
  findings
  validate
  coverage          Measure observed authorization matrix coverage;...
  discover          Summarize deterministic resource/operation candidates...
  counterfactual    Generate safe counterfactual test plans; never...
  session           Append or inspect identity/session lifecycle events...
  invariant-dsl     Parse and install a small auditable...
  graphql           Show authorization observations grouped by GraphQL...
  batch             Analyze supplied batch-operation item decisions; no...
  skeptic           Generate alternative explanations, missing evidence...
  export
  report
  demo
  web
  evidence          Store a local evidence artifact in SRIC...
  ai                Show AI mode.
  plugins           List SRIC plugin manifests without auto-executing...
  scope             Evaluate a target using SRIC Scope Engine; no request...
  query             Search this workspace's shared SRIC graph.
  notebook          List/append research notes or manage saved...
  evidence-lineage  Explain evidence lineage and the reason a derived...
  jobs              List/inspect/cancel persistent SRIC jobs for this...
  update            Check/install a signed wheel release.
  help
```

## `authtwin actor`

```text
Usage: authtwin actor [OPTIONS] WORKSPACE ACTOR_ID NAME

Arguments:
  WORKSPACE  [required]
  ACTOR_ID   [required]
  NAME       [required]

Options:
  --role TEXT
  --tenant TEXT
  --suspended / --no-suspended  [default: no-suspended]
  --root PATH                   [default: /home/oai/.authtwin/workspaces]
  -h, --help                    Show this message and exit.
```

## `authtwin ai`

```text
Usage: authtwin ai [OPTIONS]

  Show AI mode. Cloud AI remains disabled until explicitly configured.

Options:
  -h, --help  Show this message and exit.
```

## `authtwin batch`

```text
Usage: authtwin batch [OPTIONS] WORKSPACE

  Analyze supplied batch-operation item decisions; no requests are generated.

Arguments:
  WORKSPACE  [required]

Options:
  --root PATH  [default: /home/oai/.authtwin/workspaces]
  -h, --help   Show this message and exit.
```

## `authtwin compare`

```text
Usage: authtwin compare [OPTIONS] WORKSPACE ACTOR_A ACTOR_B

Arguments:
  WORKSPACE  [required]
  ACTOR_A    [required]
  ACTOR_B    [required]

Options:
  --root PATH  [default: /home/oai/.authtwin/workspaces]
  -h, --help   Show this message and exit.
```

## `authtwin config`

```text
Usage: authtwin config [OPTIONS] [ACTION] [KEY]

  Inspect configuration and explain where a value comes from.

Arguments:
  [ACTION]  show|explain  [default: show]
  [KEY]

Options:
  --workspace TEXT
  --root PATH       [default: /home/oai/.authtwin/workspaces]
  -h, --help        Show this message and exit.
```

## `authtwin counterfactual`

```text
Usage: authtwin counterfactual [OPTIONS] WORKSPACE

  Generate safe counterfactual test plans; never executes them automatically.

Arguments:
  WORKSPACE  [required]

Options:
  --observation TEXT
  --root PATH         [default: /home/oai/.authtwin/workspaces]
  -h, --help          Show this message and exit.
```

## `authtwin coverage`

```text
Usage: authtwin coverage [OPTIONS] WORKSPACE

  Measure observed authorization matrix coverage; UNKNOWN cells are not
  findings.

Arguments:
  WORKSPACE  [required]

Options:
  --root PATH  [default: /home/oai/.authtwin/workspaces]
  -h, --help   Show this message and exit.
```

## `authtwin demo`

```text
Usage: authtwin demo [OPTIONS]

Options:
  --workspace TEXT  [default: demo]
  --root PATH       [default: /home/oai/.authtwin/workspaces]
  -h, --help        Show this message and exit.
```

## `authtwin discover`

```text
Usage: authtwin discover [OPTIONS] WORKSPACE

  Summarize deterministic resource/operation candidates from supplied
  observations.

Arguments:
  WORKSPACE  [required]

Options:
  --root PATH  [default: /home/oai/.authtwin/workspaces]
  -h, --help   Show this message and exit.
```

## `authtwin doctor`

```text
Usage: authtwin doctor [OPTIONS]

  Check runtime, SRIC integration, plugin registry and secure defaults.

Options:
  -h, --help  Show this message and exit.
```

## `authtwin evidence`

```text
Usage: authtwin evidence [OPTIONS] WORKSPACE FILE

  Store a local evidence artifact in SRIC content-addressed storage.

Arguments:
  WORKSPACE  [required]
  FILE       [required]

Options:
  --source TEXT      [default: user]
  --media-type TEXT  [default: application/octet-stream]
  --redacted
  --root PATH        [default: /home/oai/.authtwin/workspaces]
  -h, --help         Show this message and exit.
```

## `authtwin evidence-lineage`

```text
Usage: authtwin evidence-lineage [OPTIONS] WORKSPACE ARTIFACT_ID

  Explain evidence lineage and the reason a derived artifact is visible.

Arguments:
  WORKSPACE    [required]
  ARTIFACT_ID  [required]

Options:
  --root PATH  [default: /home/oai/.authtwin/workspaces]
  -h, --help   Show this message and exit.
```

## `authtwin export`

```text
Usage: authtwin export [OPTIONS] WORKSPACE OUTPUT

Arguments:
  WORKSPACE  [required]
  OUTPUT     [required]

Options:
  --rcap       Export a valid RCAP capsule containing the authorization model
               as evidence.
  --root PATH  [default: /home/oai/.authtwin/workspaces]
  -h, --help   Show this message and exit.
```

## `authtwin findings`

```text
Usage: authtwin findings [OPTIONS] WORKSPACE

Arguments:
  WORKSPACE  [required]

Options:
  --root PATH  [default: /home/oai/.authtwin/workspaces]
  -h, --help   Show this message and exit.
```

## `authtwin graphql`

```text
Usage: authtwin graphql [OPTIONS] WORKSPACE

  Show authorization observations grouped by GraphQL operation/field metadata.

Arguments:
  WORKSPACE  [required]

Options:
  --root PATH  [default: /home/oai/.authtwin/workspaces]
  -h, --help   Show this message and exit.
```

## `authtwin help`

```text
Usage: authtwin help [OPTIONS] [COMMAND]

Arguments:
  [COMMAND]

Options:
  -h, --help  Show this message and exit.
```

## `authtwin import`

```text
Usage: authtwin import [OPTIONS] WORKSPACE PATH

Arguments:
  WORKSPACE  [required]
  PATH       [required]

Options:
  --root PATH  [default: /home/oai/.authtwin/workspaces]
  -h, --help   Show this message and exit.
```

## `authtwin init`

```text
Usage: authtwin init [OPTIONS] NAME

Arguments:
  NAME  [required]

Options:
  --root PATH  [default: /home/oai/.authtwin/workspaces]
  -h, --help   Show this message and exit.
```

## `authtwin invariant`

```text
Usage: authtwin invariant [OPTIONS] WORKSPACE INVARIANT_ID DESCRIPTION KIND:{D
                          ENY_OTHER_OWNER_MUTATION|DENY_SUSPENDED|DENY_REVOKED
                          |CUSTOM}

Arguments:
  WORKSPACE                       [required]
  INVARIANT_ID                    [required]
  DESCRIPTION                     [required]
  KIND:{DENY_OTHER_OWNER_MUTATION|DENY_SUSPENDED|DENY_REVOKED|CUSTOM}
                                  [required]

Options:
  --operation TEXT
  --root PATH       [default: /home/oai/.authtwin/workspaces]
  -h, --help        Show this message and exit.
```

## `authtwin invariant-dsl`

```text
Usage: authtwin invariant-dsl [OPTIONS] WORKSPACE FILE

  Parse and install a small auditable authorization-invariant DSL.

Arguments:
  WORKSPACE  [required]
  FILE       [required]

Options:
  --root PATH  [default: /home/oai/.authtwin/workspaces]
  -h, --help   Show this message and exit.
```

## `authtwin jobs`

```text
Usage: authtwin jobs [OPTIONS] WORKSPACE

  List/inspect/cancel persistent SRIC jobs for this workspace.

Arguments:
  WORKSPACE  [required]

Options:
  --id TEXT
  --cancel
  --root PATH  [default: /home/oai/.authtwin/workspaces]
  -h, --help   Show this message and exit.
```

## `authtwin matrix`

```text
Usage: authtwin matrix [OPTIONS] WORKSPACE

Arguments:
  WORKSPACE  [required]

Options:
  --root PATH  [default: /home/oai/.authtwin/workspaces]
  -h, --help   Show this message and exit.
```

## `authtwin model`

```text
Usage: authtwin model [OPTIONS] WORKSPACE

Arguments:
  WORKSPACE  [required]

Options:
  --root PATH  [default: /home/oai/.authtwin/workspaces]
  -h, --help   Show this message and exit.
```

## `authtwin notebook`

```text
Usage: authtwin notebook [OPTIONS] WORKSPACE

  List/append research notes or manage saved investigation queries.

Arguments:
  WORKSPACE  [required]

Options:
  --type TEXT
  --title TEXT
  --body TEXT
  --status TEXT           [default: OBSERVED]
  --save-query-name TEXT
  --query TEXT
  --list-queries
  --root PATH             [default: /home/oai/.authtwin/workspaces]
  -h, --help              Show this message and exit.
```

## `authtwin observe`

```text
Usage: authtwin observe [OPTIONS] WORKSPACE OBSERVATION_ID ACTOR_ID
                        RESOURCE_ID OPERATION DECISION:{ALLOW|DENY|UNKNOWN}

Arguments:
  WORKSPACE                      [required]
  OBSERVATION_ID                 [required]
  ACTOR_ID                       [required]
  RESOURCE_ID                    [required]
  OPERATION                      [required]
  DECISION:{ALLOW|DENY|UNKNOWN}  [required]

Options:
  --evidence TEXT
  --status-code INTEGER
  --state TEXT
  --root PATH            [default: /home/oai/.authtwin/workspaces]
  -h, --help             Show this message and exit.
```

## `authtwin plugins`

```text
Usage: authtwin plugins [OPTIONS]

  List SRIC plugin manifests without auto-executing plugin code.

Options:
  --path PATH  [default: /home/oai/.sric/plugins]
  -h, --help   Show this message and exit.
```

## `authtwin query`

```text
Usage: authtwin query [OPTIONS] WORKSPACE QUERY

  Search this workspace's shared SRIC graph.

Arguments:
  WORKSPACE  [required]
  QUERY      [required]

Options:
  --limit INTEGER RANGE  [default: 50; 1<=x<=500]
  --root PATH            [default: /home/oai/.authtwin/workspaces]
  -h, --help             Show this message and exit.
```

## `authtwin report`

```text
Usage: authtwin report [OPTIONS] WORKSPACE OUTPUT

Arguments:
  WORKSPACE  [required]
  OUTPUT     [required]

Options:
  --root PATH  [default: /home/oai/.authtwin/workspaces]
  -h, --help   Show this message and exit.
```

## `authtwin resource`

```text
Usage: authtwin resource [OPTIONS] WORKSPACE RESOURCE_ID RESOURCE_TYPE

Arguments:
  WORKSPACE      [required]
  RESOURCE_ID    [required]
  RESOURCE_TYPE  [required]

Options:
  --owner TEXT
  --tenant TEXT
  --state TEXT        [default: active]
  --shared-with TEXT
  --root PATH         [default: /home/oai/.authtwin/workspaces]
  -h, --help          Show this message and exit.
```

## `authtwin scope`

```text
Usage: authtwin scope [OPTIONS] TARGET

  Evaluate a target using SRIC Scope Engine; no request is sent.

Arguments:
  TARGET  [required]

Options:
  --method TEXT  [default: GET]
  --allow TEXT
  --deny TEXT
  -h, --help     Show this message and exit.
```

## `authtwin session`

```text
Usage: authtwin session [OPTIONS] WORKSPACE ACTOR_ID

  Append or inspect identity/session lifecycle events without storing raw
  session secrets.

Arguments:
  WORKSPACE  [required]
  ACTOR_ID   [required]

Options:
  --event-id TEXT
  --event-type TEXT
  --evidence TEXT
  --root PATH        [default: /home/oai/.authtwin/workspaces]
  -h, --help         Show this message and exit.
```

## `authtwin skeptic`

```text
Usage: authtwin skeptic [OPTIONS] WORKSPACE FINDING_ID

  Generate alternative explanations, missing evidence and counter-tests for a
  candidate.

Arguments:
  WORKSPACE   [required]
  FINDING_ID  [required]

Options:
  --root PATH  [default: /home/oai/.authtwin/workspaces]
  -h, --help   Show this message and exit.
```

## `authtwin state-machine`

```text
Usage: authtwin state-machine [OPTIONS] WORKSPACE

  Show observed resource-state transitions; missing history remains UNKNOWN.

Arguments:
  WORKSPACE  [required]

Options:
  --root PATH  [default: /home/oai/.authtwin/workspaces]
  -h, --help   Show this message and exit.
```

## `authtwin update`

```text
Usage: authtwin update [OPTIONS]

  Check/install a signed wheel release. Never performs a blind git pull.

Options:
  --check
  --manifest TEXT
  --public-key PATH
  -h, --help         Show this message and exit.
```

## `authtwin validate`

```text
Usage: authtwin validate [OPTIONS] WORKSPACE FINDING_ID

Arguments:
  WORKSPACE   [required]
  FINDING_ID  [required]

Options:
  --evidence TEXT  [required]
  --note TEXT      [required]
  --confirm
  --root PATH      [default: /home/oai/.authtwin/workspaces]
  -h, --help       Show this message and exit.
```

## `authtwin version`

```text
Usage: authtwin version [OPTIONS]

Options:
  -h, --help  Show this message and exit.
```

## `authtwin web`

```text
Usage: authtwin web [OPTIONS] WORKSPACE

Arguments:
  WORKSPACE  [required]

Options:
  --host TEXT     [default: 127.0.0.1]
  --port INTEGER  [default: 8766]
  --root PATH     [default: /home/oai/.authtwin/workspaces]
  -h, --help      Show this message and exit.
```

## `authtwin workspace`

```text
Usage: authtwin workspace [OPTIONS] [ACTION] [NAME]

  Manage isolated investigation workspaces.

Arguments:
  [ACTION]  create|list|show|archive  [default: list]
  [NAME]

Options:
  --root PATH  [default: /home/oai/.authtwin/workspaces]
  --confirm    Required for archive.
  -h, --help   Show this message and exit.
```
