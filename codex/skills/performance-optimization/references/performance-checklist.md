# Performance Checklist

Use this checklist after profiling and before closing performance work.

## Measure First

- Capture a baseline before changes.
- Record the user-visible symptom and the metric that represents it.
- Confirm the bottleneck with traces, profiling, or query timing instead of guessing.

## Frontend

- Check LCP, INP, and CLS if the issue is page load or interaction latency.
- Verify large images have explicit dimensions and appropriate loading priority.
- Check for render-blocking CSS or JavaScript.
- Look for unnecessary re-renders, long tasks, and layout thrashing.
- Confirm data fetching does not create client-side waterfalls.

## Backend

- Check endpoint latency percentiles, not just averages.
- Inspect slow queries, missing indexes, and N+1 access patterns.
- Confirm pagination or limits exist for list endpoints.
- Look for repeated external calls that should be cached or batched.
- Check CPU, memory, queue depth, and connection pool pressure when relevant.

## Verify

- Measure again after the fix using the same method as the baseline.
- Confirm the change improved the target metric and did not regress correctness.
- Add a guardrail when needed: alert, benchmark, regression test, or dashboard.
