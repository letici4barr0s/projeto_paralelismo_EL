import time
from multiprocessing import cpu_count
import numpy as np

from floresta import criar_floresta, ARVORE, FOGO, QUEIMADO
from propagacao import atualizar_sequencial
from paralelo import SimuladorParalelo


def contar_celulas(grade):
    """Conta células por estado."""
    em_chamas = np.sum(grade == FOGO)
    queimadas = np.sum(grade == QUEIMADO)
    arvores = np.sum(grade == ARVORE)
    return em_chamas, queimadas, arvores


def simular(largura, altura, densidade, prob_fogo, num_processos, num_passos=100, modo="paralelo"):
    """Executa a simulação em modo console com núcleo único ou paralelo."""
    if modo not in ("paralelo", "sequencial"):
        raise ValueError("modo deve ser 'paralelo' ou 'sequencial'")

    print(f"\n{'='*70}")
    print("SIMULADOR DE INCÊNDIO FLORESTAL - MODO CONSOLE")
    print(f"{'='*70}")
    print(f"Grade: {largura}x{altura} = {largura*altura:,} células")
    print(f"Densidade florestal: {densidade*100:.0f}%")
    print(f"Modo: {modo}")
    print(f"Processos paralelos: {num_processos}")
    print(f"Passos: {num_passos}")
    print(f"{'='*70}\n")

    grade = criar_floresta(largura, altura, densidade)
    em_chamas, queimadas, arvores = contar_celulas(grade)
    print(f"INICIAL: Árvores={arvores:,} | Em chamas={em_chamas:,} | Queimadas={queimadas:,}\n")

    tempo_total_inicio = time.perf_counter()

    if modo == "paralelo":
        with SimuladorParalelo(grade, num_processos=num_processos) as simulador:
            for passo in range(1, num_passos + 1):
                t_inicio = time.perf_counter()
                simulador.step(prob_fogo)
                t_decorrido = time.perf_counter() - t_inicio

                grade = simulador.current_grid(copy=False)
                em_chamas, queimadas, arvores = contar_celulas(grade)
                if passo % 10 == 0 or em_chamas == 0:
                    print(
                        f"Passo {passo:3d}: Árvores={arvores:8,} | Em chamas={em_chamas:8,} | Queimadas={queimadas:8,} | Tempo={t_decorrido*1000:6.1f}ms"
                    )
                if em_chamas == 0:
                    print(f"\nFogo extinto no passo {passo}!")
                    break
    else:
        for passo in range(1, num_passos + 1):
            t_inicio = time.perf_counter()
            grade = atualizar_sequencial(grade, prob_fogo)
            t_decorrido = time.perf_counter() - t_inicio

            em_chamas, queimadas, arvores = contar_celulas(grade)
            if passo % 10 == 0 or em_chamas == 0:
                print(
                    f"Passo {passo:3d}: Árvores={arvores:8,} | Em chamas={em_chamas:8,} | Queimadas={queimadas:8,} | Tempo={t_decorrido*1000:6.1f}ms"
                )
            if em_chamas == 0:
                print(f"\nFogo extinto no passo {passo}!")
                break

    tempo_total = time.perf_counter() - tempo_total_inicio
    print(f"\n{'='*70}")
    print("RESULTADO FINAL:")
    print(f"Passos executados: {passo}")
    print(f"Tempo total: {tempo_total:.2f}s")
    print(f"Tempo por passo (média): {tempo_total/passo*1000:.1f}ms")
    print(f"Células queimadas: {queimadas:,} ({queimadas/(largura*altura)*100:.1f}%)")
    print(f"{'='*70}\n")


def benchmark(largura, altura, densidade, prob_fogo, num_passos, num_processos_list):
    """Executa benchmarks comparativos de sequência e paralelismo compartilhado."""
    print(f"\n{'='*70}")
    print("BENCHMARK DE DESEMPENHO")
    print(f"Grade: {largura}x{altura} = {largura*altura:,} células")
    print(f"Densidade: {densidade*100:.0f}% | Probabilidade: {prob_fogo}")
    print(f"Passos por experimento: {num_passos}")
    print(f"{'='*70}\n")

    grade_base = criar_floresta(largura, altura, densidade, semente=42)

    print("Modo               | Núcleos | Tempo total | Tempo/passo | Observação")
    print("-------------------|---------|-------------|-------------|-----------")

    grade = grade_base.copy()
    t0 = time.perf_counter()
    for _ in range(num_passos):
        grade = atualizar_sequencial(grade, prob_fogo)
    t_seq = time.perf_counter() - t0
    print(f"Sequencial NumPy   | 1       | {t_seq:10.3f}s | {t_seq/num_passos:11.3f}s | Vetorizado")

    for num_processos in num_processos_list:
        grade = grade_base.copy()
        with SimuladorParalelo(grade, num_processos=num_processos) as simulador:
            t0 = time.perf_counter()
            for _ in range(num_passos):
                simulador.step(prob_fogo)
            t_par = time.perf_counter() - t0
        print(
            f"Paralelo SM       | {num_processos:<7} | {t_par:10.3f}s | {t_par/num_passos:11.3f}s | SharedMemory"
        )

    print(f"{'='*70}\n")


if __name__ == "__main__":
    max_nucleos = cpu_count()
    print(f"\nSeu sistema tem {max_nucleos} núcleos disponíveis.")

    while True:
        try:
            num_proc = int(input(f"Quantos núcleos deseja usar (1-{max_nucleos})? "))
            if 1 <= num_proc <= max_nucleos:
                break
            print(f"Por favor, escolha entre 1 e {max_nucleos}.")
        except ValueError:
            print("Por favor, digite um número válido.")

    LARGURA = 300
    ALTURA = 300
    DENSIDADE = 0.75
    PROB_FOGO = 0.35
    NUM_PASSOS = 100

    simular(LARGURA, ALTURA, DENSIDADE, PROB_FOGO, num_proc, NUM_PASSOS, modo="paralelo")
