"""Order domain model used by the pipeline.

Contains the immutable `Order` dataclass with identifiers parsed from CSV.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    """Represents a validated order from the dataset."""

    order_id: str
    customer_id: str
