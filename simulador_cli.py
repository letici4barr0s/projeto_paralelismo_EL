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


def simular(
    largura,
    altura,
    densidade,
    prob_fogo,
    num_processos,
    modo="paralelo"
):
    """
    Executa a simulação em modo console.
    A simulação termina apenas quando o fogo apagar.
    """

    if modo not in ("paralelo", "sequencial"):
        raise ValueError(
            "modo deve ser 'paralelo' ou 'sequencial'"
        )

    print(f"\n{'='*70}")
    print("SIMULADOR DE INCÊNDIO FLORESTAL - MODO CONSOLE")
    print(f"{'='*70}")
    print(
        f"Grade: {largura}x{altura} = "
        f"{largura*altura:,} células"
    )
    print(
        f"Densidade florestal: "
        f"{densidade*100:.0f}%"
    )
    print(f"Modo: {modo}")
    print(f"Processos paralelos: {num_processos}")
    print(f"{'='*70}\n")

    # ==========================================
    # CRIA FLORESTA
    # ==========================================

    grade = criar_floresta(
        largura,
        altura,
        densidade
    )

    em_chamas, queimadas, arvores = contar_celulas(grade)

    print(
        f"INICIAL: "
        f"Árvores={arvores:,} | "
        f"Em chamas={em_chamas:,} | "
        f"Queimadas={queimadas:,}\n"
    )

    tempo_total_inicio = time.perf_counter()

    # ======================================================
    # MODO PARALELO
    # ======================================================

    if modo == "paralelo":

        with SimuladorParalelo(
            grade,
            num_processos=num_processos
        ) as simulador:

            passo = 0

            while True:

                passo += 1

                t_inicio = time.perf_counter()

                simulador.step(prob_fogo)

                t_decorrido = (
                    time.perf_counter() - t_inicio
                )

                grade = simulador.current_grid(
                    copy=False
                )

                em_chamas, queimadas, arvores = (
                    contar_celulas(grade)
                )

                # imprime progresso
                if passo % 5 == 0 or em_chamas == 0:

                    print(
                        f"Passo {passo:4d}: "
                        f"Árvores={arvores:10,} | "
                        f"Em chamas={em_chamas:10,} | "
                        f"Queimadas={queimadas:10,} | "
                        f"Tempo={t_decorrido*1000:7.1f}ms"
                    )

                # fogo acabou
                if em_chamas == 0:

                    print(
                        f"\nFogo extinto "
                        f"no passo {passo}!"
                    )

                    break

    # ======================================================
    # MODO SEQUENCIAL
    # ======================================================

    else:

        passo = 0

        while True:

            passo += 1

            t_inicio = time.perf_counter()

            grade = atualizar_sequencial(
                grade,
                prob_fogo
            )

            t_decorrido = (
                time.perf_counter() - t_inicio
            )

            em_chamas, queimadas, arvores = (
                contar_celulas(grade)
            )

            if passo % 5 == 0 or em_chamas == 0:

                print(
                    f"Passo {passo:4d}: "
                    f"Árvores={arvores:10,} | "
                    f"Em chamas={em_chamas:10,} | "
                    f"Queimadas={queimadas:10,} | "
                    f"Tempo={t_decorrido*1000:7.1f}ms"
                )

            if em_chamas == 0:

                print(
                    f"\nFogo extinto "
                    f"no passo {passo}!"
                )

                break

    # ======================================================
    # RESULTADO FINAL
    # ======================================================

    tempo_total = (
        time.perf_counter() - tempo_total_inicio
    )

    print(f"\n{'='*70}")
    print("RESULTADO FINAL:")
    print(f"Passos executados: {passo}")
    print(f"Tempo total: {tempo_total:.2f}s")

    print(
        f"Tempo médio por passo: "
        f"{tempo_total/passo*1000:.1f}ms"
    )

    print(
        f"Células queimadas: "
        f"{queimadas:,} "
        f"({queimadas/(largura*altura)*100:.1f}%)"
    )

    # verifica se queimou tudo
    if arvores == 0:

        print(
            "Toda a floresta foi destruída."
        )

    else:

        print(
            f"Restaram {arvores:,} "
            f"árvores intactas."
        )

    print(f"{'='*70}\n")


# ==========================================================
# BENCHMARK
# ==========================================================

def benchmark(
    largura,
    altura,
    densidade,
    prob_fogo,
    num_passos,
    num_processos_list
):
    """
    Benchmark comparando
    sequencial vs paralelo.
    """

    print(f"\n{'='*70}")
    print("BENCHMARK DE DESEMPENHO")
    print(
        f"Grade: {largura}x{altura} = "
        f"{largura*altura:,} células"
    )

    print(
        f"Densidade: {densidade*100:.0f}% "
        f"| Probabilidade: {prob_fogo}"
    )

    print(
        f"Passos por experimento: "
        f"{num_passos}"
    )

    print(f"{'='*70}\n")

    grade_base = criar_floresta(
        largura,
        altura,
        densidade,
        semente=42
    )

    print(
        "Modo               | "
        "Núcleos | "
        "Tempo total | "
        "Tempo/passo | "
        "Observação"
    )

    print(
        "-------------------|"
        "---------|"
        "-------------|"
        "-------------|"
        "-----------"
    )

    # ==========================================
    # SEQUENCIAL
    # ==========================================

    grade = grade_base.copy()

    t0 = time.perf_counter()

    for _ in range(num_passos):

        grade = atualizar_sequencial(
            grade,
            prob_fogo
        )

    t_seq = time.perf_counter() - t0

    print(
        f"Sequencial NumPy   | "
        f"1       | "
        f"{t_seq:10.3f}s | "
        f"{t_seq/num_passos:11.3f}s | "
        f"Vetorizado"
    )

    # ==========================================
    # PARALELO
    # ==========================================

    for num_processos in num_processos_list:

        grade = grade_base.copy()

        with SimuladorParalelo(
            grade,
            num_processos=num_processos
        ) as simulador:

            t0 = time.perf_counter()

            for _ in range(num_passos):

                simulador.step(prob_fogo)

            t_par = (
                time.perf_counter() - t0
            )

        speedup = t_seq / t_par

        print(
            f"Paralelo SM       | "
            f"{num_processos:<7} | "
            f"{t_par:10.3f}s | "
            f"{t_par/num_passos:11.3f}s | "
            f"Speedup={speedup:.2f}x"
        )

    print(f"{'='*70}\n")


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    max_nucleos = cpu_count()

    print(
        f"\nSeu sistema tem "
        f"{max_nucleos} núcleos disponíveis."
    )

    while True:

        try:

            num_proc = int(
                input(
                    f"Quantos núcleos deseja usar "
                    f"(1-{max_nucleos})? "
                )
            )

            if 1 <= num_proc <= max_nucleos:
                break

            print(
                f"Por favor, escolha "
                f"entre 1 e {max_nucleos}."
            )

        except ValueError:

            print(
                "Por favor, digite "
                "um número válido."
            )

    # ==========================================
    # CONFIGURAÇÕES
    # ==========================================

    LARGURA = 1000
    ALTURA = 1000

    DENSIDADE = 1.0

    PROB_FOGO = 1.0

    # ==========================================
    # EXECUÇÃO
    # ==========================================

    simular(
        LARGURA,
        ALTURA,
        DENSIDADE,
        PROB_FOGO,
        num_proc,
        modo="paralelo"
    )