from app.exceptions.base_exceptions import CustomException


class JobPostingNotFoundException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=404, code="job_posting_not_found", error="공고를 찾을 수 없습니다."
        )


class NotificationNotFoundException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=404, code="notification_not_found", error="등록된 공고를 찾을 수 없습니다."
        )


class InvalidEmploymentTypeException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=400,
            code="invalid_employment_type",
            error="employment_type은 ['공공', '일반'] 중 하나여야 합니다.",
        )


class InvalidCareerTypeException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=400,
            code="invalid_career_type",
            error="career는 ['신입', '경력직', '경력무관'] 중 하나여야 합니다.",
        )


class InvalidEmployMethodException(CustomException):
    def __init__(self):
        super().__init__(
            status_code=400,
            code="invalid_employ_method",
            error="employ_method는 ['정규직', '계약직', '일용직', '프리랜서', '파견직'] 중 하나여야 합니다.",
        )


class TooManyPositionsException(CustomException):
    def __init__(self, max_count: int):
        super().__init__(
            status_code=400,
            code="too_many_positions",
            error=f"포지션은 최대 {max_count}개까지 지정할 수 있습니다.",
        )
