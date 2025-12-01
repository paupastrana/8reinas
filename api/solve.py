from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "*" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],
)

class SolveRequest(BaseModel):
    N: int 


class Step(BaseModel):
    board: List[List[int]] 
    row: int               # fila
    col: int               # columan
    action: str            # place or remove


algorithm_steps: List[dict] = [] 



def diagonal_libre(tablero, fila, col, N):
    
    # diagonal arriba izquierda
    i, j = fila - 1, col - 1
    while i >= 0 and j >= 0:
        if tablero[i][j] == 1:
            return False
        i -= 1
        j -= 1

    # diagonal arriba derecha
    i, j = fila - 1, col + 1
    while i >= 0 and j < N:
        if tablero[i][j] == 1:
            return False
        i -= 1
        j += 1
    

    
    return True


def valido(tablero, x, y, N): 
    # x es la fila actual, y es la columna actual

    for i in range(x): 
        if tablero[i][y] == 1:
            return False
            
  
    if(diagonal_libre(tablero, x, y, N) == False):
        return False
        
    return True


def solucion_8reinas(tablero, fila, N):
    global algorithm_steps
    
    #todas las reinas colocadas 
    if fila == N:
        return True

    for columna in range(N):
        if valido(tablero, fila, columna, N):
            
            #colocar reina
            tablero[fila][columna] = 1
            
            #registrar paso de colocar reina
            algorithm_steps.append(Step(
                board=[r[:] for r in tablero], # Clonar el tablero
                row=fila, 
                col=columna, 
                action='Place'
            ).model_dump())

            #intentar colocar la siguiente reina
            if solucion_8reinas(tablero, fila + 1, N):
                return True # Éxito: Encontramos una solución.

            #si no se pudo colocar la siguiente reina, RETROCEDER
            tablero[fila][columna] = 0
            
            # registrar paso de quitar reina (backtrack)
            algorithm_steps.append(Step(
                board=[r[:] for r in tablero], # Clonar el tablero
                row=fila, 
                col=columna, 
                action='Remove'
            ).model_dump())
            
    # Si probamos todas las columnas y no encontramos solución
    return False

@app.post("/api/solve")
def solve_n_queens_endpoint(request: SolveRequest):
    global algorithm_steps
    N = request.N
    
    #restricción
    if not (4 <= N <= 12):
        return {"error": f"N debe estar entre 4 y 12. Se recibió N={N}"}
    
    # reiniciar la lista de pasos para la nueva solicitud
    algorithm_steps = []
    
    #inicializar el tablero de N x N
    board = [[0] * N for _ in range(N)]
    

    success = solucion_8reinas(board, 0, N) 

    if success:
        
        return {"steps": algorithm_steps}
    else:
        # En el caso de N=2 o N=3 (no tienen solución)
        return {"steps": [], "message": f"No solution found for N={N}"}
