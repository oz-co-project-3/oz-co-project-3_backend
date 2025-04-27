from fastapi import HTTPException, status


class CustomException(HTTPException):
    def __init__(self, *, error: str, code: str, status_code: int = 400):
        super().__init__(status_code=status_code)
        self.error = error
        self.code = code
