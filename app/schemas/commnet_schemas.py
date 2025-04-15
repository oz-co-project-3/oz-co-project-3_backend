from pydantic import BaseModel


class CommentCreateUpdateSchema(BaseModel):
    content: str
