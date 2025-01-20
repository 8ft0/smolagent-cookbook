from typing import Optional


class ShoppingListError(Exception):
    """Base exception for shopping list related errors"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(ShoppingListError):
    """Raised when input validation fails"""
    pass


class ItemNotFoundError(ShoppingListError):
    """Raised when an item is not found"""
    pass


class InvalidQuantityError(ValidationError):
    """Raised when quantity is invalid"""
    pass


class InvalidSkuError(ValidationError):
    """Raised when SKU is invalid"""
    pass
