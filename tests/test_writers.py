from src.writers.output_writer import OutputWriter


def test_writer_outputs_csv(tmp_path: object) -> None:
    """Ensure the output writer generates the CSV file."""
    output_path = tmp_path / "result.csv"
    records = [{"customer_id": "10", "order_id": "1", "barcodes": ["111", "112"]}]

    writer = OutputWriter()
    writer.write(records, str(output_path))

    content = output_path.read_text().splitlines()
    assert content[0] == "customer_id,order_id,barcodes"
    assert content[1] == "10,1,\"['111', '112']\""
