import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
import time
from multiprocessing import freeze_support, cpu_count

from floresta import criar_floresta, VAZIO, ARVORE, FOGO, QUEIMADO
from paralelo import atualizar_paralelo

# ── Configurações ──────────────────────────────────────────────
LARGURA    = 1000   # Para teste rápido use 1000; para full use 10000
ALTURA     = 1000
DENSIDADE  = 0.75    # 75% de cobertura florestal
PROB_FOGO  = 0.35    # Probabilidade de um vizinho pegar fogo
N_PROC     = None    # None = perguntar ao usuário
VISUALIZACAO_PASSOS = 20  # Atualizar visualização a cada 20 passos

# Perguntar núcleos se N_PROC é None
if N_PROC is None:
    max_nucleos = cpu_count()
    print(f"Seu sistema tem {max_nucleos} núcleos disponíveis.")
    while True:
        try:
            N_PROC = int(input(f"Quantos núcleos deseja usar (1-{max_nucleos})? "))
            if 1 <= N_PROC <= max_nucleos:
                break
            else:
                print(f"Por favor, escolha entre 1 e {max_nucleos}.")
        except ValueError:
            print("Por favor, digite um número válido.")

# ── Mapa de cores ──────────────────────────────────────────────
CMAP = plt.cm.colors.ListedColormap(['#111111','#2d7a2d','#e85c1b','#666666'])

# ── Mapa de cores ──────────────────────────────────────────────
CMAP = plt.cm.colors.ListedColormap(['#111111','#2d7a2d','#e85c1b','#666666'])

class SimuladorIncendio:
    def __init__(self):
        self.grade = criar_floresta(LARGURA, ALTURA, DENSIDADE)
        self.rodando = False
        self.passo = 0
        self.tempo_inicio = None
        self.ani = None

        self._montar_interface()

    def _montar_interface(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 9))
        self.fig.patch.set_facecolor('#1a1a1a')
        self.ax.set_facecolor('#1a1a1a')
        plt.subplots_adjust(bottom=0.18)

        self.imagem = self.ax.imshow(
            self.grade, cmap=CMAP, vmin=0, vmax=3,
            interpolation='nearest'
        )
        self.ax.set_title('Propagação de Incêndio Florestal',
                          color='white', fontsize=14, pad=10)
        self.ax.axis('off')

        # Legenda
        from matplotlib.patches import Patch
        legenda = [
            Patch(facecolor='#111111', label='Vazio'),
            Patch(facecolor='#2d7a2d', label='Árvore'),
            Patch(facecolor='#e85c1b', label='Em chamas'),
            Patch(facecolor='#666666', label='Queimado'),
        ]
        self.ax.legend(handles=legenda, loc='lower right',
                       facecolor='#2a2a2a', edgecolor='#444',
                       labelcolor='white', fontsize=9)

        # Texto de status
        self.texto_status = self.fig.text(
            0.5, 0.13, 'Pressione INICIAR para começar',
            ha='center', color='#aaaaaa', fontsize=11
        )

        # Botão Iniciar/Pausar
        ax_btn = plt.axes([0.35, 0.04, 0.15, 0.06])
        self.btn_iniciar = Button(ax_btn, 'INICIAR',
                                  color='#2d6a2d', hovercolor='#3a8a3a')
        self.btn_iniciar.label.set_color('white')
        self.btn_iniciar.label.set_fontsize(11)
        self.btn_iniciar.on_clicked(self._toggle)

        # Botão Reset
        ax_rst = plt.axes([0.52, 0.04, 0.13, 0.06])
        self.btn_reset = Button(ax_rst, 'RESET',
                                color='#6a2d2d', hovercolor='#8a3a3a')
        self.btn_reset.label.set_color('white')
        self.btn_reset.label.set_fontsize(11)
        self.btn_reset.on_clicked(self._reset)

    def _toggle(self, evento):
        if not self.rodando:
            self.rodando = True
            self.tempo_inicio = time.time()
            self.btn_iniciar.label.set_text('PAUSAR')
            self.ani = animation.FuncAnimation(
                self.fig, self._atualizar,
                interval=50, cache_frame_data=False
            )
            self.fig.canvas.draw()
        else:
            self.rodando = False
            self.btn_iniciar.label.set_text('CONTINUAR')
            if self.ani:
                self.ani.event_source.stop()

    def _reset(self, evento):
        self.rodando = False
        if self.ani:
            self.ani.event_source.stop()
        self.grade = criar_floresta(LARGURA, ALTURA, DENSIDADE)
        self.passo = 0
        self.tempo_inicio = None
        self.imagem.set_data(self.grade)
        self.texto_status.set_text('Pressione INICIAR para começar')
        self.btn_iniciar.label.set_text('INICIAR')
        self.fig.canvas.draw()

    def _atualizar(self, frame):
        if not self.rodando:
            return

        t0 = time.time()
        self.grade = atualizar_paralelo(self.grade, PROB_FOGO, N_PROC)
        t1 = time.time()

        self.passo += 1
        elapsed = time.time() - self.tempo_inicio
        em_chamas = np.sum(self.grade == FOGO)
        queimadas = np.sum(self.grade == QUEIMADO)

        # Atualizar visualização apenas a cada VISUALIZACAO_PASSOS passos
        if self.passo % VISUALIZACAO_PASSOS == 0:
            self.imagem.set_data(self.grade)
            self.texto_status.set_text(
                f'⏱ {elapsed:.1f}s  |  Passo: {self.passo}  |  '
                f'🔥 {em_chamas:,}  |  ⬛ {queimadas:,}  |  '
                f'Δt: {(t1-t0)*1000:.0f}ms'
            )
        else:
            # Atualizar apenas texto
            self.texto_status.set_text(
                f'⏱ {elapsed:.1f}s  |  Passo: {self.passo}  |  '
                f'🔥 {em_chamas:,}  |  ⬛ {queimadas:,}  |  '
                f'Δt: {(t1-t0)*1000:.0f}ms'
            )

        if em_chamas == 0:
            self.rodando = False
            self.btn_iniciar.label.set_text('CONCLUÍDO')
            self.texto_status.set_text(
                f'✅ Fogo extinto em {elapsed:.1f}s | '
                f'{queimadas:,} células queimadas'
            )

        return [self.imagem]

    def iniciar(self):
        plt.show()


if __name__ == '__main__':
    freeze_support()   # necessário no Windows
    sim = SimuladorIncendio()
    sim.iniciar()