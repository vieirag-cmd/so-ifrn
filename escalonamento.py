
from collections import deque

# Processos: (nome, chegada, duracao)
processos = [
    ("P1", 0, 7),
    ("P2", 2, 4),
    ("P3", 4, 1),
    ("P4", 5, 4)
]

QUANTUM = 2


def mostrar(nome, processos, gantt, conclusao):
    print(f"\n{'=' * 55}")
    print(nome)
    print("=" * 55)

    print("\nDIAGRAMA DE GANTT:")
    print(" -> ".join(
        f"[{inicio}-{fim}: {proc}]"
        for inicio, fim, proc in gantt
    ))

    print("\nPROCESSO | ESPERA | RETORNO")
    espera_total = 0
    retorno_total = 0

    for p, chegada, duracao in processos:
        retorno = conclusao[p] - chegada
        espera = retorno - duracao

        espera_total += espera
        retorno_total += retorno

        print(f"{p:8} | {espera:6} | {retorno:7}")

    n = len(processos)

    print(f"\nEspera media: {espera_total / n:.2f}")
    print(f"Retorno medio: {retorno_total / n:.2f}")


def adicionar(gantt, inicio, fim, processo):
    if inicio == fim:
        return

    if (gantt and gantt[-1][2] == processo
            and gantt[-1][1] == inicio):
        gantt[-1] = (gantt[-1][0], fim, processo)
    else:
        gantt.append((inicio, fim, processo))


# FCFS: primeiro a chegar, primeiro a executar
def fcfs():
    fila = sorted(enumerate(processos),
                  key=lambda x: (x[1][1], x[0]))

    tempo = 0
    gantt = []
    conclusao = {}

    for _, (nome, chegada, duracao) in fila:
        if tempo < chegada:
            adicionar(gantt, tempo, chegada, "IDLE")
            tempo = chegada

        inicio = tempo
        tempo += duracao

        adicionar(gantt, inicio, tempo, nome)
        conclusao[nome] = tempo

    mostrar("FCFS", processos, gantt, conclusao)


# SJF: menor processo disponivel primeiro
def sjf():
    pendentes = list(enumerate(processos))
    tempo = 0
    gantt = []
    conclusao = {}

    while pendentes:
        disponiveis = [
            x for x in pendentes
            if x[1][1] <= tempo
        ]

        if not disponiveis:
            proximo = min(x[1][1] for x in pendentes)
            adicionar(gantt, tempo, proximo, "IDLE")
            tempo = proximo
            continue

        escolhido = min(
            disponiveis,
            key=lambda x: (x[1][2], x[1][1], x[0])
        )

        indice, (nome, chegada, duracao) = escolhido
        pendentes.remove(escolhido)

        inicio = tempo
        tempo += duracao

        adicionar(gantt, inicio, tempo, nome)
        conclusao[nome] = tempo

    mostrar("SJF", processos, gantt, conclusao)


# ROUND ROBIN: cada processo recebe um quantum
def round_robin():
    ordenados = sorted(
        enumerate(processos),
        key=lambda x: (x[1][1], x[0])
    )

    restantes = {
        p[0]: p[2] for _, p in ordenados
    }

    fila = deque()
    conclusao = {}
    gantt = []

    tempo = 0
    i = 0

    while i < len(ordenados) or fila:

        if not fila:
            proxima = ordenados[i][1][1]

            if tempo < proxima:
                adicionar(gantt, tempo, proxima, "IDLE")
                tempo = proxima

        # Adiciona processos que ja chegaram
        while (i < len(ordenados)
               and ordenados[i][1][1] <= tempo):
            fila.append(ordenados[i][1][0])
            i += 1

        nome = fila.popleft()

        execucao = min(QUANTUM, restantes[nome])

        inicio = tempo
        tempo += execucao
        restantes[nome] -= execucao

        adicionar(gantt, inicio, tempo, nome)

        # Novas chegadas entram antes do processo interrompido
        while (i < len(ordenados)
               and ordenados[i][1][1] <= tempo):
            fila.append(ordenados[i][1][0])
            i += 1

        if restantes[nome] > 0:
            fila.append(nome)
        else:
            conclusao[nome] = tempo

    mostrar(
        f"ROUND ROBIN (Quantum = {QUANTUM})",
        processos, gantt, conclusao
    )


# EXECUCAO
fcfs()
sjf()
round_robin()

