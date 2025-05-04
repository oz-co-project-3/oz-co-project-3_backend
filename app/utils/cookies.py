from fastapi import Response


def set_token_cookies(
    response: Response, access_token: str, refresh_token: str | None = None
):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=False,
        secure=False,  # 로컬 테스트 시 False, 배포 시 True
        samesite="lax",
        path="/",
    )

    if refresh_token is not None:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,  # 로컬 테스트 시 False, 배포 시 True
            samesite="lax",
            path="/",
        )
