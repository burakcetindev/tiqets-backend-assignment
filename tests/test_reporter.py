from src.reporter.reporter import Reporter


def test_reporter_top_customers(capsys: object) -> None:
    """Ensure the reporter prints customer counts."""
    top_customers = [("10", 3), ("11", 1)]

    reporter = Reporter()
    reporter.print_top_customers(top_customers)

    captured = capsys.readouterr()
    assert "10, 3" in captured.out
    assert "11, 1" in captured.out


def test_reporter_prints_stdout(capsys: object) -> None:
    """Ensure the reporter prints summaries to stdout."""
    reporter = Reporter()
    reporter.print_top_customers([("10", 1)])
    reporter.print_unused_barcodes(2)

    captured = capsys.readouterr()
    assert "10, 1" in captured.out
    assert "Unused barcodes: 2" in captured.out
