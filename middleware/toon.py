"""
TOON Middleware for FastAPI
Converts TOON ↔ JSON automatically based on Content-Type and Accept headers
"""
from fastapi import Request, Response
import json
import re

async def toon_middleware(request: Request, call_next):
    """Middleware para convertir TOON ↔ JSON automáticamente"""
    if request.headers.get("Content-Type") == "application/x-toon":
        try:
            body = await request.body()
            request.state.raw_body = body
            request.state.body = toon_to_json(body.decode())
        except Exception as e:
            return Response(
                content=json.dumps({"error": "Invalid TOON format"}),
                status_code=400,
                media_type="application/json"
            )

    response = await call_next(request)

    # Convertir respuesta a TOON si se solicita
    if request.headers.get("Accept") == "application/x-toon":
        response.body = json_to_toon(response.body)
        response.headers["Content-Type"] = "application/x-toon"

    return response

def toon_to_json(toon_str: str) -> dict:
    """Convierte TOON a JSON"""
    result = {}
    for line in toon_str.split('\n'):
        line = line.strip()
        if not line:
            continue

        # Ejemplo: user id123 name "John Doe" age 30
        parts = re.split(r'\s+', line)
        obj_name = parts[0]
        obj_data = {}

        i = 1
        while i < len(parts):
            key = parts[i]
            value = parts[i+1] if i+1 < len(parts) else None

            if value and value.startswith('"') and value.endswith('"'):
                obj_data[key] = value[1:-1]
                i += 2
            elif value and value.isdigit():
                obj_data[key] = int(value)
                i += 2
            else:
                obj_data[key] = value
                i += 2

        result[obj_name] = obj_data

    return {"data": result}

def json_to_toon(json_data: dict) -> str:
    """Convierte JSON a TOON"""
    toon = ""
    for obj_name, obj_data in json_data.get("data", {}).items():
        toon += f"{obj_name} "
        for key, value in obj_data.items():
            if isinstance(value, str):
                toon += f'{key} "{value}" '
            else:
                toon += f'{key} {value} '
        toon += "\n"
    return toon.strip()
