# SO-IFRN — Simulador de Escalonamento de Processos

Projeto acadêmico da disciplina de **Sistemas Operacionais** do IFRN. O sistema simula algoritmos de escalonamento de CPU, calcula métricas de desempenho e apresenta diagramas de Gantt em uma interface gráfica.

## Objetivos

- Compreender o funcionamento do escalonador de CPU.
- Implementar e comparar algoritmos preemptivos e não preemptivos.
- Visualizar a ordem de execução dos processos por meio de diagramas de Gantt.
- Calcular tempos de espera, retorno e conclusão.
- Experimentar diferentes tempos de chegada, durações e valores de quantum.

## Funcionalidades

- **FCFS (First Come, First Served):** executa os processos pela ordem de chegada.
- **SJF (Shortest Job First):** seleciona o menor processo disponível, sem preempção.
- **SRTF (Shortest Remaining Time First):** versão preemptiva do SJF; a CPU pode trocar de processo quando chega um processo com menor tempo restante.
- **Round Robin (RR):** distribui a CPU em fatias de tempo (*quantum*) configuráveis.
- Cadastro e remoção de processos na interface.
- Diagrama de Gantt com intervalos de execução e períodos ociosos (`IDLE`).
- Tabela com tempos de conclusão, espera e retorno, além das médias.

## Tecnologias

- Python 3.10 ou superior.
- Tkinter (biblioteca de interface gráfica do Python).
- Matplotlib (visualização dos diagramas de Gantt).
- Git.
- Docker (opcional, para o ambiente de terminal).

## Estrutura do projeto

```text
so-ifrn/
├── escalonamento.py       # Implementação dos algoritmos e métricas
├── interface.py           # Interface gráfica Tkinter + Matplotlib
├── test_escalonamento.py  # Testes automatizados
├── requirements.txt       # Dependências Python
├── Dockerfile             # Ambiente opcional de desenvolvimento
├── .gitignore
└── README.md
```

## Requisitos e instalação

### Windows

1. Instale Python 3.10 ou superior. Na instalação, habilite a opção de adicionar Python ao `PATH`.
2. Clone o repositório:

```bash
git clone https://github.com/vieirag-cmd/so-ifrn.git
cd so-ifrn
```

3. Crie e ative um ambiente virtual:

```powershell
py -m venv .venv
.venv\Scripts\activate
```

4. Instale as dependências:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

O Tkinter normalmente acompanha a distribuição oficial do Python para Windows.

### Ubuntu / Debian

Instale Python, o suporte ao Tkinter e ferramentas para ambientes virtuais:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-tk python3-pip
```

Clone o projeto e instale as dependências em um ambiente virtual:

```bash
git clone https://github.com/vieirag-cmd/so-ifrn.git
cd so-ifrn
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Em ambientes Linux sem interface gráfica, a janela Tkinter não poderá ser aberta. Execute a aplicação em uma sessão de desktop com suporte a janelas.

## Como executar

### Interface gráfica

Com o ambiente virtual ativado:

```bash
python interface.py
```

Na janela, adicione processos informando nome, tempo de chegada e duração. Selecione o algoritmo e clique em **Executar simulação**. Para Round Robin, informe também o quantum. O botão **Restaurar exemplo** recupera os processos demonstrativos.

### Modo terminal

Também é possível executar as simulações e imprimir os resultados no terminal:

```bash
python escalonamento.py
```

### Utilização como módulo

As funções recebem uma lista de tuplas no formato `(nome, chegada, duração)` e retornam um dicionário com o diagrama de Gantt, as métricas individuais e as médias:

```python
from escalonamento import fcfs, sjf, srtf, round_robin

processos = [
    ("P1", 0, 7),
    ("P2", 2, 4),
    ("P3", 4, 1),
]

resultado = srtf(processos)
print(resultado["gantt"])
print(resultado["espera_media"])
print(resultado["retorno_medio"])

resultado_rr = round_robin(processos, quantum=2)
```

## Métricas utilizadas

Para cada processo:

- **Tempo de retorno:** instante de conclusão menos instante de chegada.
- **Tempo de espera:** tempo de retorno menos duração total de CPU.
- **Tempo médio:** soma da métrica de todos os processos dividida pela quantidade de processos.

Em fórmulas:

```text
Tempo de retorno = Tempo de conclusão - Tempo de chegada
Tempo de espera  = Tempo de retorno - Duração
```

Os intervalos `IDLE` representam períodos em que nenhum processo está disponível para execução. Os processos devem ter nomes únicos, chegada inteira não negativa e duração inteira positiva. O quantum do Round Robin também deve ser um inteiro positivo.

## Testes

Execute os testes automatizados com:

```bash
python -m unittest -v
```

Os testes verificam preempção do SRTF, períodos ociosos, comportamento do SJF, quantum do Round Robin, validação de entradas e cálculo das médias.

## Docker (opcional)

O Dockerfile instala dependências de desenvolvimento e bibliotecas gráficas. Para construir a imagem:

```bash
docker build -t so-ifrn .
```

Para abrir um terminal no contêiner:

```bash
docker run --rm -it -v "$(pwd):/workspace" so-ifrn
```

A interface gráfica deve ser executada diretamente no sistema hospedeiro, a menos que o Docker esteja configurado para encaminhar o servidor gráfico (X11/Wayland). Para a experiência mais simples com Tkinter, recomenda-se executar a aplicação localmente, seguindo as instruções de instalação acima.

## Colaboração

Antes de começar a trabalhar, atualize sua cópia local:

```bash
git pull origin main
```

Depois de implementar e testar suas alterações:

```bash
git add .
git commit -m "Descreva as alterações"
git push origin main
```

Converse com os integrantes do grupo antes de integrar alterações que possam conflitar com o trabalho de outras pessoas.

## Finalidade acadêmica

Projeto desenvolvido para fins educacionais na disciplina de Sistemas Operacionais do Instituto Federal do Rio Grande do Norte (IFRN).
