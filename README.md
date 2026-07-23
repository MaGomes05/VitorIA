# VitórIA 🤖

Automação em Python para execução de tarefas repetitivas no **PJe (Processo Judicial Eletrônico)**, desenvolvida para auxiliar a equipe da Assessoria de Processamento do **TRE-PB**, reduzindo o tempo gasto em atividades operacionais.

---

# Funcionalidades

Atualmente o sistema possui as seguintes automações:

| Tarefa                                   | Status                     |
| ---------------------------------------- | -------------------------- |
| 📄 Visualizar Expediente DJE             | ✅ Disponível              |
| 📑 Verificação de Certidão de Julgamento | ✅ Disponível              |
| 🏷️ Etiqueta META 02 - 70%                | 🚧 Desenvolvimento pausado |
| ✅ Verificação de Baixa Definitiva       | 🚧 Desenvolvimento pausado |

---

# Funcionamento das tarefas

## 📄 Visualizar Expediente DJE

Realiza automaticamente a conferência dos expedientes publicados no Diário da Justiça Eletrônico (DJE).

### Fluxo

```text
Login
      │
      ▼
Selecionar perfil
      │
      ▼
Abrir tarefa "Visualizar Expediente DJE"
      │
      ▼
Abrir DJE em uma nova aba
      │
      ▼
Para cada processo:
      │
      ├── Abrir o processo
      ├── Abrir os autos
      ├── Consultar a data do expediente
      ├── Pesquisar o processo no DJE
      ├── Comparar as datas
      └── Finalizar o processo quando aplicável
```

---

## 📑 Verificação de Certidão de Julgamento

Percorre automaticamente os processos da tarefa verificando a existência da **Certidão de Julgamento** nos autos.

Quando localizada, o processo é automaticamente finalizado na tarefa.

### Fluxo

```text
Login
      │
      ▼
Selecionar perfil
      │
      ▼
Abrir tarefa
      │
      ▼
Para cada processo:
      │
      ├── Abrir processo
      ├── Abrir autos
      ├── Procurar Certidão de Julgamento
      ├── Se encontrada:
      │        └── Finalizar processo
      │
      └── Caso contrário:
               └── Passar para o próximo processo
```

---

## 🏷️ Etiqueta META 02 - 70%

> 🚧 **Desenvolvimento pausado**

Automação destinada à identificação e etiquetagem de processos relacionados ao cumprimento da **Meta 02 - 70%**, reduzindo o trabalho manual de classificação.

---

## ✅ Verificação de Baixa Definitiva

> 🚧 **Desenvolvimento pausado**

Automação destinada à conferência da movimentação processual para identificar processos que já possuem **Baixa Definitiva**, permitindo sua finalização automática na tarefa correspondente.

---

# Tecnologias utilizadas

- Python 3
- Selenium
- Firefox
- GeckoDriver
- Tkinter
- Pillow
- Pyperclip

---

# Estrutura do projeto

```
VitorIA/
│
├── interface.py          # Interface gráfica
├── tarefas.py            # Implementação das automações
├── main.py               # Inicialização do sistema
├── geckodriver.exe
├── logo2.jpg
├── requirements.txt
└── README.md
```

---

# Como funciona

1. O usuário informa login e senha do PJe.
2. O Firefox é iniciado automaticamente.
3. Caso solicitado, o usuário informa manualmente o código de autenticação em dois fatores (2FA).
4. O sistema aguarda a conclusão da autenticação.
5. O usuário escolhe uma das tarefas disponíveis.
6. A automação é executada até sua conclusão.

---

# Requisitos

- Windows
- Mozilla Firefox
- GeckoDriver compatível com a versão instalada
- Python 3.11 ou superior

---

# Instalação

Clone o repositório:

```bash
git clone https://github.com/MaGomes05/VitorIA.git
```

Entre na pasta:

```bash
cd VitorIA
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute:

```bash
python main.py
```

---

# Observações

- O login utiliza autenticação em dois fatores (2FA).
- O código do 2FA é informado manualmente pelo usuário.
- O sistema aguarda automaticamente a conclusão da autenticação antes de liberar as tarefas.
- Algumas automações utilizam múltiplas abas e iframes para consulta de informações no PJe e no DJE.
- O projeto foi desenvolvido visando reduzir atividades repetitivas e minimizar erros operacionais.

---

# Autor

**Maria Antonia de Paula Gomes**

Desenvolvido durante o estágio no **Tribunal Regional Eleitoral da Paraíba (TRE-PB)**.
