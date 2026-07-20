import os
import sys
import tkinter as tk

from queue import Empty, Queue
from threading import Thread
from tkinter import messagebox, ttk

from PIL import Image, ImageTk

from tarefas import (
    Etiqueta_meta2_70,
    Inicial,
    ProcBaixa,
    Tarefa_visualizaDJE,
    ProcJulgado
)


def caminho_recurso(nome_arquivo: str) -> str:
    if getattr(sys, "frozen", False):
        pasta_base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        pasta_base = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(pasta_base, nome_arquivo)


class Interface:
    def __init__(self):
        self.window = None
        self.navegador = None
        self.login_em_andamento = False
        self.tarefa_em_andamento = False
        self.senha_visivel = False
        self.fila_resultados = Queue()
        self.botoes_tarefas = []
        self.canvas_tarefas = None
        self.frame_botoes_tarefas = None
        self.janela_canvas_tarefas = None

    def execute(self):
        self.window = tk.Tk()
        self.window.title("VitórIA")
        self.window.configure(bg="#F4F6FA")
        self.window.minsize(900, 600)

        try:
            self.window.state("zoomed")
        except tk.TclError:
            self.window.geometry("1100x700")

        self.configurar_estilos()
        self.criar_interface()

        self.window.after(100, self.processar_fila)
        self.window.protocol("WM_DELETE_WINDOW", self.fechar_programa)
        self.window.mainloop()

    def configurar_estilos(self):
        estilo = ttk.Style()

        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass

        estilo.configure(
            "Titulo.TLabel",
            background="#F4F6FA",
            foreground="#26354A",
            font=("Segoe UI", 22, "bold"),
        )
        estilo.configure(
            "Subtitulo.TLabel",
            background="#F4F6FA",
            foreground="#687386",
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "Campo.TLabel",
            background="#FFFFFF",
            foreground="#344054",
            font=("Segoe UI", 10, "bold"),
        )
        estilo.configure("TEntry", padding=8, font=("Segoe UI", 10))

    def criar_interface(self):
        container = tk.Frame(self.window, bg="#F4F6FA", padx=30, pady=20)
        container.pack(fill="both", expand=True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)

        frame_cabecalho = tk.Frame(container, bg="#F4F6FA")
        frame_cabecalho.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.criar_cabecalho(frame_cabecalho)

        area_principal = tk.Frame(container, bg="#F4F6FA")
        area_principal.grid(row=1, column=0, sticky="nsew")
        area_principal.grid_columnconfigure(0, weight=1, minsize=360)
        area_principal.grid_columnconfigure(1, weight=2, minsize=500)
        area_principal.grid_rowconfigure(0, weight=1)

        frame_login = tk.Frame(area_principal, bg="#F4F6FA")
        frame_login.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        frame_tarefas = tk.Frame(area_principal, bg="#F4F6FA")
        frame_tarefas.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self.criar_area_login(frame_login)
        self.criar_area_tarefas(frame_tarefas)

        frame_status = tk.Frame(container, bg="#F4F6FA")
        frame_status.grid(row=2, column=0, sticky="ew", pady=(20, 0))
        self.criar_area_status(frame_status)

    def criar_cabecalho(self, container):
        cabecalho = tk.Frame(container, bg="#F4F6FA")
        cabecalho.pack(fill="x")

        try:
            imagem = Image.open(caminho_recurso("logo2.jpg"))
            imagem.thumbnail((85, 85))
            self.imagem_logo = ImageTk.PhotoImage(imagem)

            label_imagem = tk.Label(cabecalho, image=self.imagem_logo, bg="#F4F6FA")
            label_imagem.pack(side="left", padx=(0, 15))
        except Exception as erro:
            print(f"Não foi possível carregar a imagem: {erro}")

        area_textos = tk.Frame(cabecalho, bg="#F4F6FA")
        area_textos.pack(side="left")

        ttk.Label(area_textos, text="VitórIA", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(
            area_textos,
            text="Automação de tarefas do PJe",
            style="Subtitulo.TLabel",
        ).pack(anchor="w")

    def criar_area_login(self, container):
        card_login = tk.Frame(
            container,
            bg="#FFFFFF",
            highlightbackground="#DCE2EA",
            highlightthickness=1,
            padx=25,
            pady=25,
        )
        card_login.pack(fill="both", expand=True)

        tk.Label(
            card_login,
            text="Acesso ao sistema",
            bg="#FFFFFF",
            fg="#26354A",
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w", pady=(0, 20))

        ttk.Label(card_login, text="Usuário", style="Campo.TLabel").pack(anchor="w")
        self.input_usuario = ttk.Entry(card_login)
        self.input_usuario.pack(fill="x", pady=(5, 15))

        ttk.Label(card_login, text="Senha", style="Campo.TLabel").pack(anchor="w")

        frame_senha = tk.Frame(card_login, bg="#FFFFFF")
        frame_senha.pack(fill="x", pady=(5, 15))

        self.input_senha = ttk.Entry(frame_senha, show="*")
        self.input_senha.pack(side="left", fill="x", expand=True)

        self.botao_mostrar_senha = tk.Button(
            frame_senha,
            text="Mostrar",
            command=self.alternar_visibilidade_senha,
            bg="#FFFFFF",
            fg="#4D6181",
            activebackground="#FFFFFF",
            activeforeground="#26354A",
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=10,
        )
        self.botao_mostrar_senha.pack(side="right")

        self.botao_login = tk.Button(
            card_login,
            text="Entrar",
            command=self.start_login_thread,
            bg="#526A98",
            fg="#FFFFFF",
            activebackground="#40557E",
            activeforeground="#FFFFFF",
            disabledforeground="#D9DDE5",
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 11, "bold"),
            pady=11,
        )
        self.botao_login.pack(fill="x")

        self.label_ajuda_login = tk.Label(
            card_login,
            text=(
                "Após informar usuário e senha, conclua o código 2FA "
                "diretamente na janela do navegador."
            ),
            bg="#FFFFFF",
            fg="#7A8494",
            font=("Segoe UI", 9),
            justify="left",
            wraplength=320,
        )
        self.label_ajuda_login.pack(fill="x", pady=(15, 0))

        self.input_senha.bind("<Return>", lambda _event: self.start_login_thread())
        self.input_usuario.focus_set()

    def criar_area_tarefas(self, container):
        card_tarefas = tk.Frame(
            container,
            bg="#FFFFFF",
            highlightbackground="#DCE2EA",
            highlightthickness=1,
        )
        card_tarefas.pack(fill="both", expand=True)

        cabecalho = tk.Frame(card_tarefas, bg="#FFFFFF", padx=25, pady=20)
        cabecalho.pack(fill="x")

        self.label_tarefas = tk.Label(
            cabecalho,
            text="Tarefas disponíveis",
            bg="#FFFFFF",
            fg="#26354A",
            font=("Segoe UI", 15, "bold"),
        )
        self.label_tarefas.pack(anchor="w")

        self.label_orientacao = tk.Label(
            cabecalho,
            text="Faça o login para habilitar as tarefas.",
            bg="#FFFFFF",
            fg="#7A8494",
            font=("Segoe UI", 10),
            justify="left",
            wraplength=550,
        )
        self.label_orientacao.pack(anchor="w", pady=(4, 0))

        tk.Frame(card_tarefas, bg="#E5E9F0", height=1).pack(fill="x")

        area_scroll = tk.Frame(card_tarefas, bg="#FFFFFF")
        area_scroll.pack(fill="both", expand=True)

        self.canvas_tarefas = tk.Canvas(area_scroll, bg="#FFFFFF", highlightthickness=0)
        self.canvas_tarefas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(area_scroll, orient="vertical", command=self.canvas_tarefas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas_tarefas.configure(yscrollcommand=scrollbar.set)

        self.frame_botoes_tarefas = tk.Frame(
            self.canvas_tarefas,
            bg="#FFFFFF",
            padx=25,
            pady=20,
        )

        self.janela_canvas_tarefas = self.canvas_tarefas.create_window(
            (0, 0),
            window=self.frame_botoes_tarefas,
            anchor="nw",
        )

        self.frame_botoes_tarefas.bind("<Configure>", self.atualizar_scroll_tarefas)
        self.canvas_tarefas.bind("<Configure>", self.ajustar_largura_scroll_tarefas)
        self.canvas_tarefas.bind("<Enter>", self.ativar_scroll_mouse)
        self.canvas_tarefas.bind("<Leave>", self.desativar_scroll_mouse)

        tarefas = [
            (
                "Visualizar expediente DJE",
                "Verifica a publicação dos expedientes no DJE.",
                self.start_visualizaDJE_thread,
            ),
            (
                "Aplicar etiqueta META 02 - 70%",
                "Pesquisa os processos e aplica a etiqueta correspondente.",
                self.start_etiqueta_meta2_thread,
            ),
            (
                "Verificar baixa definitiva",
                "Analisa se os processos possuem o movimento de baixa definitiva.",
                self.start_etiqueta_proc_baixa,
            ),
            (
                "Processo Julgado",
                "Finaliza os processos já julgados da tarefa 'Processo Julgado'.",
                self.start_procjulgado_thread,
            ),
        ]

        self.botoes_tarefas = []
        for titulo, descricao, comando in tarefas:
            self.criar_item_tarefa(titulo, descricao, comando)

    def criar_item_tarefa(self, titulo, descricao, comando):
        item = tk.Frame(
            self.frame_botoes_tarefas,
            bg="#F8F9FC",
            highlightbackground="#DCE2EA",
            highlightthickness=1,
            padx=18,
            pady=15,
        )
        item.pack(fill="x", pady=(0, 12))

        tk.Label(
            item,
            text=titulo,
            bg="#F8F9FC",
            fg="#26354A",
            font=("Segoe UI", 11, "bold"),
            anchor="w",
            justify="left",
        ).pack(fill="x")

        tk.Label(
            item,
            text=descricao,
            bg="#F8F9FC",
            fg="#6B7587",
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
            wraplength=550,
        ).pack(fill="x", pady=(5, 12))

        botao = tk.Button(
            item,
            text="Executar tarefa",
            command=comando,
            state="disabled",
            bg="#E8ECF2",
            fg="#26354A",
            activebackground="#D9E0EA",
            activeforeground="#26354A",
            disabledforeground="#949CAA",
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            pady=8,
        )
        botao.pack(fill="x")
        self.botoes_tarefas.append(botao)

    def criar_area_status(self, container):
        frame_status = tk.Frame(
            container,
            bg="#EEF2F8",
            highlightbackground="#DCE2EA",
            highlightthickness=1,
            padx=15,
            pady=12,
        )
        frame_status.pack(fill="x")

        tk.Label(
            frame_status,
            text="Status",
            bg="#EEF2F8",
            fg="#26354A",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")

        self.label_status = tk.Label(
            frame_status,
            text="Aguardando login.",
            bg="#EEF2F8",
            fg="#596579",
            font=("Segoe UI", 10),
            anchor="w",
            justify="left",
            wraplength=1000,
        )
        self.label_status.pack(fill="x", pady=(4, 0))

        self.barra_progresso = ttk.Progressbar(frame_status, mode="indeterminate")

    def atualizar_scroll_tarefas(self, _event=None):
        self.canvas_tarefas.configure(scrollregion=self.canvas_tarefas.bbox("all"))

    def ajustar_largura_scroll_tarefas(self, event):
        self.canvas_tarefas.itemconfigure(self.janela_canvas_tarefas, width=event.width)

    def ativar_scroll_mouse(self, _event=None):
        self.canvas_tarefas.bind_all("<MouseWheel>", self.rolar_tarefas)

    def desativar_scroll_mouse(self, _event=None):
        self.canvas_tarefas.unbind_all("<MouseWheel>")

    def rolar_tarefas(self, event):
        self.canvas_tarefas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def alternar_visibilidade_senha(self):
        self.senha_visivel = not self.senha_visivel

        if self.senha_visivel:
            self.input_senha.configure(show="")
            self.botao_mostrar_senha.configure(text="Ocultar")
        else:
            self.input_senha.configure(show="*")
            self.botao_mostrar_senha.configure(text="Mostrar")

    def atualizar_status(self, mensagem, tipo="normal"):
        cores = {
            "normal": "#596579",
            "sucesso": "#217A4D",
            "erro": "#B42318",
            "aviso": "#9A6700",
        }
        self.label_status.configure(text=mensagem, fg=cores.get(tipo, cores["normal"]))

    def iniciar_carregamento(self):
        self.barra_progresso.pack(fill="x", pady=(10, 0))
        self.barra_progresso.start(10)

    def finalizar_carregamento(self):
        self.barra_progresso.stop()
        self.barra_progresso.pack_forget()

    def alterar_estado_tarefas(self, estado):
        for botao in self.botoes_tarefas:
            botao.configure(state=estado)

    def start_login_thread(self):
        if self.login_em_andamento:
            return

        if self.tarefa_em_andamento:
            self.atualizar_status("Aguarde a tarefa atual terminar.", "aviso")
            return

        usuario = self.input_usuario.get().strip()
        senha = self.input_senha.get()

        if not usuario or not senha:
            self.atualizar_status("Preencha o usuário e a senha.", "aviso")
            return

        self.login_em_andamento = True
        self.navegador = None

        self.botao_login.configure(state="disabled", text="Aguardando login...")
        self.alterar_estado_tarefas("disabled")

        self.label_orientacao.configure(
            text="Conclua o login e informe o código 2FA diretamente no navegador.",
            fg="#9A6700",
        )
        self.atualizar_status(
            (
                "Informe o código 2FA no navegador, caso seja solicitado. "
                "O sistema está aguardando a abertura da tela principal do PJe."
            ),
            "aviso",
        )

        self.iniciar_carregamento()
        self.window.update_idletasks()

        thread = Thread(target=self.login, args=(usuario, senha), daemon=True)
        thread.start()

    def login(self, usuario, senha):
        try:
            print("Iniciando login...")
            navegador = Inicial().login(usuario, senha)

            if navegador:
                print("Login retornado para a interface.")
                self.fila_resultados.put(("login_sucesso", navegador))
            else:
                self.fila_resultados.put(("login_erro", "O navegador não foi retornado após o login."))
        except Exception as erro:
            print(f"Erro durante o login: {erro!r}")
            self.fila_resultados.put(("login_erro", f"Erro ao realizar login: {erro}"))

    def start_visualizaDJE_thread(self):
        self.iniciar_tarefa(
            nome="Visualizando expediente DJE",
            funcao=Tarefa_visualizaDJE().executa,
        )

    def start_etiqueta_meta2_thread(self):
        self.iniciar_tarefa(
            nome="Aplicando etiqueta META 02 - 70%",
            funcao=Etiqueta_meta2_70().executa,
        )

    def start_etiqueta_proc_baixa(self):
        self.iniciar_tarefa(
            nome="Verificando baixa definitiva",
            funcao=ProcBaixa().executa,
        )
    
    def start_procjulgado_thread(self):
        self.iniciar_tarefa(
            nome="Verificando processos julgados",
            funcao=ProcJulgado().executa,
        )

    def iniciar_tarefa(self, nome, funcao):
        if self.login_em_andamento:
            self.atualizar_status(
                "O login ainda não foi confirmado. Conclua o código 2FA no navegador.",
                "aviso",
            )
            return

        if self.tarefa_em_andamento:
            self.atualizar_status("Já existe uma tarefa em execução.", "aviso")
            return

        if not self.navegador:
            self.atualizar_status(
                "Faça o login e conclua o código 2FA antes de selecionar uma tarefa.",
                "erro",
            )
            return

        self.tarefa_em_andamento = True
        self.alterar_estado_tarefas("disabled")
        self.botao_login.configure(state="disabled")
        self.atualizar_status(f"{nome}. Aguarde...", "normal")
        self.iniciar_carregamento()

        thread = Thread(target=self.executar_tarefa, args=(funcao,), daemon=True)
        thread.start()

    def executar_tarefa(self, funcao):
        try:
            resposta = funcao(self.navegador)
            if not resposta:
                resposta = "Tarefa concluída com sucesso."
            self.fila_resultados.put(("tarefa_sucesso", resposta))
        except Exception as erro:
            print("ERRO NA EXECUÇÃO DA TAREFA:")
            print(repr(erro))
            self.fila_resultados.put(("tarefa_erro", f"Erro durante a execução: {erro}"))

    def processar_fila(self):
        try:
            while True:
                tipo, resultado = self.fila_resultados.get_nowait()

                if tipo == "login_sucesso":
                    self.navegador = resultado
                    self.login_em_andamento = False
                    self.botao_login.configure(state="normal", text="Entrar novamente")
                    self.alterar_estado_tarefas("normal")
                    self.finalizar_carregamento()
                    self.label_orientacao.configure(
                        text="Login confirmado. Selecione uma tarefa.",
                        fg="#217A4D",
                    )
                    self.atualizar_status(
                        "Login e autenticação 2FA concluídos com sucesso.",
                        "sucesso",
                    )

                elif tipo == "login_erro":
                    self.navegador = None
                    self.login_em_andamento = False
                    self.botao_login.configure(state="normal", text="Entrar")
                    self.alterar_estado_tarefas("disabled")
                    self.finalizar_carregamento()
                    self.label_orientacao.configure(
                        text="Não foi possível confirmar o login.",
                        fg="#B42318",
                    )
                    self.atualizar_status(resultado, "erro")

                elif tipo == "tarefa_sucesso":
                    self.tarefa_em_andamento = False
                    self.botao_login.configure(state="normal")
                    self.alterar_estado_tarefas("normal")
                    self.finalizar_carregamento()
                    self.atualizar_status(str(resultado), "sucesso")

                elif tipo == "tarefa_erro":
                    self.tarefa_em_andamento = False
                    self.botao_login.configure(state="normal")
                    if self.navegador:
                        self.alterar_estado_tarefas("normal")
                    self.finalizar_carregamento()
                    self.atualizar_status(resultado, "erro")

        except Empty:
            pass

        if self.window:
            self.window.after(100, self.processar_fila)

    def fechar_programa(self):
        if self.tarefa_em_andamento:
            confirmar = messagebox.askyesno(
                "Encerrar programa",
                "Existe uma tarefa em execução. Deseja encerrar mesmo assim?",
            )
            if not confirmar:
                return

        try:
            if self.navegador:
                self.navegador.quit()
        except Exception:
            pass

        self.window.destroy()


if __name__ == "__main__":
    Interface().execute()