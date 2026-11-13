
# SO-IFRN

Ambiente de desenvolvimento e simulacao de algoritmos
de escalonamento de processos para a disciplina
de Sistemas Operacionais.

## Objetivos

- Compreender o funcionamento do escalonador de CPU.
- Implementar algoritmos de escalonamento.
- Construir diagramas de Gantt.
- Calcular tempos de espera e retorno.
- Comparar o desempenho dos algoritmos.

## Tecnologias

- Ubuntu 24.04
- Docker
- C++ (GCC)
- Python 3
- Git

## Algoritmos estudados

- FCFS (First Come, First Served)
- SJF (Shortest Job First)
- SRTF (Shortest Remaining Time First)
- Round Robin (RR)

## Requisitos

- Docker Desktop
- Git

## Instalacao

Clone o repositorio:

```bash
git clone https://github.com/vieirag-cmd/so-ifrn.git
cd so-ifrn
```

Construa a imagem:

```bash
docker build -t so-ifrn .
```

Execute o ambiente:

No CMD do Windows:

```cmd
docker run --rm -it -v "%cd%:/workspace" so-ifrn
```

No terminal Linux:

```bash
docker run --rm -it -v "$(pwd):/workspace" so-ifrn
```

## Executando os programas

Simulacao em Python:

```bash
python3 escalonamento.py
```

Compilacao em C++:

```bash
g++ -std=c++17 -Wall -Wextra teste.cpp -o teste
```

Execucao:

```bash
./teste
```

## Estrutura

```text
so-ifrn/
├── Dockerfile
├── README.md
├── .gitignore
├── escalonamento.py
└── teste.cpp
```

## Colaboracao

Contribuicoes dos integrantes do grupo sao bem-vindas.

Antes de trabalhar, atualize seu repositorio:

```bash
git pull origin main
```

Depois de realizar alteracoes:

```bash
git add .
git commit -m "Descricao das alteracoes"
git push origin main
```

## Finalidade academica

Projeto desenvolvido para fins educacionais
na disciplina de Sistemas Operacionais do IFRN.
