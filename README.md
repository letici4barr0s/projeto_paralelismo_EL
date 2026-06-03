# Relatório da Atividade: Simulação Paralela de Incêndio Florestal

*Disciplina:* Programação Concorrente e Distribuída  
*Aluno(s):* Ellen e Letícia de Oliveira Barros  
*Turma:* Sistemas de Informação - 5º semestre  
*Professor:* Rafael Marconi  
*Data:* 08/04/2026  


# 1. Descrição do Problema

O projeto desenvolvido implementa uma simulação de propagação de incêndio florestal em uma grade bidimensional. A floresta é representada por uma matriz, na qual cada célula corresponde a uma pequena região do ambiente simulado. Cada posição da matriz pode assumir um estado diferente: vazio, árvore, fogo ou queimado.

O objetivo do programa é acompanhar a evolução do fogo ao longo de vários passos de simulação. A cada passo, o algoritmo verifica o estado atual das células e calcula o próximo estado da floresta. Uma árvore pode pegar fogo quando existe fogo em sua vizinhança, enquanto uma célula que estava em chamas passa para o estado de queimada. O código também inclui fatores de variação, como influência dos vizinhos, vento, terreno e aleatoriedade local, tornando a propagação menos uniforme.

Esse problema possui relação direta com situações reais. Em um país como o Brasil, onde existem grandes áreas de vegetação na Amazônia, no Cerrado, no Pantanal e em outras regiões, simulações desse tipo podem auxiliar estudos sobre comportamento do fogo, risco ambiental e planejamento de combate a incêndios. Embora o programa seja uma simplificação, ele demonstra como modelos computacionais podem representar fenômenos naturais e apoiar análises em larga escala.

A paralelização foi utilizada porque o volume de dados processado é muito grande. Foram testadas grades de `7000 x 7000` e `10000 x 10000`, o que corresponde, respectivamente, a 49.000.000 e 100.000.000 de células. Como cada passo da simulação precisa analisar a matriz, o custo computacional cresce rapidamente.

O algoritmo utilizado é uma simulação baseada em grade com atualização iterativa por vizinhança. A complexidade aproximada é:

```text
O(P * H * W)
```

Onde:

- `P` representa o número de passos executados;
- `H` representa a altura da matriz;
- `W` representa a largura da matriz.

Na versão paralela, a matriz é dividida em faixas de linhas. Cada processo atualiza uma parte da floresta, e a comunicação ocorre por meio de memória compartilhada. O objetivo é diminuir o tempo total de execução quando comparado à versão serial.

---

# 2. Ambiente Experimental

Os experimentos foram realizados em um MacBook Air com 16 GB de memória RAM. O projeto foi implementado em Python, utilizando NumPy para manipulação das matrizes e `multiprocessing` com `shared_memory` para a execução paralela.

| Item | Descrição |
| --- | --- |
| Computador | MacBook Air |
| Memória RAM | 16 GB |
| Sistema Operacional | macOS |
| Linguagem utilizada | Python |
| Biblioteca de paralelização | `multiprocessing` + `shared_memory` |
| Bibliotecas auxiliares | NumPy, Matplotlib e Streamlit |
| Configurações testadas | Serial, 2, 4, 8 e 10 processos |

Observação: o termo "serial" representa a execução sem paralelização e corresponde ao tempo base `T(1)` utilizado no cálculo de speedup.

---

# 3. Metodologia de Testes

O tempo de execução foi medido pela própria aplicação utilizando a função `time.perf_counter()` da linguagem Python. Ao final da simulação, o programa exibiu o número de passos executados, o tempo total, o tempo médio por passo e a quantidade de células queimadas.

Foram utilizadas duas entradas principais:

- `7000 x 7000`, com 49.000.000 células e 7000 passos;
- `10000 x 10000`, com 100.000.000 células e 10000 passos.

Para cada tamanho de entrada, foram comparadas execuções em modo serial e em modo paralelo. No modo paralelo, foram testadas configurações com 2, 4, 8 e 10 processos. Para a grade `10000 x 10000`, o teste com 10 processos ainda não foi executado.

Como os valores disponíveis correspondem aos tempos obtidos nas execuções registradas, as tabelas apresentam o tempo medido em cada configuração. O tempo médio por passo é calculado pelo programa dividindo o tempo total pelo número de passos executados.

---

# 4. Resultados Experimentais

## 4.1 Entrada 7000 x 7000

