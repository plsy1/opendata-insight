from pydantic import BaseModel

class DecryptedImagePayload(BaseModel):
    url: str
    exp: int

    @property
    def expired(self) -> bool:
        import time
        return self.exp < time.time()