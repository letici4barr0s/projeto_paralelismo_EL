import numpy as np

try:
    from numba import njit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False

VAZIO = 0
ARVORE = 1
FOGO = 2
QUEIMADO = 3


def atualizar_sequencial(grade, probabilidade):
    """Atualiza a grade inteira usando operações NumPy vetorizadas."""
    altura, largura = grade.shape
    proximo = grade.copy()

    fogo = grade == FOGO
    proximo[fogo] = QUEIMADO

    padded = np.pad(fogo, ((1, 1), (1, 1)), constant_values=False)
    vizinhos_em_chamas = (
        padded[:-2, 1:-1]
        | padded[2:, 1:-1]
        | padded[1:-1, :-2]
        | padded[1:-1, 2:]
        | padded[:-2, :-2]
        | padded[:-2, 2:]
        | padded[2:, :-2]
        | padded[2:, 2:]
    )

    incendiar = (grade == ARVORE) & vizinhos_em_chamas
    rand = np.random.random(size=grade.shape)
    proximo[incendiar & (rand < probabilidade)] = FOGO
    return proximo


def _atualizar_faixa_numpy(source, dest, y0, y1, probabilidade):
    """Atualiza uma faixa de linhas [y0:y1) sem copiar a grade inteira."""
    altura, largura = source.shape
    linhas = y1 - y0
    if linhas <= 0:
        return

    bloco_fogo = np.zeros((linhas + 2, largura), dtype=bool)
    bloco_fogo[1:-1] = source[y0:y1] == FOGO

    if y0 > 0:
        bloco_fogo[0] = source[y0 - 1] == FOGO
    if y1 < altura:
        bloco_fogo[-1] = source[y1] == FOGO

    bloco_padded = np.pad(bloco_fogo, ((0, 0), (1, 1)), constant_values=False)
    vizinhos = (
        bloco_padded[:-2, 1:-1]
        | bloco_padded[2:, 1:-1]
        | bloco_padded[1:-1, :-2]
        | bloco_padded[1:-1, 2:]
        | bloco_padded[:-2, :-2]
        | bloco_padded[:-2, 2:]
        | bloco_padded[2:, :-2]
        | bloco_padded[2:, 2:]
    )

    destino = dest[y0:y1]
    origem = source[y0:y1]
    destino[:] = origem
    queima = origem == FOGO
    destino[queima] = QUEIMADO

    incendiar = (origem == ARVORE) & vizinhos
    if probabilidade > 0:
        rand = np.random.random(size=incendiar.shape)
        destino[incendiar & (rand < probabilidade)] = FOGO


def _atualizar_faixa_numba(source, dest, y0, y1, probabilidade):
    raise RuntimeError("Numba não está disponível")


if NUMBA_AVAILABLE:
    @njit(nogil=True)
    def _atualizar_faixa_numba(source, dest, y0, y1, probabilidade):
        altura, largura = source.shape
        for y in range(y0, y1):
            for x in range(largura):
                estado = source[y, x]
                if estado == FOGO:
                    dest[y, x] = QUEIMADO
                    continue
                if estado != ARVORE:
                    dest[y, x] = estado
                    continue

                tem_vizinho = False
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dy == 0 and dx == 0:
                            continue
                        ny = y + dy
                        nx = x + dx
                        if 0 <= ny < altura and 0 <= nx < largura:
                            if source[ny, nx] == FOGO:
                                tem_vizinho = True
                                break
                    if tem_vizinho:
                        break

                if tem_vizinho and np.random.random() < probabilidade:
                    dest[y, x] = FOGO
                else:
                    dest[y, x] = ARVORE
