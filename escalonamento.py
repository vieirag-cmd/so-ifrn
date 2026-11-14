"""Simulador de escalonamento de CPU: FCFS, SJF, SRTF e Round Robin.

Cada processo é representado por uma tupla (nome, chegada, duração).
As funções de simulação recebem a lista explicitamente e retornam dados,
sem depender de interface gráfica ou imprimir automaticamente.
"""

from collections import deque
from typing import Iterable

# Exemplo usado pela execução em modo terminal.
PROCESSOS_EXEMPLO = [
    ("P1", 0, 7),
    ("P2", 2, 4),
    ("P3", 4, 1),
    ("P4", 5, 4),
]
QUANTUM_PADRAO = 2


def validar_processos(processos: Iterable[tuple]) -> list[tuple[str, int, int]]:
    """Valida e normaliza processos (nome, tempo de chegada, duração)."""
    normalizados = []
    nomes = set()

    for item in processos:
        if len(item) != 3:
            raise ValueError("Cada processo deve conter nome, chegada e duração.")

        nome, chegada, duracao = item
        nome = str(nome).strip()

        if not nome:
            raise ValueError("O nome do processo não pode ficar vazio.")
        if nome in nomes:
            raise ValueError(f"Nome de processo duplicado: {nome}.")
        if isinstance(chegada, bool) or not isinstance(chegada, int) or chegada < 0:
            raise ValueError(f"O tempo de chegada de {nome} deve ser um inteiro >= 0.")
        if isinstance(duracao, bool) or not isinstance(duracao, int) or duracao <= 0:
            raise ValueError(f"A duração de {nome} deve ser um inteiro > 0.")

        nomes.add(nome)
        normalizados.append((nome, chegada, duracao))

    if not normalizados:
        raise ValueError("Adicione pelo menos um processo.")

    return normalizados


def adicionar(gantt: list, inicio: int, fim: int, processo: str) -> None:
    """Adiciona um intervalo e une intervalos adjacentes do mesmo processo."""
    if inicio >= fim:
        return
    if gantt and gantt[-1][2] == processo and gantt[-1][1] == inicio:
        gantt[-1] = (gantt[-1][0], fim, processo)
    else:
        gantt.append((inicio, fim, processo))


def _resultado(algoritmo: str, processos: list, gantt: list, conclusao: dict) -> dict:
    metricas = []
    for nome, chegada, duracao in processos:
        termino = conclusao[nome]
        retorno = termino - chegada
        espera = retorno - duracao
        metricas.append({
            "processo": nome,
            "chegada": chegada,
            "duracao": duracao,
            "conclusao": termino,
            "espera": espera,
            "retorno": retorno,
        })

    quantidade = len(metricas)
    return {
        "algoritmo": algoritmo,
        "gantt": gantt,
        "metricas": metricas,
        "conclusao": conclusao,
        "espera_media": sum(m["espera"] for m in metricas) / quantidade,
        "retorno_medio": sum(m["retorno"] for m in metricas) / quantidade,
    }


def fcfs(processos=None) -> dict:
    """First Come, First Served: atende por ordem de chegada."""
    ps = validar_processos(PROCESSOS_EXEMPLO if processos is None else processos)
    ordenados = sorted(enumerate(ps), key=lambda x: (x[1][1], x[0]))
    tempo, gantt, conclusao = 0, [], {}

    for _, (nome, chegada, duracao) in ordenados:
        if tempo < chegada:
            adicionar(gantt, tempo, chegada, "IDLE")
            tempo = chegada
        inicio = tempo
        tempo += duracao
        adicionar(gantt, inicio, tempo, nome)
        conclusao[nome] = tempo

    return _resultado("FCFS", ps, gantt, conclusao)


def sjf(processos=None) -> dict:
    """Shortest Job First não preemptivo."""
    ps = validar_processos(PROCESSOS_EXEMPLO if processos is None else processos)
    pendentes = list(enumerate(ps))
    tempo, gantt, conclusao = 0, [], {}

    while pendentes:
        disponiveis = [item for item in pendentes if item[1][1] <= tempo]
        if not disponiveis:
            proximo = min(item[1][1] for item in pendentes)
            adicionar(gantt, tempo, proximo, "IDLE")
            tempo = proximo
            continue

        escolhido = min(disponiveis, key=lambda x: (x[1][2], x[1][1], x[0]))
        pendentes.remove(escolhido)
        nome, _, duracao = escolhido[1]
        inicio = tempo
        tempo += duracao
        adicionar(gantt, inicio, tempo, nome)
        conclusao[nome] = tempo

    return _resultado("SJF", ps, gantt, conclusao)


