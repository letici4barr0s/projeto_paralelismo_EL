import numpy as np

VAZIO   = 0
ARVORE  = 1
FOGO    = 2
QUEIMADO = 3

def criar_floresta(largura, altura, densidade=0.75):
    """Cria uma grade aleatória de árvores."""
    grade = np.random.choice(
        [VAZIO, ARVORE],
        size=(altura, largura),
        p=[1 - densidade, densidade]
    )
    # Ignição inicial na lateral esquerda (coluna 0, várias linhas)
    for y in range(altura // 4, 3 * altura // 4):
        grade[y, 0] = FOGO
    return grade