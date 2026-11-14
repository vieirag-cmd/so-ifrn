/*
 * rr_sim.c — simulador de Round Robin: efeito do quantum.
 *
 * Seminário de Sistemas Operacionais · Escalonamento, Parte B (Grupo 2)
 *
 * Compilar:  gcc -Wall -Wextra -O0 -o rr_sim rr_sim.c
 * Executar:  ./rr_sim [quantum] [custo_troca]
 *            ./rr_sim 2          (quantum 2, troca de contexto de graça)
 *            ./rr_sim 2 1        (quantum 2, cada troca gasta 1 unidade de CPU)
 *            ./rr_sim 100        (quantum enorme: vira FCFS)
 *
 * Os 4 processos abaixo são os combinados com a Parte A (Grupo 1).
 * Se algo mudar, troque só o vetor `procs`.
 *
 * Convenção usada: quando um processo novo chega no mesmo instante em que
 * outro é preemptado, o NOVO entra na fila ANTES do preemptado.
 */
#include <stdio.h>
#include <stdlib.h>

#define N 4

struct proc {
	const char *nome;
	int chegada;
	int duracao;
	int restante;
	int inicio;      /* primeira vez que usou a CPU (-1 = ainda não) */
	int fim;
};

static struct proc procs[N] = {
	{"P1", 0, 7, 7, -1, 0},
	{"P2", 2, 4, 4, -1, 0},
	{"P3", 4, 1, 1, -1, 0},
	{"P4", 5, 4, 4, -1, 0},
};

int main(int argc, char *argv[])
{
	int quantum = (argc > 1) ? atoi(argv[1]) : 2;
	int custo   = (argc > 2) ? atoi(argv[2]) : 0;
	if (quantum < 1) {
		fprintf(stderr, "quantum deve ser >= 1\n");
		return 1;
	}

	int fila[256], ini = 0, fim = 0;       /* fila circular simples */
	int prox = 0;                          /* próximo a chegar (procs já ordenados por chegada) */
	int t = 0, feitos = 0, ultimo = -1, trocas = 0;

	printf("Round Robin, quantum = %d, custo de troca = %d\n\nGantt:\n", quantum, custo);

	while (feitos < N) {
		while (prox < N && procs[prox].chegada <= t)
			fila[fim++ % 256] = prox++;

		if (ini == fim) {                  /* CPU ociosa: pula para a próxima chegada */
			t = procs[prox].chegada;
			continue;
		}

		int i = fila[ini++ % 256];

		if (ultimo != -1 && ultimo != i) { /* trocou de processo: paga a troca */
			trocas++;
			if (custo > 0) {
				printf("[%2d-%2d] troca\n", t, t + custo);
				t += custo;
				while (prox < N && procs[prox].chegada <= t)
					fila[fim++ % 256] = prox++;
			}
		}

		int fatia = procs[i].restante < quantum ? procs[i].restante : quantum;
		if (procs[i].inicio < 0)
			procs[i].inicio = t;

		printf("[%2d-%2d] %s\n", t, t + fatia, procs[i].nome);
		t += fatia;
		procs[i].restante -= fatia;
		ultimo = i;

		while (prox < N && procs[prox].chegada <= t)
			fila[fim++ % 256] = prox++;    /* chegadas entram ANTES do preemptado */

		if (procs[i].restante > 0) {
			fila[fim++ % 256] = i;
		} else {
			procs[i].fim = t;
			feitos++;
		}
	}

	printf("\n%-4s %7s %7s %7s %8s %8s\n", "proc", "cheg", "dur", "espera", "retorno", "resposta");
	double se = 0, sr = 0, sresp = 0;
	for (int i = 0; i < N; i++) {
		int retorno  = procs[i].fim - procs[i].chegada;
		int espera   = retorno - procs[i].duracao;
		int resposta = procs[i].inicio - procs[i].chegada;
		printf("%-4s %7d %7d %7d %8d %8d\n", procs[i].nome, procs[i].chegada,
		       procs[i].duracao, espera, retorno, resposta);
		se += espera; sr += retorno; sresp += resposta;
	}
	printf("\nmedia: espera = %.2f   retorno = %.2f   resposta = %.2f\n", se / N, sr / N, sresp / N);
	printf("trocas de contexto: %d   tempo total: %d\n", trocas, t);
	return 0;
}