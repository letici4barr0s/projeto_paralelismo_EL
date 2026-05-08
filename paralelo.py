from multiprocessing import Pool
import numpy as np
from propagacao import processar_faixa


def atualizar_paralelo(grade, probabilidade, num_processos):
    """
    Divide a grade em faixas horizontais e
    processa em paralelo usando multiprocessing.
    """

    altura = grade.shape[0]

    # Tamanho de cada faixa
    tamanho_faixa = altura // num_processos

    tarefas = []

    for i in range(num_processos):
        y_inicio = i * tamanho_faixa

        # Último processo pega o restante
        if i == num_processos - 1:
            y_fim = altura
        else:
            y_fim = (i + 1) * tamanho_faixa

        tarefas.append(
            (grade, y_inicio, y_fim, probabilidade)
        )

    # Executa em paralelo
    with Pool(processes=num_processos) as pool:
        resultados = pool.map(processar_faixa, tarefas)

    # Junta as faixas processadas
    nova_grade = grade.copy()

    for y_inicio, y_fim, faixa in resultados:
        nova_grade[y_inicio:y_fim, :] = faixa

    return nova_grade