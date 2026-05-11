# Simulação de Incêndio Florestal

Este repositório contém uma versão reescrita da simulação de propagação de fogo em uma grade 2D.

## Arquitetura

- `floresta.py`: geração de grade e ignição inicial.
- `propagacao.py`: kernel de atualização vetorizada e suporte a Numba quando disponível.
- `paralelo.py`: gerencia shared memory e pool de processos com double buffering real.
- `simulador_cli.py`: interface de linha de comando e benchmark comparativo.

## Principais melhorias

1. Shared memory `multiprocessing.shared_memory` para evitar a serialização da grade inteira.
2. Double buffering contínuo entre dois arrays compartilhados.
3. Processos filhos leem apenas blocos de linhas e usam vizinhança com halo correto.
4. Atualização vetorizada em NumPy como baseline de alto desempenho.
5. Suporte opcional a Numba para transformar o kernel em código compilado.
6. Benchmark integrado para comparar "Sequencial NumPy" e "Paralelo SharedMemory".

## Uso

- Para executar a simulação paralela:

```bash
python simulador_cli.py
```

- Para rodar benchmark:

```bash
python -c "from simulador_cli import benchmark; benchmark(300,300,0.75,0.35,20,[1,2,4])"
```

## Observação

No ambiente atual, o kernel vetorizado NumPy de um único processo é mais rápido do que o paralelismo por processo quando o código paralelo ainda não está acelerado por Numba. A arquitetura atual já está preparada para multi-core real; basta ativar Numba para maiores ganhos.
