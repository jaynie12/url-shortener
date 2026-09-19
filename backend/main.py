from fastapi import FastAPI
import UrlEndpoints

app = FastAPI()
app.include_router(UrlEndpoints.router)
