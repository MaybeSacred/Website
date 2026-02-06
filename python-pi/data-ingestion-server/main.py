# def main():
#     print("Hello from example!")


# if __name__ == "__main__":
#     main()
from fastapi import FastAPI
from .routers import data_ingestion, devices, home_objects#, camera

tags_metadata = [
    {
        "name": "home-objects",
        "description": "Operations for main home objects.",
    },
    {
        "name": "devices",
        "description": "Manage devices. These are a special type of home object that can ingest data.",
    },
    {
        "name": "data-ingestion",
        "description": "Ingest data from various sensors and devices.",
    },
]

app = FastAPI(
    openapi_tags=tags_metadata
)

app.include_router(data_ingestion.router)
app.include_router(devices.router)
app.include_router(home_objects.router)
#app.include_router(camera.router)

someData: dict[int, str] = {}

@app.get("/")
async def root():
    return {"message": "Hello World"}

# def Packet:
#     { "value": str }

@app.post("/items/{item_id}")
async def addItem(item_id: int): #, data: { "value": str }
    return {"item_id": item_id} #someData[id]