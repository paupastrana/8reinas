import json
from typing import List, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# -----------------------------------------------------
#    ALGORITMO N-REINAS (GENERALIZADO A N, CON PASOS)
# -----------------------------------------------------

def diagonal_libre(tablero, fila, col, n):
    # diagonal arriba izquierda
    i, j = fila - 1, col - 1
    while i >= 0 and j >= 0:
        if tablero[i][j] == 1:
            return False
        i -= 1
        j -= 1

    # diagonal arriba derecha
    i, j = fila - 1, col + 1
    while i >= 0 and j < n:
        if tablero[i][j] == 1:
            return False
        i -= 1
        j += 1

    # diagonal abajo izquierda
    i, j = fila + 1, col - 1
    while i < n and j >= 0:
        if tablero[i][j] == 1:
            return False
        i += 1
        j -= 1

    # diagonal abajo derecha
    i, j = fila + 1, col + 1
    while i < n and j < n:
        if tablero[i][j] == 1:
            return False
        i += 1
        j += 1

    return True


def valido(tablero, x, y, n):
    # revisamos fila x y columna y
    for i in range(n):
        if tablero[x][i] == 1:
            return False
        if tablero[i][y] == 1:
            return False
    if not diagonal_libre(tablero, x, y, n):
        return False
    return True


def snapshot(tablero, row: Optional[int], col: Optional[int], action: str) -> Dict:
    # copia del tablero para no modificar pasos anteriores
    return {
        "board": [fila[:] for fila in tablero],
        "row": row,
        "col": col,
        "action": action  # "place", "remove" o "solution"
    }


def resolver_n_reinas(tablero, fila, n, steps) -> bool:
    # caso base: solución completa
    if fila == n:
        steps.append(snapshot(tablero, None, None, "solution"))
        return True  # solo una solución

    for columna in range(n):
        if valido(tablero, fila, columna, n):
            # colocar reina
            tablero[fila][columna] = 1
            steps.append(snapshot(tablero, fila, columna, "place"))

            if resolver_n_reinas(tablero, fila + 1, n, steps):
                return True

            # retroceder (backtracking)
            tablero[fila][columna] = 0
            steps.append(snapshot(tablero, fila, columna, "remove"))

    return False


def solve_n_reinas(n: int):
    tablero = [[0 for _ in range(n)] for _ in range(n)]
    steps: List[Dict] = []
    resolver_n_reinas(tablero, 0, n, steps)
    return steps


# ---------------------------------------
#   FASTAPI (para cumplir con el profe)
# ---------------------------------------

app = FastAPI()


class SolveRequest(BaseModel):
    n: int


class Step(BaseModel):
    board: List[List[int]]
    row: Optional[int]
    col: Optional[int]
    action: str


class SolveResponse(BaseModel):
    steps: List[Step]


@app.post("/api/solve", response_model=SolveResponse)
def solve(req: SolveRequest):
    n = req.n
    if n < 4 or n > 12:
        raise HTTPException(
            status_code=400,
            detail="N debe estar entre 4 y 12."
        )

    steps_dicts = solve_n_reinas(n)
    steps = [Step(**s) for s in steps_dicts]
    return SolveResponse(steps=steps)


# ------------------------------------------
#   handler PARA VERCEL (serverless)
#   Vercel usará ESTA función al desplegar.
# ------------------------------------------

def handler(request):
    try:
        body = request.get_json()
        n = int(body.get("n", 8))

        if n < 4 or n > 12:
            return {
                "statusCode": 400,
                "body": json.dumps({"detail": "N debe estar entre 4 y 12."})
            }

        steps = solve_n_reinas(n)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"steps": steps})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"detail": str(e)})
        }
