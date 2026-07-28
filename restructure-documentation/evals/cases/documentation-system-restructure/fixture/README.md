# Lantern CLI

Lantern scans workspaces.

Set `LANTERN_CACHE_DIR` if you do not want `.lantern-cache`. Configuration schema version 3 is current. A workspace is a folder with `lantern.toml`, although the examples below already use that term.

## Getting started

Run:

```console
lantern init
lantern scan --format json
```

The scan command emits JSON. For more concepts see [concepts](docs/concepts.md), for commands see [recipes](docs/cookbook.md), and for every exact setting see [configuration](docs/reference.md#config-file).

## Configuration

The `cache_dir` setting defaults to `.lantern-cache`. `LANTERN_CACHE_DIR` overrides it. Schema version 3 is current.

## Recipes

To create a workspace run `lantern init`. To scan it run `lantern scan --format json`.
