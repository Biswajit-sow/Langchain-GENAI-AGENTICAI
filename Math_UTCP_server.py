from fastapi import FastAPI

app = FastAPI()

# ---- Real tool endpoints (plain HTTP, no protocol wrapper) ----
@app.get("/add/{a}/{b}")
def add(a: int, b: int) -> dict:
    return {"result": a + b}

@app.get("/multiply/{a}/{b}")
def multiply(a: int, b: int) -> dict:
    return {"result": a * b}

# ---- UTCP discovery endpoint: the "manual" ----
@app.get("/utcp")
def utcp_manual():
    two_ints = {
        "type": "object",
        "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
        "required": ["a", "b"],
    }
    return {
        "utcp_version": "1.0.0",
        "manual_version": "1.0.0",
        "tools": [
            {
                "name": "add",
                "description": "Add two numbers",
                "inputs": two_ints,
                "tool_call_template": {
                    "call_template_type": "http",
                    "url": "http://localhost:8001/add/{a}/{b}",
                    "http_method": "GET",
                },
            },
            {
                "name": "multiply",
                "description": "Multiply two numbers",
                "inputs": two_ints,
                "tool_call_template": {
                    "call_template_type": "http",
                    "url": "http://localhost:8001/multiply/{a}/{b}",
                    "http_method": "GET",
                },
            },
        ],
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)