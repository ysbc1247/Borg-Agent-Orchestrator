# Forecaster Evaluation and Interpretation

Date: 2026-03-19

## Scope

This report records the evaluated forecasting baseline results and the interpretation findings produced during the Borg trace experiments.

## Primary Baseline Profile

Default profile: `base`

Validation results:

- Validation rows: `4,810,777`
- Validation positives: `1,448`
- Validation positive rate: `0.0301%`
- Average precision: `0.0074076`
- Precision@0.1%: `0.0122661`
- Recall@0.1%: `0.0407459`
- Precision@1%: `0.0070676`
- Recall@1%: `0.2348066`

## Alternate Rolling Profile

Alternate profile: `base_plus_roll`

Validation results:

- Validation rows: `4,810,777`
- Validation positives: `1,448`
- Validation positive rate: `0.0301%`
- Average precision: `0.0071694`
- Precision@0.1%: `0.0222453`
- Recall@0.1%: `0.0738950`
- Precision@1%: `0.0069013`
- Recall@1%: `0.2292818`

Interpretation:

- `base` remained the best default profile for overall ranking quality.
- `base_plus_roll` improved the extreme top-risk alert slice.
- Full temporal feature expansion reduced overall average precision and was not kept as the default.

## Cluster-Level Interpretation

Per-cluster behavior was uneven and should not be hidden behind the aggregate score.

- Cluster `b`: relatively strong ranking performance
- Cluster `c`: relatively strong ranking performance
- Cluster `d`: mixed performance
- Cluster `e`: no positive validation examples in the evaluated split
- Cluster `f`: weak performance
- Cluster `g`: weak performance

Interpretation:

- The baseline does not generalize uniformly across clusters.
- Future comparisons should continue to include per-cluster metrics.
- Aggregate metrics alone are insufficient for deciding model quality.

## Feature Interpretation

The strongest feature weights in the baseline were concentrated in scheduling and resource-usage signals.

Highest-ranked signals observed in the exported feature ranking:

- `scheduling_class`
- `avg_mem`
- `max_mem`
- `avg_mem_utilization`
- `max_mem_utilization`
- `max_cpu_utilization`
- `max_cpu`
- `avg_cpu_utilization`
- `avg_cpu`

Interpretation:

- Memory level and memory utilization signals were especially important in the baseline separation.
- CPU utilization and CPU level signals were also important.
- `req_cpu`, `req_mem`, and especially `event_count` were weaker than direct resource-usage signals in this baseline.

## Main Conclusion

- The current `base` profile is the strongest default baseline.
- The `base_plus_roll` profile is useful for top-alert triage scenarios.
- The next improvement should come from a stronger model class rather than adding more unfiltered temporal features to the current linear risk-score baseline.
