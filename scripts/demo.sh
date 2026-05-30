#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." >/dev/null 2>&1 && pwd)"
cd "$ROOT_DIR"

# ══════════════════════════════════════════════════════════════
# COLORS & UTILITIES
# ══════════════════════════════════════════════════════════════
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
LIGHT_BLUE='\033[1;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

status_ok() { printf '%b%s%b\n' "$GREEN" "$1" "$NC"; }
status_warn() { printf '%b%s%b\n' "$YELLOW" "$1" "$NC"; }
status_err() { printf '%b%s%b\n' "$RED" "$1" "$NC"; }
section_header() { printf '%b%s%b\n' "$BOLD$CYAN" "$1" "$NC"; }

pause() {
  printf '\n%bPress any key to return to menu...%b\n' "$DIM" "$NC"
  read -r -n 1 -s || true
}

# ══════════════════════════════════════════════════════════════
# VENV SETUP
# ══════════════════════════════════════════════════════════════
setup_venv() {
  if [[ ! -d .venv ]]; then
    printf '%b%s%b\n' "$CYAN" "Setting up Python virtual environment..." "$NC"
    python3 -m venv .venv
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pip install -r requirements.txt -q
}

# ══════════════════════════════════════════════════════════════
# MENU FUNCTIONS
# ══════════════════════════════════════════════════════════════

show_menu() {
  clear

  printf '%b' "$PURPLE"
  printf '╔════════════════════════════════════════════╗\n'
  printf '║%b  TIQETS VOUCHER PIPELINE — DEMO            %b║\n' "$BOLD" "$NC$PURPLE"
  printf '╠════════════════════════════════════════════╣\n'

  printf '║  %b1)%b %bRun full pipeline (default data)       %b║\n' "$YELLOW" "$PURPLE" "$LIGHT_BLUE" "$PURPLE"
  printf '║  %b2)%b %bRun test suite                         %b║\n' "$YELLOW" "$PURPLE" "$LIGHT_BLUE" "$PURPLE"
  printf '║  %b3)%b %bShow input data                        %b║\n' "$YELLOW" "$PURPLE" "$LIGHT_BLUE" "$PURPLE"
  printf '║  %b4)%b %bShow output CSV                        %b║\n' "$YELLOW" "$PURPLE" "$LIGHT_BLUE" "$PURPLE"
  printf '║  %b5)%b %bTop 5 customers                        %b║\n' "$YELLOW" "$PURPLE" "$LIGHT_BLUE" "$PURPLE"
  printf '║  %b6)%b %bUnused barcodes count                  %b║\n' "$YELLOW" "$PURPLE" "$LIGHT_BLUE" "$PURPLE"
  printf '║  %b7)%b %bValidation demo (bad data)             %b║\n' "$YELLOW" "$PURPLE" "$LIGHT_BLUE" "$PURPLE"
  printf '║  %b8)%b %bRun with custom input files            %b║\n' "$YELLOW" "$PURPLE" "$LIGHT_BLUE" "$PURPLE"
  printf '║  %b9)%b %bShow SQL schema                        %b║\n' "$YELLOW" "$PURPLE" "$LIGHT_BLUE" "$PURPLE"
  printf '║  %b0)%b %bQuit                                   %b║\n' "$YELLOW" "$PURPLE" "$LIGHT_BLUE" "$PURPLE"

  printf '╚════════════════════════════════════════════╝\n'
  printf '%b' "$NC"

  printf '\nChoice [0-9]: '
}

run_full_pipeline() {
  clear
  section_header "Running Full Pipeline (Default Data)"
  mkdir -p output
  python main.py --orders assignment/data/orders.csv --barcodes assignment/data/barcodes.csv --output output/result.csv 2>"${ROOT_DIR}/.tmp_stderr.txt" >"${ROOT_DIR}/.tmp_stdout.txt"
  
  status_ok "✓ Output written to: output/result.csv"
  
  if [[ -s "${ROOT_DIR}/.tmp_stderr.txt" ]]; then
    printf '\n%bValidation Warnings:%b\n' "$YELLOW" "$NC"
    cat "${ROOT_DIR}/.tmp_stderr.txt" | sed "s/^/  /"
  fi
  
  printf '\n%bPipeline Output (Top Customers + Unused Count):%b\n' "$GREEN" "$NC"
  cat "${ROOT_DIR}/.tmp_stdout.txt" | sed "s/^/  /"
  
  printf '\n%bPreview (First 10 Rows):%b\n' "$GREEN" "$NC"
  head -11 output/result.csv | sed "s/^/  /"
  
  rm -f "${ROOT_DIR}/.tmp_stderr.txt" "${ROOT_DIR}/.tmp_stdout.txt"
  pause
}

