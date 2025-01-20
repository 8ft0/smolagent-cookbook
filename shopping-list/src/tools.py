from typing import Dict, Any, Optional
from exceptions import ShoppingListError, ValidationError, ItemNotFoundError
import logging
import jmespath
from smolagents import Tool
from client import ShoppingListClient
from validators import ShoppingListValidator


logger = logging.getLogger(__name__)

shopping_list_client = ShoppingListClient()
validator = ShoppingListValidator()


class GetShoppingListTool(Tool):
    name = "get_shopping_list"
    description = """
    Retrieves the shopping list for a given customer.
    
    Args:
        customer_id (str): The unique identifier of the customer.
        
    Returns:
        A dictionary containing the shopping list details:
        - list_id: The unique identifier of the shopping list. (type: int)
        - items: A list of items in the shopping list, where each item contains:
            - sku: The unique identifier of the item. (type: int)
            - quantity: The quantity of the item. (type: int)
        
    Raises:
        ValidationError: If customer_id is invalid
    """
    
    inputs = {
        "customer_id": {
            "type": "integer",
            "description": "The unique identifier of the customer (default: 0).",
            "default": 0
        }
    }
    output_type = "object"
    
    EXTRACT_QUERY = '{list_id: list_id, items: items}'
    
    def forward(self, customer_id: str) -> Dict[str, Any]:
        try:
            validator.validate_customer_id(customer_id)
            shopping_list = shopping_list_client.get_shopping_list(
                customer_id=int(customer_id)
            )
            
            extract = _extract(shopping_list, self.EXTRACT_QUERY)
            logger.info("Retrieved shopping list: %s", extract)
            return extract or {}
            
        except ValueError:
            raise ValidationError("Customer ID must be a valid integer")
        except ShoppingListError as e:
            logger.error("Shopping list error: %s", str(e))
            return {"error": str(e), "error_code": e.error_code}
        except Exception as e:
            logger.error("Unexpected error: %s", str(e))
            return {"error": "An unexpected error occurred"}


class GetItemDetailsTool(Tool):
    name = "get_item_details"
    description = """
    Retrieves detailed information about a specific item.
    
    Args:
        sku (str): The unique identifier of the item (optional if item_name provided)
        item_name (str): The name of the item to search for (optional if sku provided)
        
    Returns:
        A dictionary containing the item details:
        - sku: The unique identifier of the item. (type: int)
        - item_name: The name of the item. (type: str)
        - unit_price: The price of one unit of the item. (type: float)
        
    Raises:
        ValidationError: If neither sku nor item_name is provided or if they are invalid
        ItemNotFoundError: If the item cannot be found
    """
    
    inputs = {
        "sku": {
            "type": "string",
            "description": "The unique identifier of the item.",
            "nullable": True
        },
        "item_name": {
            "type": "string",
            "description": "The name of the item to search for.",
            "nullable": True
        }
    }
    output_type = "object"
    
    EXTRACT_QUERY = '{sku: sku, item_name: item_name, unit_price: unit_price}'
    
    def forward(self, sku: str = None, item_name: str = None) -> Dict[str, Any]:
        try:
            if not sku and not item_name:
                raise ValidationError("Either sku or item_name must be provided")
                
            if sku:
                validator.validate_sku(sku)
                item_info = shopping_list_client.get_item_info(sku=int(sku))
            else:
                if not isinstance(item_name, str) or not item_name.strip():
                    raise ValidationError("Item name must be a non-empty string")
                    
                # Search items by name (case-insensitive)
                all_items = shopping_list_client.items.values()
                item_info = next(
                    (item for item in all_items
                     if item['item_name'].lower() == item_name.lower()),
                    None
                )
                if not item_info:
                    raise ItemNotFoundError(f"Item '{item_name}' not found")
                    
            extract = _extract(item_info, self.EXTRACT_QUERY)
            logger.info("Retrieved item details: %s", extract)
            return extract or {}
            
        except ShoppingListError as e:
            logger.error("Shopping list error: %s", str(e))
            return {"error": str(e), "error_code": e.error_code}
        except Exception as e:
            logger.error("Unexpected error: %s", str(e))
            return {"error": "An unexpected error occurred"}


