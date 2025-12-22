from pydantic import BaseModel, HttpUrl

class DecryptedImagePayload(BaseModel):
    url: str
    exp: int
    src: str

    @property
    def expired(self) -> bool:
        import time
        return self.exp < time.time()