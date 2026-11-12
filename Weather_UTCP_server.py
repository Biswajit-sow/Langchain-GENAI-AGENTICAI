from fastapi import FastAPI

app = FastAPI()

@app.get("/weather/{location}")
def get_weather(location: str) -> dict:
    # mocked, same as your MCP example; replace with a real API call
    return {"weather": f"It's sunny and 25°C in {location}."}

@app.get("/utcp")
def utcp_manual():
    return {
        "utcp_version": "1.0.0",
        "manual_version": "1.0.0",
        "tools": [
            {
                "name": "get_weather",
                "description": "Get the weather for a given location (mocked example)",
                "inputs": {
                    "type": "object",
                    "properties": {"location": {"type": "string"}},
                    "required": ["location"],
                },
                "tool_call_template": {
                    "call_template_type": "http",
                    "url": "http://localhost:8000/weather/{location}",
                    "http_method": "GET",
                },
            }
        ],
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)