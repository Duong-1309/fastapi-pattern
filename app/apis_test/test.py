from configs.settings import app


@app.get("/")
async def root():
    return {"message": "Hello World"}
