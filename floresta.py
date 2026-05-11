import numpy as np

VAZIO = 0
ARVORE = 1
FOGO = 2
QUEIMADO = 3


def criar_floresta(largura, altura, densidade=0.75, semente=None):
    """Cria uma grade 2D de floresta e inicia fogo na borda esquerda."""
    rng = np.random.default_rng(semente)
    grade = rng.choice(
        [VAZIO, ARVORE],
        size=(altura, largura),
        p=[1 - densidade, densidade],
    ).astype(np.uint8)
    grade[altura // 4 : 3 * altura // 4, 0] = FOGO
    return grade
