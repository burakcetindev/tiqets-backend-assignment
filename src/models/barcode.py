from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Barcode:
    """Represents a validated barcode, sold or unused."""

    barcode: str
    order_id: Optional[str]
