import numpy as np
import time
from multiprocessing import cpu_count
from floresta import criar_floresta, VAZIO, ARVORE, FOGO, QUEIMADO
from paralelo import atualizar_paralelo

def contar_celulas(grade):
    """Conta células por estado."""
    em_chamas = np.sum(grade == FOGO)
    queimadas = np.sum(grade == QUEIMADO)
    arvores = np.sum(grade == ARVORE)
    return em_chamas, queimadas, arvores

def simular(largura, altura, densidade, prob_fogo, num_processos, num_passos=100):
    """Executa a simulação em modo CLI."""
    
    print(f"\n{'='*70}")
    print(f"SIMULADOR DE INCÊNDIO FLORESTAL - MODO CONSOLE")
    print(f"{'='*70}")
    print(f"Grade: {largura}x{altura} = {largura*altura:,} células")
    print(f"Densidade florestal: {densidade*100:.0f}%")
    print(f"Processos paralelos: {num_processos}")
    print(f"Passos: {num_passos}")
    print(f"{'='*70}\n")
    
    # Criar floresta
    grade = criar_floresta(largura, altura, densidade)
    em_chamas, queimadas, arvores = contar_celulas(grade)
    
    print(f"INICIAL: Árvores={arvores:,} | Em chamas={em_chamas:,} | Queimadas={queimadas:,}\n")
    
    tempo_total_inicio = time.time()
    
    passo = 0
    while passo < num_passos:
        passo += 1
        
        t_inicio = time.time()
        grade = atualizar_paralelo(grade, prob_fogo, num_processos)
        t_decorrido = time.time() - t_inicio
        
        em_chamas, queimadas, arvores = contar_celulas(grade)
        
        # Mostrar cada 10 passos ou quando fogo acabar
        if passo % 10 == 0 or em_chamas == 0:
            print(f"Passo {passo:3d}: Árvores={arvores:8,} | Em chamas={em_chamas:8,} | Queimadas={queimadas:8,} | Tempo={t_decorrido*1000:6.1f}ms")
        
        # Parar se fogo acabou
        if em_chamas == 0:
            print(f"\nFogo extinto no passo {passo}!")
            break
    
    tempo_total = time.time() - tempo_total_inicio
    
    print(f"\n{'='*70}")
    print(f"RESULTADO FINAL:")
    print(f"Passos executados: {passo}")
    print(f"Tempo total: {tempo_total:.2f}s")
    print(f"Tempo por passo (média): {tempo_total/passo*1000:.1f}ms")
    print(f"Células queimadas: {queimadas:,} ({queimadas/(largura*altura)*100:.1f}%)")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    # Detectar núcleos disponíveis
    max_nucleos = cpu_count()
    print(f"\nSeu sistema tem {max_nucleos} núcleos disponíveis.")
    
    while True:
        try:
            num_proc = int(input(f"Quantos núcleos deseja usar (1-{max_nucleos})? "))
            if 1 <= num_proc <= max_nucleos:
                break
            else:
                print(f"Por favor, escolha entre 1 e {max_nucleos}.")
        except ValueError:
            print("Por favor, digite um número válido.")
    
    # Configuração
    LARGURA = 300
    ALTURA = 300
    DENSIDADE = 0.75
    PROB_FOGO = 0.35
    NUM_PASSOS = 100
    
    simular(LARGURA, ALTURA, DENSIDADE, PROB_FOGO, num_proc, NUM_PASSOS)
