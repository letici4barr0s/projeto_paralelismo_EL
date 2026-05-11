import numpy as np
from multiprocessing import Pool, cpu_count, shared_memory
from propagacao import (
    _atualizar_faixa_numpy,
    _atualizar_faixa_numba,
    NUMBA_AVAILABLE,
)

_worker_a = None
_worker_b = None
_shm_a = None
_shm_b = None


def _worker_init(name_a, name_b, altura, largura):
    global _worker_a, _worker_b, _shm_a, _shm_b
    _shm_a = shared_memory.SharedMemory(name=name_a)
    _shm_b = shared_memory.SharedMemory(name=name_b)
    _worker_a = np.ndarray((altura, largura), dtype=np.uint8, buffer=_shm_a.buf)
    _worker_b = np.ndarray((altura, largura), dtype=np.uint8, buffer=_shm_b.buf)


def _processar_faixa(args):
    y0, y1, probabilidade, buffer_id = args
    source = _worker_a if buffer_id == 0 else _worker_b
    dest = _worker_b if buffer_id == 0 else _worker_a

    if NUMBA_AVAILABLE:
        _atualizar_faixa_numba(source, dest, y0, y1, probabilidade)
    else:
        _atualizar_faixa_numpy(source, dest, y0, y1, probabilidade)


class SimuladorParalelo:
    def __init__(self, grade, num_processos=None):
        altura, largura = grade.shape
        self.altura = altura
        self.largura = largura
        self.num_processos = min(cpu_count(), altura, num_processos or cpu_count())

        self._shm_a = shared_memory.SharedMemory(create=True, size=altura * largura)
        self._shm_b = shared_memory.SharedMemory(create=True, size=altura * largura)
        self._grid_a = np.ndarray((altura, largura), dtype=np.uint8, buffer=self._shm_a.buf)
        self._grid_b = np.ndarray((altura, largura), dtype=np.uint8, buffer=self._shm_b.buf)
        self._grid_a[:] = grade
        self._grid_b.fill(0)
        self._current_buffer = 0

        self._pool = Pool(
            processes=self.num_processos,
            initializer=_worker_init,
            initargs=(self._shm_a.name, self._shm_b.name, altura, largura),
        )

    def step(self, probabilidade):
        tarefas = []
        altura = self.altura
        fatia = altura // self.num_processos

        for i in range(self.num_processos):
            y0 = i * fatia
            y1 = altura if i == self.num_processos - 1 else (i + 1) * fatia
            tarefas.append((y0, y1, probabilidade, self._current_buffer))

        self._pool.map(_processar_faixa, tarefas)
        self._current_buffer ^= 1

    def current_grid(self, copy=False):
        grid = self._grid_a if self._current_buffer == 0 else self._grid_b
        return grid.copy() if copy else grid

    def close(self):
        if self._pool is not None:
            self._pool.close()
            self._pool.join()
            self._pool = None

        for shm in (self._shm_a, self._shm_b):
            try:
                shm.close()
            except Exception:
                pass
            try:
                shm.unlink()
            except Exception:
                pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

