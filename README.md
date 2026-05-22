# Simulação de Incêndio Florestal

Simulador de propagação de incêndio em grade 2D com foco em desempenho, incluindo:
- execução sequencial (NumPy),
- execução paralela com `multiprocessing` + `shared_memory`,
- interface gráfica local com Matplotlib,
- interface web com Streamlit.

## Objetivo do projeto

Modelar a propagação do fogo em uma floresta discretizada, comparando desempenho entre abordagens sequenciais e paralelas em grades grandes.

## Estrutura do projeto

- `floresta.py`: geração da grade inicial e ignição do fogo.
- `propagacao.py`: regras de atualização e kernels (NumPy e Numba opcional).
- `paralelo.py`: coordenação paralela com `Pool` e double buffering em memória compartilhada.
- `simulador_cli.py`: execução em terminal + benchmark.
- `main.py`: interface visual com Matplotlib (animação local).
- `front.py`: front web profissional com Streamlit.

## Requisitos

- Python 3.10+
- Dependências:
  - `numpy`
  - `matplotlib`
  - `streamlit`
  - `numba` (opcional, recomendado para acelerar kernel)

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install numpy matplotlib streamlit numba
```

## Como executar

### 1) Modo terminal (CLI)

```bash
python3 simulador_cli.py
```

O programa pergunta quantos núcleos usar e executa a simulação em modo paralelo por padrão.

### 2) Interface gráfica Matplotlib

```bash
python3 main.py
```

Abre uma janela com animação da grade e painel de status.


## Modelo da simulação

Estados por célula:
- `0`: vazio
- `1`: árvore
- `2`: fogo
- `3`: queimado

Dinâmica geral:
- célula em fogo vira queimada no próximo passo;
- árvore pode pegar fogo se houver vizinhos em combustão;
- probabilidade e fatores locais controlam intensidade da propagação.

## Arquitetura de paralelismo

- Shared memory (`multiprocessing.shared_memory`) para evitar cópia integral da grade entre processos.
- Double buffering real (`buffer A`/`buffer B`) alternado a cada passo.
- Divisão da grade em faixas de linhas por processo.
- Suporte a Numba no kernel quando disponível.

## Benchmark (10 núcleos)

Todos os testes abaixo foram executados com **10 núcleos** no modo paralelo.

| Grade | Células totais | Passos executados | Tempo total (s) | Tempo total (min) | Tempo médio por passo |
|---|---:|---:|---:|---:|---:|
| 1000 x 1000 | 1.000.000 | 1000 | 1,73s | 0,03 min | 1,7 ms |
| 5000 x 5000 | 25.000.000 | 5000 | 100,28s | 1,67 min | 20,1 ms |
| 7000 x 7000 | 49.000.000 | 7000 | 270,06s | 4,50 min | 38,6 ms |
| 10000 x 10000 | 100.000.000 | 10000 | 778,72s | 12,98 min | 77,9 ms |

## Gráficos de desempenho

### Tempo total por grade

![Tempo total por grade](assets/benchmark_tempo_total_10nucleos.png)

### Tempo médio por passo

![Tempo médio por passo](assets/benchmark_tempo_por_passo_10nucleos.png)

## Interpretação dos resultados

- O tempo cresce de forma consistente com o aumento da grade e dos passos.
- Em grades muito grandes, o custo de memória e sincronização fica dominante.
- Mesmo com 10 núcleos, simulações de 100 milhões de células podem levar vários minutos.

## Observações práticas

- Para demonstração rápida: `1000x1000`.
- Para testes intermediários: `5000x5000` ou `7000x7000`.
- Para carga alta: `10000x10000` com maior tempo de execução.

---

Projeto voltado a estudo de paralelismo, modelagem em grade e análise de desempenho computacional.
