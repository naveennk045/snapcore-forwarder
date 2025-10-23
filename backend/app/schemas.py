from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional
from .models import Provider

# ============ Account Schemas ============
class AccountBase(BaseModel):
    provider: Provider
    post_enabled: bool = True
    config: Dict[str, Any] = Field(..., description="Provider-specific configuration")

class AccountCreate(AccountBase):
    user_id: int = Field(..., description="User ID (must exist in database)")

class AccountUpdate(BaseModel):
    post_enabled: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None

class AccountResponse(AccountBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)

# ============ Generic Response ============
class MessageResponse(BaseModel):
    message: str
