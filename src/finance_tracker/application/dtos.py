"""Data transfer objects for transaction operations."""

from pydantic import BaseModel, ConfigDict, Field


class AddTransactionDTO(BaseModel):
    """Data needed to create a new transaction.
    
    Args:
        description: Transaction description (1-200 characters)
        amount: Positive transaction amount
        type_: Transaction type as string ("income" or "expense")
        categories: List of category names
        
    Raises:
        ValueError: If amount is not positive
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    description: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0)
    type_: str = Field(..., pattern="^(income|expense)$")
    categories: list[str] = Field(default_factory=list)