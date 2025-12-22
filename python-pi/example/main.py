# def main():
#     print("Hello from example!")


# if __name__ == "__main__":
#     main()
from fastapi import FastAPI
from .routers import data_ingestion

app = FastAPI()

app.include_router(data_ingestion.router)

someData: dict[int, str] = []

@app.get("/")
async def root():
    return {"message": "Hello World"}

# def Packet:
#     { "value": str }

@app.post("/items/{item_id}")
async def addItem(item_id: int): #, data: { "value": str }
    return {"item_id": item_id} #someData[id]