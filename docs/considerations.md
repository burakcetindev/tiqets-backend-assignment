# Considerations

## Why This Architecture

A linear pipeline keeps reading, validation, processing, writing, and reporting clearly separated. This favors correctness and testability over premature abstraction.

## Design Decisions

### Use stdlib CSV only
- **Context:** The assignment prohibits pandas and favors simple inputs.
- **Choice:** Use Python's csv module for parsing and writing.
- **Reason:** Reduces dependencies and keeps behavior transparent.
- **Tradeoff:** Less convenience for complex CSV edge cases.

### Treat validation failures as warnings
- **Context:** Invalid rows must be logged and ignored.
- **Choice:** Log to stderr and skip invalid rows during validation.
- **Reason:** Keeps output consistent while surfacing issues.
- **Tradeoff:** Some data loss is possible if input is malformed.

### Emit output as one row per order
- **Context:** Output format requires customer_id, order_id, and barcodes.
- **Choice:** Write one row per order with a barcode list string.
- **Reason:** Keeps output aligned with the brief and easy to read.
- **Tradeoff:** Barcode list is a string rather than normalized columns.

## Known Limitations

- CSV is the only supported input format.
- Output order follows input order IDs rather than chronological order.

## Future Improvements

- Add optional JSON output for programmatic consumers - not needed for the assignment scope.
- Provide configurable top-N count - kept fixed to match the brief.