Nesta entrada, a simulação processou 49.000.000 células durante 7000 passos. Ao final, 100% da floresta foi queimada.

| Configuração | Processos | Tempo total (s) | Tempo médio por passo |
| --- | ---: | ---: | ---: |
| Serial | 1 | 590.73 | 84.4 ms |
| Paralelo | 2 | 435.02 | 62.1 ms |
| Paralelo | 4 | 309.28 | 44.2 ms |
| Paralelo | 8 | 276.49 | 39.5 ms |
| Paralelo | 10 | 268.91 | 38.4 ms |

## 4.2 Entrada 10000 x 10000

Nesta entrada, a simulação processou 100.000.000 células durante 10000 passos. Ao final, 100% da floresta foi queimada.

| Configuração | Processos | Tempo total (s) | Tempo médio por passo |
| --- | ---: | ---: | ---: |
| Serial | 1 | 1777.82 | 177.8 ms |
| Paralelo | 2 | 1406.39 | 140.6 ms |
| Paralelo | 4 | 915.21 | 91.5 ms |
| Paralelo | 8 | 826.33 | 82.6 ms |
| Paralelo | 10 | A executar | A executar |

---

# 5. Tabela de Resultados e Cálculos

O speedup mede quantas vezes a execução paralela foi mais rápida que a execução serial. A eficiência mede o aproveitamento dos processos utilizados.

```text
Speedup(p) = T(1) / T(p)
Eficiência(p) = Speedup(p) / p
```

Onde:

- `T(1)` é o tempo da execução serial;
- `T(p)` é o tempo com `p` processos;
- `p` é o número de processos utilizados.

## 5.1 Entrada 7000 x 7000

| Configuração | Processos | Tempo (s) | Speedup | Eficiência |
| --- | ---: | ---: | ---: | ---: |
| Serial | 1 | 590.73 | 1.00 | 1.00 |
| Paralelo | 2 | 435.02 | 1.36 | 0.68 |
| Paralelo | 4 | 309.28 | 1.91 | 0.48 |
| Paralelo | 8 | 276.49 | 2.14 | 0.27 |
| Paralelo | 10 | 268.91 | 2.20 | 0.22 |

### Memorial de cálculo - 7000 x 7000

Tempo serial utilizado como base:

```text
T(1) = 590.73 s
```

Cálculos:

```text
Speedup(1) = 590.73 / 590.73 = 1.00
Eficiência(1) = 1.00 / 1 = 1.00

Speedup(2) = 590.73 / 435.02 = 1.36
Eficiência(2) = 1.36 / 2 = 0.68

Speedup(4) = 590.73 / 309.28 = 1.91
Eficiência(4) = 1.91 / 4 = 0.48

Speedup(8) = 590.73 / 276.49 = 2.14
Eficiência(8) = 2.14 / 8 = 0.27

Speedup(10) = 590.73 / 268.91 = 2.20
Eficiência(10) = 2.20 / 10 = 0.22
```

## 5.2 Entrada 10000 x 10000

| Configuração | Processos | Tempo (s) | Speedup | Eficiência |
| --- | ---: | ---: | ---: | ---: |
| Serial | 1 | 1777.82 | 1.00 | 1.00 |
| Paralelo | 2 | 1406.39 | 1.26 | 0.63 |
| Paralelo | 4 | 915.21 | 1.94 | 0.49 |
| Paralelo | 8 | 826.33 | 2.15 | 0.27 |
| Paralelo | 10 | A executar | A executar | A executar |

### Memorial de cálculo - 10000 x 10000

Tempo serial utilizado como base:

```text
T(1) = 1777.82 s
```

Cálculos:

```text
Speedup(1) = 1777.82 / 1777.82 = 1.00
Eficiência(1) = 1.00 / 1 = 1.00

Speedup(2) = 1777.82 / 1406.39 = 1.26
Eficiência(2) = 1.26 / 2 = 0.63

Speedup(4) = 1777.82 / 915.21 = 1.94
Eficiência(4) = 1.94 / 4 = 0.49

Speedup(8) = 1777.82 / 826.33 = 2.15
Eficiência(8) = 2.15 / 8 = 0.27
```

O cálculo para 10 processos na entrada `10000 x 10000` ainda não foi realizado porque o tempo dessa execução não foi medido.

---

# 6. Gráfico de Tempo de Execução

O gráfico abaixo mostra o tempo total de execução em função do número de processos. Observa-se que o aumento no número de processos reduz o tempo total, mas a redução fica menor conforme mais processos são adicionados.

