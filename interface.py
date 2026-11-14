"""Interface gráfica para simulação de escalonamento e diagramas de Gantt."""

import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Patch

from escalonamento import fcfs, sjf, srtf, round_robin, PROCESSOS_EXEMPLO


class AplicacaoEscalonamento:
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("SO-IFRN | Simulador de Escalonamento")
        self.raiz.geometry("1120x780")
        self.raiz.minsize(900, 650)
        self.processos = list(PROCESSOS_EXEMPLO)

        self._configurar_estilo()
        self._construir_interface()
        self._atualizar_tabela_processos()
        self.executar_simulacao()

    def _configurar_estilo(self):
        estilo = ttk.Style()
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass
        estilo.configure("Titulo.TLabel", font=("TkDefaultFont", 16, "bold"))
        estilo.configure("Treeview", rowheight=25)
        estilo.configure("Treeview.Heading", font=("TkDefaultFont", 10, "bold"))

    def _construir_interface(self):
        principal = ttk.Frame(self.raiz, padding=12)
        principal.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            principal, text="Simulador de Escalonamento de CPU",
            style="Titulo.TLabel"
        ).pack(anchor=tk.W, pady=(0, 10))

        painel = ttk.LabelFrame(principal, text="Processos", padding=10)
        painel.pack(fill=tk.X)

        campos = ttk.Frame(painel)
        campos.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 14))

        self.nome_var = tk.StringVar()
        self.chegada_var = tk.StringVar(value="0")
        self.duracao_var = tk.StringVar(value="1")

        for linha, (rotulo, variavel) in enumerate((
            ("Nome", self.nome_var),
            ("Chegada", self.chegada_var),
            ("Duração", self.duracao_var),
        )):
            ttk.Label(campos, text=rotulo).grid(row=linha, column=0, sticky=tk.W, pady=3)
            ttk.Entry(campos, textvariable=variavel, width=12).grid(
                row=linha, column=1, sticky=tk.EW, padx=(8, 0), pady=3
            )

        botoes = ttk.Frame(campos)
        botoes.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=(8, 0))
        ttk.Button(botoes, text="Adicionar", command=self.adicionar_processo).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(botoes, text="Remover selecionado", command=self.remover_processo).pack(
            side=tk.LEFT
        )

        tabela_frame = ttk.Frame(painel)
        tabela_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        colunas = ("nome", "chegada", "duracao")
        self.tabela_processos = ttk.Treeview(
            tabela_frame, columns=colunas, show="headings", height=4,
            selectmode="browse"
        )
        for coluna, titulo, largura in (
            ("nome", "Processo", 100),
            ("chegada", "Tempo de chegada", 150),
            ("duracao", "Duração (burst)", 150),
        ):
            self.tabela_processos.heading(coluna, text=titulo)
            self.tabela_processos.column(coluna, width=largura, anchor=tk.CENTER)
        self.tabela_processos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        barra = ttk.Scrollbar(
            tabela_frame, orient=tk.VERTICAL, command=self.tabela_processos.yview
        )
        barra.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabela_processos.configure(yscrollcommand=barra.set)

        controles = ttk.LabelFrame(principal, text="Simulação", padding=10)
        controles.pack(fill=tk.X, pady=10)

        ttk.Label(controles, text="Algoritmo:").pack(side=tk.LEFT)
        self.algoritmo_var = tk.StringVar(value="SRTF")
        self.algoritmo_combo = ttk.Combobox(
            controles, textvariable=self.algoritmo_var, state="readonly",
            values=("FCFS", "SJF", "SRTF", "Round Robin"), width=18
        )
        self.algoritmo_combo.pack(side=tk.LEFT, padx=(7, 14))
        self.algoritmo_combo.bind("<<ComboboxSelected>>", self._alternar_quantum)

        self.quantum_var = tk.StringVar(value="2")
        self.quantum_label = ttk.Label(controles, text="Quantum:")
        self.quantum_entry = ttk.Entry(
            controles, textvariable=self.quantum_var, width=6
        )
        self.quantum_label.pack(side=tk.LEFT)
        self.quantum_entry.pack(side=tk.LEFT, padx=(7, 14))
        ttk.Button(
            controles, text="Executar simulação", command=self.executar_simulacao
        ).pack(side=tk.LEFT)
        ttk.Button(
            controles, text="Restaurar exemplo", command=self.restaurar_exemplo
        ).pack(side=tk.LEFT, padx=7)

        self.status_var = tk.StringVar(value="Pronto.")
        ttk.Label(principal, textvariable=self.status_var).pack(
            anchor=tk.W, pady=(0, 5)
        )

        grafico_frame = ttk.LabelFrame(principal, text="Diagrama de Gantt", padding=6)
        grafico_frame.pack(fill=tk.BOTH, expand=True)
        self.figura = Figure(figsize=(9, 3.3), dpi=100, constrained_layout=True)
        self.eixo = self.figura.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figura, master=grafico_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        resultados = ttk.LabelFrame(principal, text="Métricas por processo", padding=6)
        resultados.pack(fill=tk.X, pady=(10, 0))
        cols = ("processo", "chegada", "duracao", "conclusao", "espera", "retorno")
        self.tabela_metricas = ttk.Treeview(
            resultados, columns=cols, show="headings", height=4
        )
        titulos = (
            ("processo", "Processo"), ("chegada", "Chegada"),
            ("duracao", "Duração"), ("conclusao", "Conclusão"),
            ("espera", "Espera"), ("retorno", "Retorno"),
        )
        for coluna, titulo in titulos:
            self.tabela_metricas.heading(coluna, text=titulo)
            self.tabela_metricas.column(coluna, anchor=tk.CENTER, width=110)
        self.tabela_metricas.pack(fill=tk.X)

        self.medias_var = tk.StringVar()
        ttk.Label(
            principal, textvariable=self.medias_var,
            font=("TkDefaultFont", 10, "bold")
        ).pack(anchor=tk.E, pady=(7, 0))

    def _atualizar_tabela_processos(self):
        for item in self.tabela_processos.get_children():
            self.tabela_processos.delete(item)
        for processo in self.processos:
            self.tabela_processos.insert("", tk.END, values=processo)

    def adicionar_processo(self):
        nome = self.nome_var.get().strip()
        try:
            chegada = int(self.chegada_var.get())
            duracao = int(self.duracao_var.get())
            if not nome:
                raise ValueError("Informe o nome do processo.")
            if chegada < 0 or duracao <= 0:
                raise ValueError("Chegada deve ser >= 0 e duração deve ser > 0.")
            if any(p[0] == nome for p in self.processos):
                raise ValueError("Já existe um processo com esse nome.")
        except ValueError as erro:
            messagebox.showerror("Dados inválidos", str(erro))
            return

        self.processos.append((nome, chegada, duracao))
        self.nome_var.set("")
        self._atualizar_tabela_processos()

    def remover_processo(self):
        selecionados = self.tabela_processos.selection()
        if not selecionados:
            messagebox.showinfo("Remover processo", "Selecione um processo.")
            return
        nome = self.tabela_processos.item(selecionados[0], "values")[0]
        self.processos = [p for p in self.processos if p[0] != nome]
        self._atualizar_tabela_processos()

    def restaurar_exemplo(self):
        self.processos = list(PROCESSOS_EXEMPLO)
        self._atualizar_tabela_processos()
        self.executar_simulacao()

    def _alternar_quantum(self, _evento=None):
        estado = tk.NORMAL if self.algoritmo_var.get() == "Round Robin" else tk.DISABLED
        self.quantum_entry.configure(state=estado)

    def executar_simulacao(self):
        try:
            algoritmo = self.algoritmo_var.get()
            if algoritmo == "FCFS":
                resultado = fcfs(self.processos)
            elif algoritmo == "SJF":
                resultado = sjf(self.processos)
            elif algoritmo == "SRTF":
                resultado = srtf(self.processos)
            elif algoritmo == "Round Robin":
                resultado = round_robin(self.processos, int(self.quantum_var.get()))
            else:
                raise ValueError("Selecione um algoritmo válido.")
        except (ValueError, TypeError) as erro:
            messagebox.showerror("Não foi possível simular", str(erro))
            return

        self._desenhar_gantt(resultado)
        self._atualizar_metricas(resultado)
        self.status_var.set(f"Simulação concluída: {resultado['algoritmo']}.")

    def _desenhar_gantt(self, resultado):
        self.eixo.clear()
        gantt = resultado["gantt"]
        nomes = list(dict.fromkeys(item[2] for item in gantt))
        paleta = {
            nome: ("#b8bec8" if nome == "IDLE" else
                   f"C{indice % 10}")
            for indice, nome in enumerate(nomes)
        }

        for inicio, fim, nome in gantt:
            self.eixo.barh(
                0, fim - inicio, left=inicio, height=0.55,
                color=paleta[nome], edgecolor="white", linewidth=1
            )
            self.eixo.text(
                (inicio + fim) / 2, 0, nome,
                ha="center", va="center", fontsize=9, fontweight="bold"
            )

        limite = max((fim for _, fim, _ in gantt), default=1)
        marcas = sorted(set([0] + [ponto for inicio, fim, _ in gantt
                                   for ponto in (inicio, fim)]))
        self.eixo.set_xticks(marcas)
        self.eixo.set_xlim(0, max(1, limite))
        self.eixo.set_ylim(-0.55, 0.55)
        self.eixo.set_yticks([])
        self.eixo.set_xlabel("Tempo")
        self.eixo.set_title(resultado["algoritmo"])
        self.eixo.grid(axis="x", linestyle=":", alpha=0.5)
        legenda = [
            Patch(facecolor=paleta[nome], label=nome, edgecolor="white")
            for nome in nomes
        ]
        self.eixo.legend(handles=legenda, loc="upper center",
                         bbox_to_anchor=(0.5, -0.28), ncol=min(6, len(legenda)))
        self.canvas.draw_idle()

    def _atualizar_metricas(self, resultado):
        for item in self.tabela_metricas.get_children():
            self.tabela_metricas.delete(item)
        for m in resultado["metricas"]:
            self.tabela_metricas.insert("", tk.END, values=(
                m["processo"], m["chegada"], m["duracao"],
                m["conclusao"], m["espera"], m["retorno"]
            ))
        self.medias_var.set(
            f"Tempo médio de espera: {resultado['espera_media']:.2f}    |    "
            f"Tempo médio de retorno: {resultado['retorno_medio']:.2f}"
        )


def main():
    raiz = tk.Tk()
    AplicacaoEscalonamento(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