run_tests() {
  clear
  section_header "Running Test Suite"
  python -m pytest tests/ -v --tb=short
  pause
}

show_input_data() {
  clear
  section_header "Input Data Summary"
  
  printf '%bOrders (%b\n' "$CYAN" "$NC"
  printf 'Rows: %d\n\n' $(($(wc -l < assignment/data/orders.csv) - 1))
  head -5 assignment/data/orders.csv | sed "s/^/  /"
  printf '  ...\n\n'
  
  printf '%bBarcodes (%b\n' "$CYAN" "$NC"
  total_barcodes=$(($(wc -l < assignment/data/barcodes.csv) - 1))
  sold=$(grep -c '^[^,]*,[0-9]' assignment/data/barcodes.csv || true)
  unsold=$((total_barcodes - sold))
  printf 'Total: %d | Sold: %d | Unsold: %d\n\n' "$total_barcodes" "$sold" "$unsold"
  head -5 assignment/data/barcodes.csv | sed "s/^/  /"
  printf '  ...\n'
  
  pause
}

show_output_csv() {
  clear
  section_header "Output CSV"
  
  if [[ ! -f output/result.csv ]]; then
    status_warn "⚠ output/result.csv not found"
    printf '\nWould you like to run the pipeline first? (run option 1 from menu)\n'
    pause
    return
  fi
  
  line_count=$(wc -l < output/result.csv)
  printf '%bContents (total rows: %d):%b\n\n' "$GREEN" "$((line_count - 1))" "$NC"
  cat -n output/result.csv | sed "s/^/  /"
  pause
}

top_customers() {
  clear
  section_header "Top 5 Customers"

  python main.py --orders assignment/data/orders.csv --barcodes assignment/data/barcodes.csv --output /tmp/tiqets_temp.csv 2>/dev/null >/tmp/tiqets_output.txt || true

  printf '%bTop Customers by Ticket Count:%b\n\n' "$GREEN" "$NC"
  printf '  ┌─────────────┬────────────────┐\n'
  printf '  │ Customer ID │ Ticket Count   │\n'
  printf '  ├─────────────┼────────────────┤\n'

  head -5 /tmp/tiqets_output.txt | while read -r line; do
    cid=$(echo "$line" | awk '{print $1}' | tr -d ',')
    count=$(echo "$line" | awk '{print $2}' | tr -d ',')
    printf '  │ %-11s │ %-14s │\n' "$cid" "$count"
  done
  
  printf '  └─────────────┴────────────────┘\n'

  rm -f /tmp/tiqets_temp.csv /tmp/tiqets_output.txt
  pause
}

unused_barcodes() {
  clear
  section_header "Unused Barcodes"
  
  python main.py --orders assignment/data/orders.csv --barcodes assignment/data/barcodes.csv --output /tmp/tiqets_temp.csv 2>/dev/null >/tmp/tiqets_output.txt || true
  
  unused=$(grep "Unused barcodes:" /tmp/tiqets_output.txt | tail -1)
  
  printf '%bBreakdown:%b\n' "$GREEN" "$NC"
  total_barcodes=$(($(wc -l < assignment/data/barcodes.csv) - 1))
  sold=$(grep -c '^[^,]*,[0-9]' assignment/data/barcodes.csv || true)
  unsold=$((total_barcodes - sold))
  
  printf '  Total barcodes in file:  %d\n' "$total_barcodes"
  printf '  Sold (assigned to orders): %d\n' "$sold"
  printf '  Unsold (no order):        %d\n\n' "$unsold"
  
  printf '%bPipeline Result:%b\n' "$GREEN" "$NC"
  echo "  $unused" | sed 's/^/  /'
  
  rm -f /tmp/tiqets_temp.csv /tmp/tiqets_output.txt
  pause
}

