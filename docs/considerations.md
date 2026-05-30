# Considerations

Purpose: Record the main design decisions, constraints, limitations, and likely future improvements.

## Why This Architecture

The pipeline is intentionally linear: readers load rows, validators clean and log issues, the processor aggregates by order, the writer persists output, and the reporter prints summaries. This keeps responsibilities separated and makes failures explicit.

## Design Decisions

### Use stdlib CSV only
- **Context:** The assignment favors a simple, dependency-light solution.
- **Choice:** Use Python's built-in csv module for reading and writing.
- **Reason:** Transparent behavior, fewer dependencies, and easy inspection.
- **Tradeoff:** Less convenience for advanced CSV quirks.

### Validate early and log warnings
- **Context:** Invalid rows must be ignored and logged.
- **Choice:** Validation filters invalid rows and logs warnings to stderr.
- **Reason:** Keeps output deterministic while exposing data issues.
- **Tradeoff:** Some data is dropped when malformed.

### Emit one row per order
- **Context:** Output format requires customer_id, order_id, and barcode list.
- **Choice:** Write one row per order with a list-formatted barcode string.
- **Reason:** Matches the brief and keeps output human-readable.
- **Tradeoff:** The barcode list is not normalized into separate columns.

### Keep top-5 fixed in both CLI and demo
- **Context:** The brief explicitly asks for the top 5 customers.
- **Choice:** The CLI and demo both show the top 5 summary only.
- **Reason:** Matches the assignment exactly and avoids ambiguity in review.
- **Tradeoff:** Reviewers cannot request an arbitrary N from the demo.

### Preserve original datasets
- **Context:** The assignment data must remain unchanged.
- **Choice:** Keep immutable files in assignment/data and mirror them in data.
- **Reason:** Ensures a stable baseline while allowing local experiments.
- **Tradeoff:** Duplicate files are required for clarity.

## Known Limitations

- CSV is the only supported input format.
- Output order follows the input order list rather than timestamp sorting.
- The CLI and demo both intentionally keep the top-N value fixed at 5.

## Future Improvements

- Add optional JSON output for programmatic consumers.
- Stream processing for larger datasets to reduce memory usage.
