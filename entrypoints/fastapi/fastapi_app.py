from fastapi import FastAPI

from entrypoints.fastapi import feed_endpoints, user_endpoints
from rss_reader.service_layer.update_service import run_scheduling

app = FastAPI()

app.include_router(user_endpoints.router)
app.include_router(feed_endpoints.router)
run_scheduling()


@app.get("/")
async def root():
    return {"message": "Please see /docs"}
