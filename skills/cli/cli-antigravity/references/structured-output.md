# Antigravity structured output (`--json-schema`)

Read this before passing `--json-schema` or relying on `structured_output`. The checks
below used agy 1.4.0 on macOS on 2026-10-16 with `gemini-3.8-flash-high`.

## What the schema is

The schema is sent to Gemini as the parameters of a function declaration, so Gemini's
own schema limits apply and the API, not the CLI, rejects an unacceptable one. With
`--output-format stream-json` the schema applies to the final result only.

## A rejected schema

A `null` inside an `enum`, for example `{"type":["string","null"],"enum":[null,"a","b"]}`,
is rejected:

- exit status 3 and a terminal `result` with `status: "ERROR"`;
- empty `response`, no `structured_output`, zero usage;
- it fails within seconds, before any inference;
- the `error` text names the offending path:

```text
INVALID_ARGUMENT (code 400): * GenerateContentRequest.tools[13].function_declarations[0].parameters.properties[code].enum[0]: cannot be empty
```

This is an invalid request, not quota, authentication or network trouble, and retrying
cannot help: fix the schema. It differs from an invalid or contradictory `--model` and
`--effort` pair, which the CLI rejects itself with exit status 1 and an empty
`conversation_id`.

Accepted in the same checks: type lists containing `"null"`, `maxLength`,
`additionalProperties: false`, `required`, and string enums without `null`. Other keywords
(`$ref`, `pattern`, `oneOf` and so on) were not tested; probe rather than assume.

## Nullable fields

Gemini does not read "nullable and required" as "may be null". With the null removed from
an enum but the field still required, a success probe returned a registered error code in
`error_code`; required nullable strings came back as `""` instead of `null`. A caller's
strict validator would then reject a good result.

Make nullable fields optional instead: drop them from `required`, keep `null` out of
enums, and tell the model to omit what does not apply. Read an omitted field, `null` and
`""` as absent. Keep validating contradictions (a successful report that names an error)
and fail closed rather than quietly cleaning them. Checked: with optional nullable fields a
success report omitted the error fields, and a failure report supplied the correct code and
message.

## Reading the result

A successful schema run returns `conversation_id`, `duration_seconds`, `json_schema` (an
echo of the schema), `num_turns`, `response`, `status`, `structured_output` and `usage`
(`input_tokens`, `output_tokens`, `thinking_tokens`, `cache_read_tokens`, `total_tokens`).

`structured_output` is the deliverable. `response` is independent prose: in a real research
run it was 14,177 characters of narrative with no headings, while
`structured_output.summary` was a separate 5,969-character report with no verbatim overlap.
Do not parse the report out of `response` when a schema was supplied, and do not assume one
summarises the other. Treat `SUCCESS` without a valid `structured_output` as incomplete.
For the resumed-conversation inconsistency, see [follow-up.md](follow-up.md).

## Probe a schema before relying on it

After any schema change, send one tiny request from a temporary directory. A rejection
arrives within seconds. If the schema has conditional fields, probe a success-shaped and a
failure-shaped prompt.

```sh
printf '%s\n' '{"event":"user","message":{"content":"Use no tools. Reply with the JSON object."}}' |
  agy --input-format stream-json --output-format stream-json --model "$model_slug" \
      --print-timeout 2m --json-schema "$schema_json" --sandbox
```

Check the exit status and the `event: "result"` line: `status: "SUCCESS"` and a
`structured_output` that passes your own validator. Unit tests with a fake CLI cannot show
that Gemini accepts a schema, so a job that has not run for days is not evidence that its
schema still works.

## Sources and limits

[Official headless guide](https://antigravity.google/docs/cli/headless/) and the installed
`agy --help`. The observations come from a Scheduled Jobs schema that failed every
Antigravity run from 14 October 2026 (a `null` in an `error_code` enum) and from probing the
CLI with schema variants. One model was used, and other models or keywords may behave
differently.
