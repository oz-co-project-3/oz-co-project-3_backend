from app.models.free_board_models import FreeBoard
from app.schemas.freeboard_schemas import FreeBoardCreateUpdate


async def create_free_board(free_board: FreeBoardCreateUpdate, user: User):
    board = await FreeBoard.create(**free_board.dict(), user=user)
    return board
