# FireGuard - Simulação de Incêndio Florestal

Projeto de simulação da propagação de incêndio florestal com interface interativa e comparação de desempenho entre execução sequencial e paralela (MPI).

## Objetivo

Este projeto modela uma floresta em uma grade 2D, onde cada célula pode estar em um dos estados:

- `0` Vazio
- `1` Árvore
- `2` Em chamas
- `3` Queimado

A cada passo da simulação, o fogo pode se propagar para árvores vizinhas com base em uma probabilidade configurável.

---

## Estrutura do projeto

```text
simulacao_incendio/
├─ backend/
│  ├─ simulador.py
│  └─ simulador_mpi.py
├─ frontend/
│  ├─ app.py
│  └─ logo_fireguard.svg
├─ benchmark.py
├─ requirements.txt
└─ resultado_benchmark.txt (opcional)
