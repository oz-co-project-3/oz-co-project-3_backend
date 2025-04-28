from app.exceptions.base_exceptions import CustomException


class InvalidQueryParamsException(CustomException):
    def __init__(self, message: str):
        super().__init__(status_code=400, code="invalid_query_params", error=message)


class SearchKeywordTooLongException(CustomException):
    def __init__(self, length: int):
        super().__init__(
            status_code=400,
            code="search_too_long",
            error=f"검색어는 {length}자 이하로 입력해야 합니다.",
        )
