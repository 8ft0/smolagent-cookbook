
from typing import Dict, Any

from exceptions import ValidationError, ItemNotFoundError
from validators import ShoppingListValidator


class ShoppingListClient:
    def __init__(self):
        self.shopping_lists = {}
        self.items = {
            101: {"sku": 101, "item_name": "Apple", "unit_price": 3.50},
            102: {"sku": 102, "item_name": "Bread", "unit_price": 5.00},
            103: {"sku": 103, "item_name": "Milk", "unit_price": 2.80},
            104: {"sku": 104, "item_name": "Eggs", "unit_price": 4.20},
            105: {"sku": 105, "item_name": "Chicken Breast", "unit_price": 8.50},
            106: {"sku": 106, "item_name": "Pasta", "unit_price": 3.00},
            107: {"sku": 107, "item_name": "Tomatoes", "unit_price": 2.50}
        }
        self.validator = ShoppingListValidator()
        
    @staticmethod
    def format_currency(value: float) -> str:
        """Format floating point numbers to 2 decimal places"""
        return f"{value:.2f}"

    def get_shopping_list(self, customer_id: int = 0) -> Dict[str, Any]:
        if not isinstance(customer_id, int) or customer_id < 0:
            raise ValidationError("Invalid customer ID")
            
        if customer_id not in self.shopping_lists:
            self.shopping_lists[customer_id] = {
                "list_id": customer_id,
                "items": []
            }
        return self.shopping_lists[customer_id]

    def get_item_info(self, sku: int) -> Dict[str, Any]:
        self.validator.validate_sku(sku)
        
        item = self.items.get(sku)
        if not item:
            raise ItemNotFoundError(f"Item with SKU {sku} not found")
            
        # Format unit price to 2 decimal places
        item['unit_price'] = float(self.format_currency(item['unit_price']))
        return item

    def update_list(self, sku: int, quantity: int, customer_id: int = 0, operation: str = "set") -> Dict[str, Any]:
        """Update shopping list with add/update/remove functionality
        
        Args:
            sku: Item SKU to update
            quantity: Quantity to add/remove/set
            customer_id: Customer ID (default: 0)
            operation: Type of operation - 'add', 'remove', or 'set' (default: 'set')
            
        Returns:
            Updated shopping list
            
        Raises:
            ValidationError: If inputs are invalid
            ItemNotFoundError: If item not found when required
        """
        # Validate inputs
        self.validator.validate_sku(sku)
        self.validator.validate_quantity(quantity)
        if operation not in ["add", "remove", "set"]:
            raise ValidationError("Operation must be 'add', 'remove', or 'set'")
            
        # Verify item exists
        if sku not in self.items:
            raise ItemNotFoundError(f"Item with SKU {sku} not found")
            
        shopping_list = self.get_shopping_list(customer_id)
        items = shopping_list['items']
        
        # Find existing item if present
        existing_item = next((item for item in items if item['sku'] == sku), None)
        
        if operation == "add":
            if not existing_item:
                # Add new item
                items.append({"sku": sku, "quantity": quantity})
            else:
                # Add to existing quantity
                new_quantity = existing_item['quantity'] + quantity
                self.validator.validate_quantity(new_quantity)
                existing_item['quantity'] = new_quantity
                
        elif operation == "remove":
            if not existing_item:
                raise ItemNotFoundError(f"Cannot remove - item with SKU {sku} not found in list")
            if quantity > existing_item['quantity']:
                raise ValidationError(f"Cannot remove {quantity} - only {existing_item['quantity']} available")
            new_quantity = existing_item['quantity'] - quantity
            if new_quantity > 0:
                existing_item['quantity'] = new_quantity
            else:
                items.remove(existing_item)
                
        elif operation == "set":
            if quantity > 0:
                if existing_item:
                    existing_item['quantity'] = quantity
                else:
                    items.append({"sku": sku, "quantity": quantity})
            else:
                if existing_item:
                    items.remove(existing_item)
                    
        return shopping_list
