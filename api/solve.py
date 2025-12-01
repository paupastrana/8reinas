# api/solve.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

# --- Inicialización de FastAPI ---
app = FastAPI()

# --- Modelos de Datos (para la comunicación con el Frontend) ---

class SolveRequest(BaseModel):
    # N es el tamaño del tablero, lo que antes era el '8' fijo.
    N: int 

# Una instantánea del estado del tablero y la acción tomada.
class Step(BaseModel):
    board: List[List[int]] # El estado actual
    row: int               # Fila donde se hizo la acción
    col: int               # Columna donde se hizo la acción
    action: str            # 'Place' (colocar) o 'Remove' (quitar/backtrack)

# Lista global para almacenar todos los pasos del algoritmo
# Se reiniciará en cada llamada al endpoint.
algorithm_steps: List[dict] = [] 

# --- Funciones de Validación (Adaptadas para un tamaño N genérico) ---

# Tus funciones 'valido' y 'diagonal_libre2' no las usaremos en esta versión
# de N-Reinas, pero las mantengo adaptadas para que no rompan la estructura.
# La función 'valido' combinaba validación de fila, columna y diagonal.
# Para N-Reinas, solo necesitamos validar si la posición es segura.

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
    
    # Las diagonales abajo no necesitan revisarse porque siempre colocamos
    # la reina en la fila actual y solo revisamos las filas anteriores (0 a fila-1).
    
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
    
    # CASO BASE: Todas las reinas colocadas 
    if fila == N:
        return True

    for columna in range(N):
        if valido(tablero, fila, columna, N):
            
            # 1. PRUEBA: Colocar la reina
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
