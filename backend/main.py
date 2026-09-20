from fastapi import FastAPI
import UrlEndpoints
from Connections import lifespan as connections

app = FastAPI(lifespan=connections)
app.include_router(UrlEndpoints.router)

