# def main():
#     print("Hello from example!")


# if __name__ == "__main__":
#     main()
from contextlib import asynccontextmanager

from fastapi import FastAPI
from .routers import data_ingestion, devices, groups, home_objects, libraries#, camera
from fastapi.middleware.cors import CORSMiddleware
from .postgres_data import initialize_database

# Define the list of origins that are allowed to make cross-origin requests
origins = [
    "http://127.0.0.1:8081",  # Example front-end development server
    "http://localhost:8081",  # Example front-end development server
    "http://localhost:8080", 
    "http://localhost:5173", 
    "http://localhost:4173", 
    #"https://your-frontend-domain.com",
    # You can add more origins as needed
]

tags_metadata = [
    {
        "name": "libraries",
        "description": "Libraries, document metadata, and uploaded images.",
    },
    {
        "name": "home-objects",
        "description": "Operations for main home objects.",
    },
    {
        "name": "groups",
        "description": "Named groups of points.",
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_database()
    yield


app = FastAPI(
    lifespan=lifespan,
    openapi_tags=tags_metadata
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # Allows specified origins
    allow_credentials=True,        # Allows cookies/authorization headers to be included in requests
    allow_methods=["*"],           # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],           # Allows all headers
)

app.include_router(data_ingestion.router)
app.include_router(devices.router)
app.include_router(home_objects.router)
app.include_router(groups.router)
app.include_router(libraries.router)
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