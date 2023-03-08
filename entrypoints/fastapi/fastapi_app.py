from fastapi import FastAPI
from entrypoints.fastapi import feed_endpoints
from entrypoints.fastapi import user_endpoints

app = FastAPI()

app.include_router(user_endpoints.router)
app.include_router(feed_endpoints.router)


@app.get("/")
async def root():
    return {"message": "Please see /docs"}

