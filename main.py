import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
import time
from multiprocessing import freeze_support, cpu_count

from floresta import criar_floresta, FOGO, QUEIMADO

from paralelo import SimuladorParalelo

# ================= CONFIGURAÇÕES =================

LARGURA = 300
ALTURA = 300

DENSIDADE = 0.75
PROB_FOGO = 0.35

# Quantos passos executar antes de redesenhar
VISUALIZACAO_PASSOS = 3

# Intervalo da animação (ms)
INTERVALO_ANIMACAO = 120

# ================= ESCOLHER NÚCLEOS =================

max_nucleos = cpu_count()

N_PROC = min(4, max_nucleos)  # Usar 4 por padrão, ou menos se disponível

# ================= CORES =================

CMAP = plt.cm.colors.ListedColormap([
    '#111111',  # vazio
    '#2d7a2d',  # árvore
    '#e85c1b',  # fogo
    '#666666'   # queimado
])


class SimuladorIncendio:

    def __init__(self):

        # Cria floresta inicial
        self.grade = criar_floresta(
            LARGURA,
            ALTURA,
            DENSIDADE
        )

        self.rodando = False
        self.passo = 0
        self.tempo_inicio = None

        # Inicializa simulador paralelo
        self.simulador_paralelo = SimuladorParalelo(self.grade, N_PROC)

        # Monta interface
        self._montar_interface()

    # ==================================================

    def _montar_interface(self):

        self.fig, self.ax = plt.subplots(
            figsize=(9, 8)
        )

        # Espaço para botão e texto
        plt.subplots_adjust(
            top=0.88,
            bottom=0.12
        )

        # Imagem principal
        self.imagem = self.ax.imshow(
            self.grade,
            cmap=CMAP,
            vmin=0,
            vmax=3,
            interpolation='nearest'
        )

        # Título
        self.ax.set_title(
            'Simulação de Incêndio Florestal',
            fontsize=16,
            pad=15
        )

        self.ax.axis('off')

        # Texto inferior
        self.texto_status = self.fig.text(
            0.5,
            0.04,
            'Pressione INICIAR',
            ha='center',
            fontsize=11
        )

        # ================= BOTÃO =================

        ax_btn = plt.axes([
            0.40,  # esquerda
            0.91,  # altura
            0.20,  # largura
            0.05   # altura
        ])

        self.btn = Button(
            ax_btn,
            'INICIAR',
            color='#2d7a2d',
            hovercolor='#3fa33f'
        )

        self.btn.label.set_color('white')
        self.btn.label.set_fontsize(12)

        self.btn.on_clicked(self._iniciar)

    # ==================================================

    def _iniciar(self, evento):

        if self.rodando:
            return

        self.rodando = True

        self.tempo_inicio = time.time()

        self.btn.label.set_text('EXECUTANDO')

        # IMPORTANTE:
        # manter referência salva
        self.animacao = animation.FuncAnimation(
            self.fig,
            self._atualizar,
            interval=INTERVALO_ANIMACAO,
            blit=False,
            cache_frame_data=False
        )

        plt.draw()

    # ==================================================

    def _atualizar(self, frame):

        if not self.rodando:
            return

        # Executa vários passos antes de redesenhar
        for _ in range(VISUALIZACAO_PASSOS):

            self.simulador_paralelo.step(PROB_FOGO)
            self.grade = self.simulador_paralelo.current_grid()

            self.passo += 1

        # Atualiza imagem
        self.imagem.set_data(self.grade)

        # Estatísticas
        em_chamas = np.sum(
            self.grade == FOGO
        )

        queimadas = np.sum(
            self.grade == QUEIMADO
        )

        # Atualiza texto
        self.texto_status.set_text(
            f'Passo: {self.passo}   |   '
            f'🔥 {em_chamas:,}   |   '
            f'⬛ {queimadas:,}'
        )

        # ================= FINALIZAÇÃO =================

        if em_chamas == 0:

            self.rodando = False

            tempo_total = (
                time.time() - self.tempo_inicio
            )

            self.btn.label.set_text(
                'FINALIZADO'
            )

            self.texto_status.set_text(
                f'✅ Concluído em '
                f'{tempo_total:.2f}s'
            )

            self.animacao.event_source.stop()

        return [self.imagem]

    # ==================================================

    def iniciar(self):

        plt.show()


# ======================================================
# EXECUÇÃO PRINCIPAL
# ======================================================

if __name__ == '__main__':

    freeze_support()

    simulador = SimuladorIncendio()

    try:

        simulador.iniciar()

    finally:

        simulador.simulador_paralelo.close()