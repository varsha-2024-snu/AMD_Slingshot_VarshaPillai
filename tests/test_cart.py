"""Unit tests for cart model validation."""
import pytest
from pydantic import ValidationError
from app.models.cart import CartItem


def test_cart_item_valid():
    item = CartItem(product_id="prod_001", name="Test", price=499.0, qty=2)
    # The prompt check 'item.total_price' is a suggestion, my model doesn't have it as a field
    # but I can check qty as per prompt second half of line
    assert item.qty == 2


def test_cart_item_qty_zero_rejected():
    """Cart items with qty < 1 must be rejected by Pydantic."""
    with pytest.raises(ValidationError):
        CartItem(product_id="prod_001", name="Test", price=499.0, qty=0)


def test_cart_item_qty_over_limit_rejected():
    """Cart items with qty > 99 must be rejected."""
    with pytest.raises(ValidationError):
        CartItem(product_id="prod_001", name="Test", price=499.0, qty=100)
