from app.exceptions.base_exceptions import CustomException


class FreeBoardNotFoundException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=404, code="free_board_not_found", error="자유 게시판을 찾을 수 없습니다."
        )


class CompanyNotFoundException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=404, code="company_not_found", error="회사를 찾을 수 없습니다."
        )
