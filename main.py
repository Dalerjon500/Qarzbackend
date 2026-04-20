from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from endpoint import qarzdor_router

# uvicorn main:app --reload

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(users_router)
# app.include_router(posts_router)
# app.include_router(comment_router)
# app.include_router(todos_router)
# app.include_router(car_router)

app.include_router(qarzdor_router.router)
