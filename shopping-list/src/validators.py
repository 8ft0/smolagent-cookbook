from typing import Dict, Any
from decimal import Decimal

from exceptions import InvalidSkuError, InvalidQuantityError, ValidationError


class ShoppingListValidator:
    """Validator for shopping list operations"""
    
    @staticmethod
    def validate_customer_id(customer_id: str) -> None:
        try:
            customer_id_int = int(customer_id)
            if customer_id_int < 0:
                raise ValidationError("Customer ID must be a positive integer")
        except ValueError:
            raise ValidationError("Customer ID must be a valid integer")
            
    @staticmethod
    def validate_operation(operation: str) -> None:
        valid_operations = {'add', 'remove', 'set'}
        if operation not in valid_operations:
            raise ValidationError(f"Operation must be one of: {valid_operations}")
    
    @staticmethod
    def validate_sku(sku: int) -> None:
        if not isinstance(sku, int) or sku <= 0:
            raise InvalidSkuError("SKU must be a positive integer")
            
    @staticmethod
    def validate_quantity(quantity: int) -> None:
        if not isinstance(quantity, int):
            raise InvalidQuantityError("Quantity must be an integer")
        if quantity < 0:
            raise InvalidQuantityError("Quantity cannot be negative")
            
    @staticmethod
    def validate_price(price: float) -> None:
        try:
            price_decimal = Decimal(str(price))
            if price_decimal < 0:
                raise ValidationError("Price cannot be negative")
        except (TypeError, ValueError):
            raise ValidationError("Invalid price format")

    @staticmethod
    def validate_item_details(item: Dict[str, Any]) -> None:
        required_fields = {'sku', 'item_name', 'unit_price'}
        missing_fields = required_fields - set(item.keys())
        if missing_fields:
            raise ValidationError(f"Missing required fields: {missing_fields}")
            
        ShoppingListValidator.validate_sku(item['sku'])
        ShoppingListValidator.validate_price(item['unit_price'])
        if not isinstance(item['item_name'], str) or not item['item_name'].strip():
            raise ValidationError("Item name must be a non-empty string")
