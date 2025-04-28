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


class InvalidViewCountException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=400, code="invalid_view_count", error="view_count는 0 이상이어야 합니다."
        )


class InvalidOffsetException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=400, code="invalid_offset", error="offset은 0 이상이어야 합니다."
        )


class InvalidLimitException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=400, code="invalid_limit", error="limit는 1 이상 100 이하로 입력해주세요."
        )
