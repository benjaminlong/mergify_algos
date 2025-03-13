from fastapi import FastAPI, Response, Request

from mergify_algos.config import Settings
from mergify_algos.routers import github
from mergify_algos.utils import display_secret


__version__ = "0.1.0"
app = FastAPI(version=__version__)
settings = Settings()


@app.get("/")
async def root(request: Request):
    ip = request.client.host
    return {
        "message": "Hello World",
        "client_ip": ip,
        "app_settings": {
            "app_name": settings.app_name,
            "github_token": display_secret(settings.github_token)
        },
    }


@app.get("/healthz")
async def healthz(response: Response):
    response.headers["X-App-Alive"] = "True"
    return {"message": "It's alive!"}


@app.get("/error")
async def error():
    raise ValueError("this always fails, don't worry")


app.include_router(github.router)


if __name__ == "__main__":
    import uvicorn

    # Note: localhost:8000 should work too
    uvicorn.run(app, host="127.0.0.1", port=8000, timeout_keep_alive=60)
