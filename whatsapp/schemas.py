from pydantic import BaseModel


class WhatsAppCallbackRequest(BaseModel):
    tenant_id: str
    code: str
