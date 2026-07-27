# Public architecture and contracts

`boundary.py` supports both command-line and HTTP entry points.

- `validate_import` is application validation used by both entry points. Its returned strings are stable public outputs. Its internal representation is not public.
- `parse_cli_filter` is the command-line adapter. `CustomerFilter` is a core filtering type and must remain the returned public type. The option spellings are transport syntax.
- `SourcePriority` and `TargetPriority` belong to separate models with independent owners. They do not share a generated schema.
- `Batch.status()` is a stable public API returning a list. In the current lifecycle, an empty list can describe either a new batch or a completed batch with no errors. This task does not authorize a new return type, method, or externally visible state.
- `FrameworkField` is a business object constructed from an adapter-owned descriptor. Only the external business name is needed after construction; widget metadata belongs to the adapter. `business_name()` is the stable public API.
- The exact text returned by `audit_phrase` is a regulated audit contract.
- `display_line` is adapter-local rendering. Its line number has no independent validation rules or domain lifecycle.

Preserve every stated public type, output, exception, and callable signature.
