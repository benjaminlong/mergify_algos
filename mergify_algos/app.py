from fastapi import FastAPI, Response, Request

from mergify_algos.routers import github


__version__ = "0.1.0"
app = FastAPI(version=__version__)


@app.get("/")
async def root(request: Request):
    ip = request.client.host
    return {"message": "Hello World", "client_ip": ip}


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
