from pydantic import BaseModel, ConfigDict


class ClientBase(BaseModel):
    name: str
    address: str

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: str | None = None
    address: str | None = None

class ClientInDB(ClientBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
