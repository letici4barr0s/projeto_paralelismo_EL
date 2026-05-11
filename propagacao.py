import numpy as np

try:
    from numba import njit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False


# ======================================================
# ESTADOS DAS CÉLULAS
# ======================================================

VAZIO = 0
ARVORE = 1
FOGO = 2
QUEIMADO = 3


# ======================================================
# ATUALIZAÇÃO SEQUENCIAL
# ======================================================

def atualizar_sequencial(grade, probabilidade):
    """
    Atualiza a grade inteira usando propagação
    menos previsível e mais orgânica.
    """

    altura, largura = grade.shape

    proximo = grade.copy()

    # Gerar vento aleatório para tornar propagação menos simétrica
    vento = {}
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            vento[(dx, dy)] = np.random.uniform(0.3, 2.0)  # Fator mais variável

    # Gerar ruído por célula para mais caos
    ruido = np.random.uniform(0.5, 1.5, size=(altura, largura))

    # Gerar terreno variável para quebrar simetria global
    terreno = np.random.uniform(0.5, 1.5, size=(altura, largura))

    # ===============================
    # FOGO -> QUEIMADO
    # ===============================

    fogo = grade == FOGO

    proximo[fogo] = QUEIMADO

    # ==================================================
    # PROCESSA ÁRVORES
    # ==================================================

    for y in range(altura):

        for x in range(largura):

            if grade[y, x] != ARVORE:
                continue

            influencia_fogo = 0.0

            # ==========================================
            # ANALISA VIZINHOS
            # ==========================================

            for dy in (-1, 0, 1):

                for dx in (-1, 0, 1):

                    if dy == 0 and dx == 0:
                        continue

                    ny = y + dy
                    nx = x + dx

                    if 0 <= ny < altura and 0 <= nx < largura:

                        if grade[ny, nx] == FOGO:

                            # ==========================
                            # PESO DIRECIONAL
                            # ==========================

                            # diagonais propagam menos
                            if dx != 0 and dy != 0:
                                peso = 0.55
                            # laterais propagam mais
                            else:
                                peso = 1.0

                            # Aplicar vento aleatório
                            peso *= vento[(dx, dy)]

                            influencia_fogo += peso

            # ==========================================
            # PROPAGAÇÃO ORGÂNICA
            # ==========================================

            if influencia_fogo > 0:

                # aleatoriedade local maior
                variacao = np.random.uniform(0.5, 1.5)

                chance = (
                    probabilidade
                    * (influencia_fogo / 4.0)
                    * variacao
                )

                # Aplicar ruído local
                chance *= ruido[y, x]

                # Aplicar terreno variável
                chance *= terreno[y, x]

                # limite máximo
                chance = min(chance, 1.0)

                if np.random.random() < chance:
                    proximo[y, x] = FOGO

    return proximo


# ======================================================
# ATUALIZAÇÃO PARALELA NUMPY
# ======================================================

def _atualizar_faixa_numpy(
    source,
    dest,
    y0,
    y1,
    probabilidade
):
    """
    Atualiza apenas uma faixa da matriz.
    """

    altura, largura = source.shape

    if y1 <= y0:
        return

    # Gerar vento aleatório para tornar propagação menos simétrica
    vento = {}
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            vento[(dx, dy)] = np.random.uniform(0.3, 2.0)  # Fator mais variável

    # Gerar ruído por célula para a faixa
    ruido = np.random.uniform(0.5, 1.5, size=(y1 - y0, largura))

    # Gerar terreno variável para a faixa
    terreno = np.random.uniform(0.5, 1.5, size=(y1 - y0, largura))

    origem = source[y0:y1]

    destino = dest[y0:y1]

    # copia estado atual
    destino[:] = origem

    # ==========================================
    # FOGO -> QUEIMADO
    # ==========================================

    queimando = origem == FOGO

    destino[queimando] = QUEIMADO

    # ==========================================
    # PROCESSAMENTO DAS ÁRVORES
    # ==========================================

    # Gerar lista de posições em ordem aleatória para quebrar simetria
    num_celulas = (y1 - y0) * largura
    indices = np.arange(num_celulas)
    np.random.shuffle(indices)

    for idx in indices:
        y_local = idx // largura
        x = idx % largura

        if origem[y_local, x] != ARVORE:
            continue

        y_global = y0 + y_local

        influencia_fogo = 0.0

        # ==================================
        # VIZINHOS
        # ==================================

        for dy in (-1, 0, 1):

            for dx in (-1, 0, 1):

                if dy == 0 and dx == 0:
                    continue

                ny = y_global + dy
                nx = x + dx

                if 0 <= ny < altura and 0 <= nx < largura:

                    if source[ny, nx] == FOGO:

                        # diagonais possuem menos força
                        if dx != 0 and dy != 0:
                            peso = 0.55
                        else:
                            peso = 1.0

                        # Aplicar vento aleatório
                        peso *= vento[(dx, dy)]

                        influencia_fogo += peso

        # ==================================
        # CHANCE ORGÂNICA
        # ==================================

        if influencia_fogo > 0:

            variacao = np.random.uniform(
                0.5,
                1.5
            )

            chance = (
                probabilidade
                * (influencia_fogo / 4.0)
                * variacao
            )

            # Aplicar ruído local
            chance *= ruido[y_local, x]

            # Aplicar terreno variável
            chance *= terreno[y_local, x]

            chance = min(chance, 1.0)

            if np.random.random() < chance:

                destino[y_local, x] = FOGO


# ======================================================
# FALLBACK NUMBA
# ======================================================

def _atualizar_faixa_numba(
    source,
    dest,
    y0,
    y1,
    probabilidade
):
    raise RuntimeError(
        "Numba não está disponível"
    )


# ======================================================
# IMPLEMENTAÇÃO NUMBA
# ======================================================

if NUMBA_AVAILABLE:

    @njit(nogil=True)
    def _atualizar_faixa_numba(
        source,
        dest,
        y0,
        y1,
        probabilidade
    ):

        altura, largura = source.shape

        for y in range(y0, y1):

            for x in range(largura):

                estado = source[y, x]

                # ==================================
                # FOGO -> QUEIMADO
                # ==================================

                if estado == FOGO:

                    dest[y, x] = QUEIMADO

                    continue

                # ==================================
                # NÃO É ÁRVORE
                # ==================================

                if estado != ARVORE:

                    dest[y, x] = estado

                    continue

                # ==================================
                # ANALISA VIZINHOS
                # ==================================

                influencia_fogo = 0.0

                for dy in (-1, 0, 1):

                    for dx in (-1, 0, 1):

                        if dy == 0 and dx == 0:
                            continue

                        ny = y + dy
                        nx = x + dx

                        if (
                            0 <= ny < altura
                            and
                            0 <= nx < largura
                        ):

                            if source[ny, nx] == FOGO:

                                # diagonais propagam menos
                                if dx != 0 and dy != 0:
                                    peso = 0.55

                                # laterais propagam mais
                                else:
                                    peso = 1.0

                                influencia_fogo += peso

                # ==================================
                # PROPAGAÇÃO MAIS NATURAL
                # ==================================

                if influencia_fogo > 0:

                    # variação local
                    variacao = (
                        0.7 +
                        np.random.random() * 0.6
                    )

                    chance = (
                        probabilidade
                        * (0.45 + influencia_fogo / 1.5)
                        * variacao
                    )

                    if chance > 1.0:
                        chance = 1.0

                    if np.random.random() < chance:

                        dest[y, x] = FOGO

                    else:

                        dest[y, x] = ARVORE

                else:

                    dest[y, x] = ARVORE