from pydantic import BaseModel, ConfigDict


class ClientBase(BaseModel):
    """
    Base schema for common client attributes.

    Attributes:
        name: The full name or company name of the client.
        address: The primary billing/shipping address of the client.
    """
    name: str
    address: str

class ClientCreate(ClientBase):
    """
    Schema for creating a new client. Inherits all fields from ClientBase.
    """
    pass

class ClientUpdate(BaseModel):
    """
    Schema for updating an existing client. All fields are optional for partial updates.

    Attributes:
        name: The full name or company name of the client (optional).
        address: The primary billing/shipping address of the client (optional).
    """
    name: str | None = None
    address: str | None = None

class ClientInDB(ClientBase):
    """
    Schema for representing a client stored in the database.

    Includes the database-generated ID and configuration to work with ORM models.

    Attributes:
        id: The unique identifier for the client.
    """
    id: int
    model_config = ConfigDict(from_attributes=True)
