import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from matplotlib.widgets import Button
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Patch

import time

from multiprocessing import freeze_support, cpu_count

from floresta import criar_floresta,ARVORE, FOGO, QUEIMADO
from paralelo import SimuladorParalelo


# ================= CONFIGURAÇÕES =================

LARGURA = 1000
ALTURA = 1000

DENSIDADE = 0.75
PROB_FOGO = 0.7

# Quantos passos executar antes de redesenhar
VISUALIZACAO_PASSOS = 3

# Intervalo da animação (ms)
INTERVALO_ANIMACAO = 120


# ================= ESCOLHER NÚCLEOS =================

max_nucleos = cpu_count()

if max_nucleos <= 4:
    N_PROC = max_nucleos
else:
    N_PROC = max_nucleos - 2


# ================= CORES =================

CMAP = plt.cm.colors.ListedColormap([
    '#111111',  # vazio
    '#075207',  # árvore
    '#df5313',  # fogo
    '#666666'   # queimado
])


# ======================================================
# CLASSE PRINCIPAL
# ======================================================

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
        self.simulador_paralelo = SimuladorParalelo(
            self.grade,
            N_PROC
        )

        # Monta interface
        self._montar_interface()

    # ==================================================

    def _montar_interface(self):

        # Figura principal
        self.fig = plt.figure(figsize=(13, 8))

        # Layout da tela
        gs = GridSpec(
            2,
            2,
            figure=self.fig,
            width_ratios=[4.5, 1.5],
            height_ratios=[12, 1]
        )

        # ==================================================
        # ÁREA DA GRADE
        # ==================================================

        self.ax_grade = self.fig.add_subplot(gs[0, 0])

        self.imagem = self.ax_grade.imshow(
            self.grade,
            cmap=CMAP,
            vmin=0,
            vmax=3,
            interpolation='nearest'
        )

        self.ax_grade.set_title(
            'Simulação de Incêndio Florestal',
            fontsize=16,
            pad=15
        )

        self.ax_grade.axis('off')

        # ==================================================
        # PAINEL LATERAL
        # ==================================================

        self.ax_painel = self.fig.add_subplot(gs[0, 1])

        self.ax_painel.axis('off')

        # Fundo visual do painel
        self.ax_painel.set_facecolor('#f0f0f0')

        # ==================================================
        # BLOCO CONTROLES
        # ==================================================

        self.ax_painel.text(
            0.5,
            0.92,
            'CONTROLES',
            ha='center',
            fontsize=14,
            fontweight='bold'
        )

        # Área do botão
        ax_btn = self.fig.add_axes([
            0.76,   # esquerda
            0.72,   # altura
            0.16,   # largura
            0.07    # altura
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
        # BLOCO STATUS
        # ==================================================

        self.ax_painel.text(
            0.5,
            0.55,
            'STATUS',
            ha='center',
            fontsize=14,
            fontweight='bold'
        )

        self.status_texto = self.ax_painel.text(
            0.08,
            0.42,
            f'Núcleos utilizados: {N_PROC}\n\n'
            f'Tempo de execução: --',
            fontsize=11,
            va='top'
        )

        # ==================================================
        # LEGENDA
        # ==================================================

        self.ax_legenda = self.fig.add_subplot(gs[1, :])

        self.ax_legenda.axis('off')

        legendas = [
            Patch(color='#111111', label='Vazio'),
            Patch(color='#075207', label='Árvore'),
            Patch(color='#df5313', label='Fogo'),
            Patch(color='#666666', label='Queimado')
        ]

        self.ax_legenda.legend(
            handles=legendas,
            loc='center',
            ncol=4,
            frameon=False,
            fontsize=11
        )

        # Ajuste geral
        plt.subplots_adjust(
            left=0.03,
            right=0.97,
            top=0.92,
            bottom=0.06,
            wspace=0.08
        )

    # ==================================================

    def _iniciar(self, evento):

        if self.rodando:
            return

        self.rodando = True

        self.tempo_inicio = time.time()

        self.btn.label.set_text('EXECUTANDO')

        # Cria animação
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

        # Executa vários passos internos
        for _ in range(VISUALIZACAO_PASSOS):

            self.simulador_paralelo.step(PROB_FOGO)

            self.grade = (
                self.simulador_paralelo.current_grid()
            )

            self.passo += 1

        # Atualiza imagem
        self.imagem.set_data(self.grade)

        # Conta células em chamas
        em_chamas = np.sum(
            self.grade == FOGO
        )

        # ==================================================
        # FINALIZAÇÃO
        # ==================================================

        arvores_restantes = np.sum(
            self.grade == ARVORE
        )

        if arvores_restantes == 0 or em_chamas == 0:

            self.rodando = False

            tempo_total = (
                time.time() - self.tempo_inicio
            )

            # Atualiza botão
            self.btn.label.set_text(
                'FINALIZADO'
            )

            # Atualiza status
            self.status_texto.set_text(
                f'Núcleos utilizados: {N_PROC}\n\n'
                f'Tempo de execução:\n'
                f'{tempo_total:.2f} segundos'
            )

            # Para animação
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