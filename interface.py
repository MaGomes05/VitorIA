from tkinter import *
from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk
from threading import Thread
from tarefas import Inicial
from tarefas import Tarefa_visualizaDJE
from tarefas import Etiqueta_meta2_70
from tarefas import ProcBaixa

class Interface:

    def __init__(self):
        self.navegador = None
        self.login_thread = None
    
    # Execução da interface
    def execute(self):
        # Inicializa a janela principal
        window = Tk()
        window.title("Menu VitórIA")
        window.geometry("500x500+1000+50")
        window.config(bg="#F7F7EF")

        imagem_png = Image.open("logo2.jpg")
        imagem_png = imagem_png.resize((150, 150))
        imagem_tk = ImageTk.PhotoImage(imagem_png)

        label_imagem = Label(window, image=imagem_tk)
        label_imagem.pack()

        # Adiciona um rótulo para exibir texto
        self.texto = Label(window, text=" ")
        self.texto.pack()

        # Adiciona a solicitação do usuário
        label_usuario = Label(window, text="Usuário:")
        label_usuario.pack()

        # Caixa de entrada do usuário
        self.input_usuario = ttk.Entry(window)
        self.input_usuario.pack()

        # Adiciona a solicitação da senha
        label_senha = Label(window, text="Senha:")
        label_senha.pack()

        # Caixa de entrada da senha
        self.input_senha = ttk.Entry(window, show="*")
        self.input_senha.pack()

        button = tk.Button(window, text='Entrar', bg="#5C719D", fg="white", command=self.start_login_thread)
        button.pack(pady=10)

        # Adiciona um rótulo para exibir texto
        self.texto2 = Label(window, text="------CLIQUE EM ENTRAR E AGUARDE PARA SELECIONAR A TAREFA------")
        self.texto2.pack()
        self.texto3 = Label(window, text="Tarefa:")
        self.texto3.pack()

        # Botões para as tarefas
        button1 = tk.Button(window, text='Visualizar expediente DJE', width=22, height=1, bg="#D7D7D7", fg="black", command=self.start_visualizaDJE_thread)
        button1.pack(pady=5)
        button2 = tk.Button(window, text='Etiqueta META 02 - 70%', width=22, height=1, bg="#D7D7D7", fg="black", command=self.start_etiqueta_meta2_thread)
        button2.pack(pady=5)
        button3= tk.Button(window, text='Verifica Baixa', width=22, height=1, bg="#D7D7D7", fg="black", command=self.start_etiqueta_proc_baixa)
        button3.pack(pady=5)

        self.texto4 = Label(window, text="")
        self.texto4.pack()

        # Inicia o loop da interface gráfica
        window.mainloop()

    # Checa o andamento da thread de login
    def check_login_thread(self):
        if self.login_thread and self.login_thread.is_alive():
            # Se a thread ainda está rodando, checa novamente depois de 100ms
            self.texto.after(100, self.check_login_thread)
        else:
            if self.navegador:
                self.texto2.config(text="------SELECIONE A TAREFA------")
            else:
                self.texto2.config(text="-----------------------")

    # Realiza o login do usuário
    def login(self, usuario, senha):
        self.navegador = Inicial().login(usuario, senha)
        self.texto.config(text="Login efetuado")
        self.texto2.config(text="------SELECIONE A TAREFA------")

    def start_login_thread(self):
        usuario = self.input_usuario.get()
        senha = self.input_senha.get()

        thread = Thread(target=self.login, args=(usuario, senha))
        thread.start()

        self.check_login_thread()    

    # Inicia as threads de execução da tarefa
    def start_visualizaDJE_thread(self):
        if self.navegador:
            thread2 = Thread(target=self.visualizaDJE)
            thread2.start()
        else:
            self.texto.config(text="Erro ao inicializar o navegador.")

    # Executa a tarefa Visualizar expediente DJE
    def visualizaDJE(self):
        resposta = Tarefa_visualizaDJE().executa(self.navegador)
        self.navegador = None
        self.texto4.config(text=resposta)

    # Executa a estiqueta meta 2
    def etiqueta_meta2(self):
        resposta = Etiqueta_meta2_70().executa(self.navegador)
        self.navegador = None
        self.texto4.config(text=resposta)


    def start_etiqueta_meta2_thread(self):
        if self.navegador:
            thread3 = Thread(target=self.etiqueta_meta2)
            thread3.start()
        else:
            self.texto.config(text="Erro ao inicializar o navegador.")

    def proc_baixa(self):
        resposta = ProcBaixa().executa(self.navegador)
        self.navegador = None
        self.texto4.config(text=resposta)

    def start_etiqueta_proc_baixa(self):
        if self.navegador:
            thread4 = Thread(target=self.proc_baixa)
            thread4.start()
        else:
            self.texto.config(text="Erro ao inicializar o navegador.")