validation_demo() {
  clear
  section_header "Validation Demo (Bad Data)"
  
  printf '%bRunning against edge case fixtures with duplicates and missing data...\n\n' "$YELLOW" "$NC"
  
  python main.py --orders tests/fixtures/orders_edge.csv --barcodes tests/fixtures/barcodes_edge.csv --output /tmp/tiqets_edge.csv 2>"${ROOT_DIR}/.tmp_err.txt" >/tmp/tiqets_out.txt || true
  
  printf '%bValidation Warnings Caught:%b\n' "$YELLOW" "$NC"
  cat "${ROOT_DIR}/.tmp_err.txt" | sed "s/^/  /"
  
  printf '\n%bClean Output (after filtering):%b\n' "$GREEN" "$NC"
  cat /tmp/tiqets_out.txt | sed "s/^/  /"
  
  printf '\n%bWhat Was Rejected:%b\n' "$CYAN" "$NC"
  printf '  • Duplicate barcodes (same barcode in multiple orders)\n'
  printf '  • Orders with no barcodes assigned\n'
  printf '  • Invalid/malformed rows\n'
  printf '\n%bResult:%b Valid orders and barcodes appear in output; invalid items are logged above.\n' "$GREEN" "$NC"
  
  rm -f "${ROOT_DIR}/.tmp_err.txt" /tmp/tiqets_edge.csv /tmp/tiqets_out.txt
  pause
}

custom_input() {
  clear
  section_header "Run with Custom Input Files"
  
  printf 'Enter path to orders CSV (or press Enter for assignment/data/orders.csv): '
  read -r orders_path
  orders_path="${orders_path:-assignment/data/orders.csv}"
  
  printf 'Enter path to barcodes CSV (or press Enter for assignment/data/barcodes.csv): '
  read -r barcodes_path
  barcodes_path="${barcodes_path:-assignment/data/barcodes.csv}"
  
  printf 'Enter output path (or press Enter for output/custom_result.csv): '
  read -r output_path
  output_path="${output_path:-output/custom_result.csv}"
  
  mkdir -p "$(dirname "$output_path")"
  
  clear
  section_header "Running Pipeline with Custom Input"
  printf "Orders: %s\n" "$orders_path"
  printf "Barcodes: %s\n" "$barcodes_path"
  printf "Output: %s\n\n" "$output_path"
  
  python main.py --orders "$orders_path" --barcodes "$barcodes_path" --output "$output_path" 2>"${ROOT_DIR}/.tmp_err.txt" >/tmp/tiqets_custom.txt || true
  
  if [[ -s "${ROOT_DIR}/.tmp_err.txt" ]]; then
    printf '%bValidation Warnings:%b\n' "$YELLOW" "$NC"
    cat "${ROOT_DIR}/.tmp_err.txt" | sed "s/^/  /"
    printf '\n'
  fi
  
  printf '%bPipeline Output:%b\n' "$GREEN" "$NC"
  cat /tmp/tiqets_custom.txt | sed "s/^/  /"
  
  if [[ -f "$output_path" ]]; then
    printf '\n%bOutput Preview:%b\n' "$GREEN" "$NC"
    head -6 "$output_path" | sed "s/^/  /"
  fi
  
  rm -f "${ROOT_DIR}/.tmp_err.txt" /tmp/tiqets_custom.txt
  pause
}

show_sql_schema() {
  clear
  section_header "SQL Database Schema"
  
  if [[ ! -f sql/schema.sql ]]; then
    status_err "✗ sql/schema.sql not found"
    pause
    return
  fi
  
  printf '%bSchema Definition:%b\n\n' "$GREEN" "$NC"
  cat sql/schema.sql | sed "s/^/  /"
  
  printf '\n%bExplanation:%b\n' "$CYAN" "$NC"
  cat <<'EOF' | sed "s/^/  /"
TABLES & RELATIONSHIPS:

1. customers
   - customer_id: Primary key identifying unique customers

2. orders
   - order_id: Primary key identifying unique orders
   - customer_id: Foreign key linking to customers table
   - Index on customer_id for efficient lookups

3. barcodes
   - barcode: Primary key identifying unique barcode strings
   - order_id: Foreign key linking to orders (NULLABLE)
   - Nullable order_id allows tracking unsold/unassigned barcodes
   - Index on order_id for efficient lookups

DESIGN DECISIONS:

- Nullable order_id on barcodes enables tracking inventory
- Indexes on foreign keys optimize join queries
- Simple flat schema avoids complexity
EOF
  
  pause
}

# ══════════════════════════════════════════════════════════════
# MAIN LOOP
# ══════════════════════════════════════════════════════════════
main() {
  while true; do
    show_menu
    read -r choice
    case "$choice" in
      1) run_full_pipeline ;;
      2) run_tests ;;
      3) show_input_data ;;
      4) show_output_csv ;;
      5) top_customers ;;
      6) unused_barcodes ;;
      7) validation_demo ;;
      8) custom_input ;;
      9) show_sql_schema ;;
      0)
        clear
        status_ok "Goodbye!"
        return 0
        ;;
      *)
        status_warn "Invalid choice. Please select 0-9."
        sleep 1
        ;;
    esac
  done
}

# ══════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════
setup_venv
main