def srtf(processos=None) -> dict:
    """Shortest Remaining Time First: versão preemptiva do SJF.

    A cada unidade de tempo, escolhe o processo disponível com menor tempo
    restante. Empates são resolvidos por chegada e, depois, pela ordem original.
    """
    ps = validar_processos(PROCESSOS_EXEMPLO if processos is None else processos)
    restantes = {nome: duracao for nome, _, duracao in ps}
    indice = {nome: i for i, (nome, _, _) in enumerate(ps)}
    chegadas = {nome: chegada for nome, chegada, _ in ps}
    conclusao, gantt = {}, []
    tempo = min(chegadas.values())

    while len(conclusao) < len(ps):
        disponiveis = [
            nome for nome, chegada, _ in ps
            if chegada <= tempo and restantes[nome] > 0
        ]

        if not disponiveis:
            proximo = min(
                chegada for nome, chegada, _ in ps
                if restantes[nome] > 0 and chegada > tempo
            )
            adicionar(gantt, tempo, proximo, "IDLE")
            tempo = proximo
            continue

        escolhido = min(
            disponiveis,
            key=lambda nome: (restantes[nome], chegadas[nome], indice[nome])
        )
        adicionar(gantt, tempo, tempo + 1, escolhido)
        restantes[escolhido] -= 1
        tempo += 1

        if restantes[escolhido] == 0:
            conclusao[escolhido] = tempo

    return _resultado("SRTF", ps, gantt, conclusao)


def round_robin(processos=None, quantum: int = QUANTUM_PADRAO) -> dict:
    """Round Robin com quantum configurável."""
    ps = validar_processos(PROCESSOS_EXEMPLO if processos is None else processos)
    if isinstance(quantum, bool) or not isinstance(quantum, int) or quantum <= 0:
        raise ValueError("O quantum deve ser um inteiro maior que zero.")

    ordenados = sorted(enumerate(ps), key=lambda x: (x[1][1], x[0]))
    restantes = {nome: duracao for nome, _, duracao in ps}
    fila, conclusao, gantt = deque(), {}, []
    tempo, i = 0, 0

    while i < len(ordenados) or fila:
        if not fila and i < len(ordenados):
            proxima = ordenados[i][1][1]
            if tempo < proxima:
                adicionar(gantt, tempo, proxima, "IDLE")
                tempo = proxima

        while i < len(ordenados) and ordenados[i][1][1] <= tempo:
            fila.append(ordenados[i][1][0])
            i += 1

        if not fila:
            continue

        nome = fila.popleft()
        execucao = min(quantum, restantes[nome])
        inicio = tempo
        tempo += execucao
        restantes[nome] -= execucao
        adicionar(gantt, inicio, tempo, nome)

        # Processos que chegaram durante o quantum entram antes do reencaminhamento.
        while i < len(ordenados) and ordenados[i][1][1] <= tempo:
            fila.append(ordenados[i][1][0])
            i += 1

        if restantes[nome] > 0:
            fila.append(nome)
        else:
            conclusao[nome] = tempo

    return _resultado(f"Round Robin (quantum = {quantum})", ps, gantt, conclusao)


def mostrar(resultado: dict) -> None:
    """Apresenta no terminal um resultado produzido por qualquer algoritmo."""
    print(f"\n{'=' * 64}\n{resultado['algoritmo']}\n{'=' * 64}")
    print("\nDIAGRAMA DE GANTT:")
    print(" -> ".join(
        f"[{inicio}-{fim}: {processo}]"
        for inicio, fim, processo in resultado["gantt"]
    ))
    print("\nPROCESSO | CHEGADA | DURAÇÃO | CONCLUSÃO | ESPERA | RETORNO")
    for m in resultado["metricas"]:
        print(
            f"{m['processo']:8} | {m['chegada']:7} | {m['duracao']:7} | "
            f"{m['conclusao']:9} | {m['espera']:6} | {m['retorno']:7}"
        )
    print(f"\nEspera média: {resultado['espera_media']:.2f}")
    print(f"Retorno médio: {resultado['retorno_medio']:.2f}")


def main() -> None:
    """Executa os quatro algoritmos com os processos de exemplo."""
    for resultado in (
        fcfs(PROCESSOS_EXEMPLO),
        sjf(PROCESSOS_EXEMPLO),
        srtf(PROCESSOS_EXEMPLO),
        round_robin(PROCESSOS_EXEMPLO, QUANTUM_PADRAO),
    ):
        mostrar(resultado)


if __name__ == "__main__":
    main()
