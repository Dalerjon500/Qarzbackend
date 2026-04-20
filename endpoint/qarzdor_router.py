from fastapi import APIRouter
from services.qarzdor_service import QarzdorService, Qarzdor, Qarz

router = APIRouter(
    prefix="/qarzdor",
    tags=["qarzdor"],
)

qarzdor_service = QarzdorService()


@router.get("/")
async def get_qarzdorlar():
    return qarzdor_service.get_qarzdorlar()


@router.get("/{qarzdor_id}")
async def get_qarzdor(qarzdor_id: int):
    return qarzdor_service.get_qarzdor_by_id(qarzdor_id)


@router.post("/", status_code=201)
async def create_qarzdor(qarzdor: Qarzdor):
    return qarzdor_service.create_qarzdor(qarzdor)


@router.get("/{qarzdor_id}/qarzlar")
async def get_qarzlar(qarzdor_id: int):
    return qarzdor_service.get_qarz_by_qarzdor_id(qarzdor_id)


@router.post("/{qarzdor_id}/qarz", status_code=201)
async def add_qarz(
    qarzdor_id: int,
    qarz: Qarz
):
    return qarzdor_service.add_qarz_to_qarzdor(qarzdor_id, qarz)


@router.post("/{qarzdor_id}/repayment", status_code=201)
async def repayment(
    qarzdor_id: int,
    data: dict  # { "qarz_id": int, "miqdor": int }
):
    return qarzdor_service.repayment(
        qarzdor_id=qarzdor_id,
        qarz_id=data["qarz_id"],
        miqdor=data["miqdor"],
    )


@router.get("/{qarzdor_id}/qarzlar-history")
async def qarzlar_history(qarzdor_id: int):
    return qarzdor_service.get_qarzlar_history(qarzdor_id)
