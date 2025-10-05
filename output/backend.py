from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

class CalculationRequest(BaseModel):
    num1: float
    num2: float
    operation: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/calculate")
async def calculate(req: CalculationRequest):
    try:
        if req.operation == "+":
            result = req.num1 + req.num2
        elif req.operation == "-":
            result = req.num1 - req.num2
        elif req.operation == "*":
            result = req.num1 * req.num2
        elif req.operation == "/":
            if req.num2 == 0:
                raise HTTPException(status_code=400, detail="Division by zero")
            result = req.num1 / req.num2
        else:
            raise HTTPException(status_code=400, detail="Unsupported operation")
        return {"result": result}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
