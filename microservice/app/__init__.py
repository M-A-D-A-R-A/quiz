from fastapi import Depends
from fastapi import FastAPI

from .controllers import question_controller
from .utils.auth_dependency import token_required
from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI(dependencies=[Depends(token_required)])
app = FastAPI()


origins = [
    "http://localhost:3000",  # React app address
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(question_controller.router)
