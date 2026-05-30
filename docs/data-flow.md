# Data Flow

## Voucher Pipeline

### Flow Description

The user invokes the CLI with orders and barcodes CSV paths. The pipeline loads raw rows, validates duplicates and missing barcodes, aggregates barcodes per order, writes the output CSV, and prints summary metrics.
Validation rules are enforced before aggregation so invalid rows never reach the processor or writer.

### Step-by-Step Behavior

1. CLI reads orders.csv and barcodes.csv via readers.
2. Validator normalizes rows, logs invalid items, and filters orders without barcodes.
3. Processor groups barcodes by order and produces output rows.
4. Writer persists the output CSV to disk.
5. Reporter prints top customers and unused barcodes to stdout.

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant CLI as CLI
    participant R as Readers
    participant V as Validator
    participant P as Processor
    participant W as Writer
    participant Rep as Reporter

    U->>CLI: run main.py --orders --barcodes --output
    CLI->>R: read orders.csv
    CLI->>R: read barcodes.csv
    R-->>CLI: raw rows
    CLI->>V: validate rows
    V-->>CLI: valid orders + barcodes
    CLI->>P: build output rows
    P-->>CLI: order rows
    CLI->>W: write output CSV
    CLI->>Rep: print summaries
    Rep-->>U: stdout
```

## Error Flow

### Error Handling Description

- Validation errors (duplicate barcodes, missing barcodes, malformed rows) are logged to stderr and ignored.
- Orders without barcodes are logged and excluded from the output.
- IO errors bubble up to the CLI so failures are explicit.

```mermaid
sequenceDiagram
    participant CLI as CLI
    participant V as Validator

    CLI->>V: validate row
    V->>V: detect validation failure
    V-->>CLI: log warning to stderr
```

### Error Response Contract

- Validation error example: "WARNING: Duplicate barcode ignored: 12345"
- Missing barcode example: "WARNING: Order has no barcodes and was ignored: 10"
