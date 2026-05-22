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
# ATUALIZAÇÃO SEQUENCIAL (OTIMIZADA)
# ======================================================

def _atualizar_sequencial_numba(grade, proximo, probabilidade):
    altura, largura = grade.shape
    
    for y in range(altura):
        for x in range(largura):
            estado = grade[y, x]
            
            if estado == FOGO:
                proximo[y, x] = QUEIMADO
                continue
            elif estado != ARVORE:
                proximo[y, x] = estado
                continue
                
            # Verifica vizinhos para células do tipo ARVORE
            influencia_fogo = 0.0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == 0 and dx == 0:
                        continue
                    ny = y + dy
                    nx = x + dx
                    
                    if 0 <= ny < altura and 0 <= nx < largura:
                        if grade[ny, nx] == FOGO:
                            # Diagonais propagam menos, laterais propagam mais
                            peso = 0.55 if (dx != 0 and dy != 0) else 1.0
                            influencia_fogo += peso
            
            if influencia_fogo > 0:
                # Chance base baseada na influência dos vizinhos em chamas
                chance = min(1.0, probabilidade * (0.8 + influencia_fogo))
                
                if np.random.random() < chance:
                    proximo[y, x] = FOGO
                else:
                    proximo[y, x] = ARVORE
            else:
                proximo[y, x] = ARVORE

if NUMBA_AVAILABLE:
    atualizar_sequencial_jit = njit(nogil=True)(_atualizar_sequencial_numba)
else:
    atualizar_sequencial_jit = _atualizar_sequencial_numba

def atualizar_sequencial(grade, probabilidade):
    proximo = np.empty_like(grade)
    atualizar_sequencial_jit(grade, proximo, probabilidade)
    return proximo

# ======================================================
# ATUALIZAÇÃO PARALELA (FAIXAS)
# ======================================================

def _atualizar_faixa_core(source, dest, y0, y1, probabilidade):
    altura, largura = source.shape
    
    for y in range(y0, y1):
        for x in range(largura):
            estado = source[y, x]
            
            if estado == FOGO:
                dest[y, x] = QUEIMADO
                continue
            elif estado != ARVORE:
                dest[y, x] = estado
                continue
                
            influencia_fogo = 0.0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == 0 and dx == 0:
                        continue
                    ny = y + dy
                    nx = x + dx
                    
                    if 0 <= ny < altura and 0 <= nx < largura:
                        if source[ny, nx] == FOGO:
                            peso = 0.55 if (dx != 0 and dy != 0) else 1.0
                            influencia_fogo += peso
            
            if influencia_fogo > 0:
                chance = min(1.0, probabilidade * (0.8 + influencia_fogo))
                
                if np.random.random() < chance:
                    dest[y, x] = FOGO
                else:
                    dest[y, x] = ARVORE
            else:
                dest[y, x] = ARVORE

if NUMBA_AVAILABLE:
    _atualizar_faixa_numba = njit(nogil=True)(_atualizar_faixa_core)
    _atualizar_faixa_numpy = _atualizar_faixa_core # Se chamado sem JIT
else:
    _atualizar_faixa_numba = _atualizar_faixa_core
    _atualizar_faixa_numpy = _atualizar_faixa_core