class UpdateListTool(Tool):
    name = "update_list"
    description = """
    Updates items in the shopping list with options to add, remove, or modify quantities.
    
    Args:
        sku (int): The item's unique identifier
        quantity (int): The quantity to set, add, or remove
        customer_id (int): Optional customer identifier (default: 0)
        operation (str): Type of operation - 'add', 'remove', or 'set' (default: 'set')
        
    Returns:
        The updated shopping list with status and item details

            {
                "status": "success",
                "message": "Shopping list updated",
                "list": updated_list,
                "item": next(
                    (item for item in updated_list.get('items', []) 
                     if item['sku'] == sku), 
                    None
                )
            }
        
    Raises:
        ValidationError: If inputs are invalid
        ItemNotFoundError: If the item cannot be found
    """
    
    inputs = {
        "sku": {"type": "integer", "description": "The item's unique identifier"},
        "quantity": {"type": "integer", "description": "The quantity to set, add, or remove"},
        "customer_id": {
            "type": "integer",
            "description": "Optional customer identifier",
            "nullable": True,
            "default": 0
        },
        "operation": {
            "type": "string",
            "description": "Type of operation - 'add', 'remove', or 'set'",
            "enum": ["add", "remove", "set"],
            "default": "set",
            "nullable": True
        }
    }
    output_type = "object"
    
    def forward(self, sku: int, quantity: int, customer_id: int = 0, operation: str = "set") -> Dict[str, Any]:
        try:
            # Validate inputs
            validator.validate_quantity(quantity)
            validator.validate_operation(operation)
                
            # Get current list to check item existence
            current_list = shopping_list_client.get_shopping_list(customer_id=customer_id)
            item_exists = any(item['sku'] == sku for item in current_list.get('items', []))
            
            # Handle different operations
            if operation == "add":
                if not item_exists:
                    logger.info(f"Adding new item with SKU {sku}")
                else:
                    logger.info(f"Adding {quantity} to existing item with SKU {sku}")
                    
            elif operation == "remove":
                if not item_exists:
                    raise ItemNotFoundError(f"Item with SKU {sku} not found in list")
                if quantity <= 0:
                    raise ValidationError("Quantity must be positive for removal")
                logger.info(f"Removing {quantity} from item with SKU {sku}")
                
            elif operation == "set":
                if quantity == 0:
                    logger.info(f"Removing item with SKU {sku} from list")
                else:
                    logger.info(f"Setting quantity of item with SKU {sku} to {quantity}")
            
            # Perform the update
            updated_list = shopping_list_client.update_list(
                sku=sku,
                quantity=quantity,
                customer_id=customer_id,
                operation=operation
            )
            
            # Log and return results
            logger.info("Successfully updated shopping list")
            return {
                "status": "success",
                "message": "Shopping list updated",
                "list": updated_list,
                "item": next(
                    (item for item in updated_list.get('items', []) 
                     if item['sku'] == sku), 
                    None
                )
            }
            
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return {"error": str(e), "error_code": "VALIDATION_ERROR"}
        except ItemNotFoundError as e:
            logger.error(f"Item not found: {str(e)}")
            return {"error": str(e), "error_code": "ITEM_NOT_FOUND"}
        except ShoppingListError as e:
            logger.error(f"Shopping list error: {str(e)}")
            return {"error": str(e), "error_code": e.error_code}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {"error": "An unexpected error occurred", "error_code": "UNKNOWN_ERROR"}


def _extract(response: Dict[str, Any], query: str) -> Optional[Dict[str, Any]]:
    try:
        result = jmespath.search(query, response)
        msg = "Extracted data with query '%s': %s"
        logger.debug(msg, query, result)
        return result
    except Exception as e:
        msg = "Error applying query '%s': %s"
        logger.error(msg, query, e)
        return {}
