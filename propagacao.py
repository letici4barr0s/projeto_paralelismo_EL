import numpy as np
from floresta import ARVORE, FOGO, QUEIMADO

def processar_faixa(args):
    """
    Processa uma fatia horizontal da grade.
    Cada processo recebe: (grade_completa, y_inicio, y_fim, probabilidade)
    Retorna apenas a fatia atualizada.
    """
    grade, y_inicio, y_fim, prob = args
    altura, largura = grade.shape
    faixa = grade[y_inicio:y_fim, :].copy()

    for y_local in range(y_fim - y_inicio):
        y_global = y_inicio + y_local
        for x in range(largura):
            if grade[y_global, x] == FOGO:
                # Célula atual vira queimada
                faixa[y_local, x] = QUEIMADO
                # Verifica os 8 vizinhos
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dy == 0 and dx == 0:
                            continue
                        ny, nx = y_global + dy, x + dx
                        if 0 <= ny < altura and 0 <= nx < largura:
                            if grade[ny, nx] == ARVORE:
                                if np.random.random() < prob:
                                    # Marca na faixa se pertence a ela
                                    ly = ny - y_inicio
                                    if 0 <= ly < (y_fim - y_inicio):
                                        faixa[ly, nx] = FOGO
    return (y_inicio, y_fim, faixa)