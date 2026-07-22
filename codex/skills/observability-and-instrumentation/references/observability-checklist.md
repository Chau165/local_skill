# Observability Checklist

Use this checklist when shipping or reviewing production-facing behavior.

## Questions First

- Write down the key operational questions this feature must answer.
- Make sure each log, metric, or trace exists to answer one of those questions.

## Logs

- Use stable event names and structured fields.
- Attach request or correlation identifiers.
- Avoid prose-heavy logs when machine-readable fields are possible.
- Never log secrets, tokens, passwords, or full PII.

## Metrics

- Add counters for success and failure paths.
- Add latency metrics for important operations.
- Keep metric labels low-cardinality.
- Prefer service-level metrics that support alerts and dashboards.

## Tracing

- Propagate context across HTTP calls, queues, and async boundaries.
- Add spans around meaningful internal units of work.
- Add attributes that help filter by actor, operation, or dependency.

## Verification

- Trigger a known success path and confirm it appears in telemetry.
- Trigger a controlled failure path and confirm the failure is diagnosable.
- Check dashboards or queries can answer the original operational questions.
