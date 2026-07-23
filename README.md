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
- OpenPyXL
- Pyperclip

---

# Estrutura do projeto

```text
VitorIA/
│
├── tarefas/
│   ├── __init__.py
│   ├── login.py
│   ├── visualizar_dje.py
│   ├── processo_julgado.py
│   ├── meta_02.py
│   └── baixa_definitiva.py
│
├── config.py
├── utilitarios.py
├── interface.py
├── main.py
├── geckodriver.exe
├── logo2.jpg
├── requirements.txt
└── README.md
```

---

# Como utilizar

## 1. Inicie a aplicação

Execute o arquivo **VitórIA.exe** ou execute o projeto através do Python:

```bash
python main.py
```

---

## 2. Informe suas credenciais

Na interface da aplicação, informe:

- Usuário do **PJe 2º Grau do TRE-PB**
- Senha

Em seguida clique em **Entrar**.

---

## 3. Realize a autenticação em dois fatores (2FA)

Após clicar em **Entrar**, o Firefox será aberto automaticamente.

Quando solicitado pelo PJe:

- informe manualmente o código de autenticação (2FA);
- conclua normalmente a autenticação.

A automação aguardará automaticamente essa etapa.

---

## 4. Token PJe

Em alguns acessos, após a validação do 2FA, o PJe apresenta a tela **"Prosseguir sem o Token"**.

Quando essa tela for exibida, a automação realizará esse procedimento automaticamente.

Após o carregamento da tela principal do PJe, as tarefas disponíveis serão habilitadas na interface.

---

## 5. Execute uma tarefa

Clique na tarefa desejada.

Durante a execução da automação, o navegador será controlado automaticamente até a conclusão da rotina.

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
- O código do 2FA deve ser informado manualmente pelo usuário.
- A automação aguarda automaticamente a conclusão da autenticação antes de habilitar as tarefas.
- Caso seja apresentada a tela **"PJe Mobile"**, ela será tratada automaticamente pela aplicação.
- Não utilize a janela do Firefox enquanto uma automação estiver em execução.
- Algumas automações utilizam múltiplas abas e iframes para consulta de informações no PJe e no DJE.
- Alterações na interface do PJe ou do DJE podem exigir atualização da automação.

---

# Autor

**Maria Antonia de Paula Gomes**

Desenvolvido durante o estágio no **Tribunal Regional Eleitoral da Paraíba (TRE-PB)**.