![Gráfico de tempo de execução](grafico_tempo_execucao.png)

---

# 7. Gráfico de Speedup

O gráfico abaixo mostra o speedup obtido em comparação com a execução serial. A linha ideal representa o crescimento linear esperado em uma paralelização perfeita.

![Gráfico de speedup](grafico_speedup.png)

---

# 8. Gráfico de Eficiência

O gráfico abaixo mostra a eficiência da paralelização. A eficiência diminui conforme o número de processos aumenta, indicando que nem todo o poder de processamento adicional é aproveitado integralmente.

![Gráfico de eficiência](grafico_eficiencia.png)

---

# 9. Análise dos Resultados

Os resultados indicam que a paralelização trouxe ganho de desempenho nas duas entradas testadas. Para a grade `7000 x 7000`, o tempo caiu de 590.73 segundos na execução serial para 268.91 segundos com 10 processos. Isso representa um speedup de 2.20.

Para a grade `10000 x 10000`, o tempo caiu de 1777.82 segundos na execução serial para 826.33 segundos com 8 processos. Nesse caso, o speedup foi de 2.15. O teste com 10 processos ainda precisa ser executado para completar a comparação dessa entrada.

Apesar da redução no tempo total, o speedup obtido ficou abaixo do ideal. Em uma paralelização perfeita, 8 processos poderiam se aproximar de um speedup 8, e 10 processos poderiam se aproximar de um speedup 10. No entanto, os valores obtidos ficaram em torno de 2.15 e 2.20. Isso mostra que existem limitações no algoritmo e no ambiente de execução.

A eficiência também caiu conforme o número de processos aumentou. Na entrada `7000 x 7000`, a eficiência foi de 0.68 com 2 processos, mas caiu para 0.22 com 10 processos. Na entrada `10000 x 10000`, a eficiência foi de 0.63 com 2 processos e caiu para 0.27 com 8 processos.

Essa queda de eficiência pode ser explicada por fatores como:

- custo de criação e gerenciamento dos processos;
- sincronização necessária a cada passo da simulação;
- acesso intenso à memória compartilhada;
- leitura e escrita em matrizes muito grandes;
- divisão da grade em faixas de linhas;
- partes do algoritmo que não se beneficiam totalmente da paralelização;
- overhead causado pela coordenação entre os processos.

Mesmo assim, a paralelização foi útil, pois reduziu significativamente o tempo total de execução em entradas grandes. Esse resultado é importante porque simulações ambientais com milhões de células exigem alto poder computacional. Em cenários reais, como o estudo de incêndios em florestas brasileiras, a capacidade de processar grandes áreas pode ajudar na análise de risco e no planejamento de ações preventivas.

---

# 10. Conclusão

O projeto implementou uma simulação de incêndio florestal em grade bidimensional, comparando a execução serial com a execução paralela. A solução utiliza Python, NumPy e `multiprocessing` com memória compartilhada para dividir o processamento da matriz entre diferentes processos.

Os resultados mostraram que o paralelismo reduziu o tempo de execução, principalmente nas entradas maiores. Na grade `7000 x 7000`, o melhor resultado foi obtido com 10 processos, reduzindo o tempo para 268.91 segundos. Na grade `10000 x 10000`, o melhor resultado registrado até o momento foi com 8 processos, com tempo de 826.33 segundos.

Entretanto, o ganho não foi linear. A eficiência diminuiu conforme o número de processos aumentou, indicando que o desempenho ficou limitado pelo overhead de paralelização, pelo acesso à memória e pela própria estrutura do algoritmo.

Como melhorias futuras, podem ser realizadas:

- executar o teste faltante de `10000 x 10000` com 10 processos;
- repetir cada configuração mais de uma vez e calcular a média dos tempos;
- otimizar o balanceamento de carga entre processos;
- reduzir o custo de sincronização entre os passos;
- aprimorar o uso de memória compartilhada;
- testar otimizações com Numba ou outras abordagens de alto desempenho;
- executar a simulação em máquinas com maior quantidade de núcleos e memória RAM.

Conclui-se que a paralelização foi eficaz para melhorar o desempenho da simulação, mas apresentou limites práticos. O estudo demonstra a importância do paralelismo para problemas computacionais de grande escala e mostra como esse tipo de técnica pode ser aplicado em simulações relacionadas a problemas ambientais reais.
