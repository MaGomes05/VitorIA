import time
import re
import os
import pyperclip
import pandas as pd
from datetime import datetime
from openpyxl import Workbook, load_workbook
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
#Este é um código de manipulção para a tarefa "Visualizar exepediente DJE"

class Inicial:

    # Login do usuário 
    def login(self, usuario, senha):
        servicoF = Service(executable_path='geckodriver.exe')
        navegador = webdriver.Firefox(service=servicoF)
        wait = WebDriverWait(navegador, 20)
        
        # Abrindo o PJE de treinamento
        navegador.get("https://pje.tre-pb.jus.br/pje/login.seam")

        try:
            wait = WebDriverWait(navegador, 10)
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'ssoFrame')))
            print("Entrou no iframe com sucesso.")
        except TimeoutException:
            print("Iframe 'ssoFrame' não encontrado. Continuando sem mudar para ele.")

        # Realiza o login
        user = navegador.find_element(By.XPATH, '//*[@id="username"]')
        user.send_keys(usuario)
        pssw = navegador.find_element(By.XPATH, '//*[@id="password"]')
        pssw.send_keys(senha)
        navegador.find_element(By.XPATH, '//input[@value="Entrar"]').click()

        navegador.switch_to.default_content()
        time.sleep(3)

        # Pula a verificação do mobile caso exista
        try:
            elemento = navegador.find_element(By.XPATH, '/html/body/div[5]/div/div/div/div[2]/div/div/div/form/div/div[2]/div[4]/a')
            elemento.click()
        except NoSuchElementException:
            print("Elemento não encontrado, prosseguindo.")

        return navegador

class Tarefa_visualizaDJE:
    
    # Comparação das datas
    def compara_data(self, data_processo, data_comp):
        if data_processo <= data_comp:
            return(True)
        else:
            return(False)
    
    # Salva os arquivos que foram finalizados da tarefa
    def log_processos(self, numero_processo, data_atual):
        print("entrei")
        nome_arquivo = f"processos_manipulados_{data_atual}.txt"
        caminho_arquivo = os.path.join(os.getcwd(), nome_arquivo)

        with open(caminho_arquivo, 'a') as arquivo:
            arquivo.write(f"{numero_processo}\n")

        print(f"Processo {numero_processo} salvo em {nome_arquivo}.")

    def executa(self, navegador):
        wait = WebDriverWait(navegador, 10)
        self.perfil(wait, navegador)
        self.tarefa(wait, navegador)

        navegador.quit()
        return "-----Executei a tarefa-----"

    # Seleção do perfil adequado para a tarefa
    def perfil(self, wait, navegador):
        # Seleção do perfil
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/nav/div/div[2]/ul/li/a')))
        navegador.find_element(By.XPATH, '/html/body/nav/div/div[2]/ul/li/a').click()
        navegador.find_element(By.XPATH, '/html/body/nav/div/div[2]/ul/li/div/form/div/div/table[1]/tbody/tr/td/input').send_keys('coordenador de processamento')
        time.sleep(2)

        try:
            perfil = wait.until(EC.presence_of_element_located((By.XPATH, f'/html/body/nav/div/div[2]/ul/li/div/form/div/div/table[2]/tbody/tr/td[2]/a')))
            texto_completo = perfil.text
        except NoSuchElementException:
            texto_completo = " "
            print("Elemento não encontrado.")
       
        if "Coordenador de Processamento" in texto_completo:
            navegador.find_element(By.XPATH, f'/html/body/nav/div/div[2]/ul/li/div/form/div/div/table[2]/tbody/tr/td[2]/a').click()                   
 
    # Seleção da tarefa
    def tarefa(self, wait, navegador):
        abas = navegador.window_handles
        # Ajusta o ambiente para a abertura da tarefa
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'ngFrame')))
        #print("iFrame carregado. Contexto mudado para o iFrame.")
        time.sleep(2)

        # Entra na tarefa
        i = 1
        while(i):
            xpath_tarefa = f'/html/body/app-root/selector/div/div/div[2]/right-panel/div/div/div[3]/tarefas/div/div[3]/div[{i}]/div/a/div/span[1]'
            processo_elemento = wait.until(EC.presence_of_element_located((By.XPATH, xpath_tarefa)))
            texto_completo = processo_elemento.text.strip()
            texto = re.match(r'^[^\d]*', texto_completo).group().strip()

            if(texto == "Visualizar expediente DJE"):
                elemento = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_tarefa)))
                navegador.execute_script("arguments[0].click();", elemento)#clica para entrar na tarefa
                break    
            
            i += 1

        time.sleep(2)

        # Abertura do DJE
        navegador.execute_script("window.open('');")
        novas_abas = navegador.window_handles
        if len(novas_abas) > len(abas):
            navegador.switch_to.window(novas_abas[-1])
            navegador.get("https://dje-consulta.tse.jus.br/#/dje/calendario?trib=TRE-PB")
            time.sleep(1)
            navegador.switch_to.window(novas_abas[0])
            abas = navegador.window_handles
        else:
            print("Erro ao abrir o DJE")
        
        print("Voltei pro PJE")

        # Seleciona a quantidade de processos para rodar
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'ngFrame')))
        processo_elemento = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/app-root/selector/div/div/div[2]/right-panel/div/processos-tarefa/div[1]/div[1]/filtro-tarefas/div/div[1]/div[2]/span')))
        texto_completo = processo_elemento.text
        qntd_processos_match = re.search(r'\d+', texto_completo)

        if qntd_processos_match:
            i = j = 1
            qntd_processo = int(qntd_processos_match.group())
            print(f"Quantidade de processos: {qntd_processo}")
            
            while(i <= qntd_processo):
                print(f"Processo {i}")
                #print(f"xpath {j}")
                #seleciona o xapth dos processos
                xpath_processo = f'/html/body/app-root/selector/div/div/div[2]/right-panel/div/processos-tarefa/div[1]/div[2]/div/div[1]/p-datalist/div/div/ul/li[{j}]/processo-datalist-card/div/div[3]/a/div/span[2]'
                processo_elemento = wait.until(EC.presence_of_element_located((By.XPATH, xpath_processo)))
                texto_completo = processo_elemento.text 
                #print(f"{texto_completo}") 
                
                try:
                    j = self.visualizarExpedienteDJE(wait, navegador, abas, xpath_processo, j)
                    #print(f"xpath {j}")
                    print(f"Abri {i}")
                except Exception as e:
                    time.sleep(5)                     
                    print(f"Erro ao abrir o processo {i}.")
                    print(f"-----------------Tente manipular esse processo manualmente-----------------")
                    break

                time.sleep(2)
                i = i + 1
                
                if (i == qntd_processo):
                    print("-----------------Todos os processos foram percorridos com sucesso-----------------")
        else:
            print("-----------------Quantidade de processos não encontrada.-----------------")

    # Verificação no DJE
    def verificaDJE(self, wait, navegador, abas, numero_processo):
        navegador.switch_to.window(abas[-1])
        time.sleep(0.5)
        # Definição de valor de data default
        data_default = datetime(2001, 5, 17)

        # Busca pelo pdf
        # navegador.find_element('xpath', '/html/body/app-root/div/app-calendario/div/div[1]/div[2]/div[2]/button').click()
        # time.sleep(20)

        # Seleciona o TRE-PB
        navegador.find_element('xpath', '/html/body/app-root/div/app-calendario/div/div[2]/app-pesquisa/app-pesquisa-form/div/div[1]/div[1]/mat-form-field/div/div[1]/div[3]').click()
        navegador.find_element('xpath', '/html/body/div[2]/div[2]/div/div/div/mat-option[17]/span').click()

        #print(f"processo: {numero_processo}")

        # Preenche o número do processo
        pyperclip.copy(numero_processo) 
        input_element = navegador.find_element('xpath', '//*[@id="mat-input-0"]')
        input_element.clear() 
        input_element.send_keys(Keys.CONTROL, 'v')

        time.sleep(0.5)

        # Clica para pesquisar
        navegador.find_element('xpath', '/html/body/app-root/div/app-calendario/div/div[2]/app-pesquisa/app-pesquisa-form/div/div[5]/button[2]').click()
        time.sleep(8)

        # Salva a data
        try:
            data_elemento = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/app-root/div/app-calendario/div/div[8]/button/span')))
            texto_completo = data_elemento.text
            data_publicacao_match = re.search(r'\d{2}/\d{2}/\d{4}', texto_completo)
            if data_publicacao_match:
                data_publicacao = data_publicacao_match.group()  # Acessar o grupo da correspondência
                print(f"-----------------Data da publicação: {data_publicacao}-----------------")
                data_publicacao = datetime.strptime(data_publicacao, '%d/%m/%Y')
        except Exception as e:                     
            print("-----------------Data não encontrada.-----------------")
            data_publicacao = data_default

        navegador.switch_to.window(abas[0])
        return(data_publicacao)

    # Manipulação de cada processo na tarefa
    def visualizarExpedienteDJE(self, wait, navegador, abas, xpath_processo, j):
        
        # Manipulação da janela utilizada 
        navegador.switch_to.window(navegador.window_handles[0]) #garante que o programa está operando a aba correta
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'ngFrame'))) #verificar se o iframe está ativo e o conteúdo está carregado
        #print("iFrame OK.")

        # Processo a ser verificado
        elemento = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_processo)))
        navegador.execute_script("arguments[0].click();", elemento)
        print(f"XPath do processo atual: {xpath_processo}")

        # Copia o número no processo
        processo_elemento = wait.until(EC.presence_of_element_located((By.XPATH, xpath_processo)))
        texto_completo = processo_elemento.text
        numero_processo_match = re.search(r'\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}', texto_completo)
        if numero_processo_match:
            numero_processo = numero_processo_match.group()
            print(f"-----------------Número do Processo: {numero_processo}-----------------")
        else:
            print("-----------------Número do processo não encontrado.-----------------")
        
        time.sleep(2)

        # Abertura dos autos
        elemento = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/app-root/selector/div/div/div[2]/right-panel/div/processos-tarefa/div[2]/conteudo-tarefa/div[1]/div/div/div[2]/button[3]/i')))
        navegador.execute_script("arguments[0].click();", elemento)

        # Aguarda a abertura de uma nova aba
        time.sleep(2) 
        novas_abas = navegador.window_handles

        # Verificação da quantidade de abas para a mudança de aba correta
        if len(novas_abas) > len(abas):
            navegador.switch_to.window(novas_abas[1])
            print("Nova aba aberta e foco trocado para a nova aba.")
        else:
            print("Não foi possível abrir uma nova aba.")

        # Abre os expedientes
        elemento = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="navbar:linkAbaExpedientes1"]')))
        navegador.execute_script("arguments[0].click();", elemento)

        # Salva a data do expediente
        ind = 1
        while(ind):
            data_elemento = wait.until(EC.presence_of_element_located((By.XPATH, f'/html/body/div[1]/div[2]/div[2]/table/tbody/tr[2]/td/table/tbody/tr/td/div/div/div/div/div/div[2]/span/div/table/tbody/tr[{ind}]/td[1]/span/div/span/div[2]')))
            texto_completo = data_elemento.text
            
            if "Diário Eletrônico" in texto_completo:
                data_processo_match = re.search(r'\d{2}/\d{2}/\d{4}', texto_completo)
                if data_processo_match:
                    data_processo = data_processo_match.group()  # Acessar o grupo da correspondência
                    print(f"-----------------Data do expediente: {data_processo}-----------------")
                    time.sleep(5)
                    data_processo = datetime.strptime(data_processo, '%d/%m/%Y')
                    break
                else:
                    print("-----------------Data não encontrada.-----------------")
                    break
            else:
                ind = ind + 1

        # Fecha a aba dos expedientes e retoma a manipulação da aba da tarefa no PJE
        time.sleep(1)
        navegador.close()
        time.sleep(1)
        abas = navegador.window_handles
        navegador.switch_to.window(abas[0])
        time.sleep(1)

        data_comp = self.verificaDJE(wait, navegador, abas, numero_processo)
        decisao = self.compara_data(data_processo, data_comp)
        print(decisao)

        # Determina se o processo deve ser finalizado na tarefa ou se ainda deve continuar
        if(decisao):
            time.sleep(2)
            navegador.switch_to.window(abas[0])
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'ngFrame'))) 
            #print("iFrame OK.")
            
            # Finaliza a tarefa
            elemento = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btnTransicoesTarefa"]')))
            navegador.execute_script("arguments[0].click();", elemento)
            elemento = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/app-root/selector/div/div/div[2]/right-panel/div/processos-tarefa/div[2]/conteudo-tarefa/div[1]/div/div/div[2]/div[2]/ul/li/a')))
            navegador.execute_script("arguments[0].click();", elemento)
            data_atual = datetime.now().strftime("%d-%m-%Y")
            print(data_atual)
            self.log_processos(numero_processo, data_atual)
            print("salvei")
            time.sleep(10)
            return j
        else:
            time.sleep(2)
            navegador.switch_to.window(abas[0])
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'ngFrame')))
            #print("iFrame OK.")
            time.sleep(2)
            print(f"-----------------Processo {numero_processo} não publicado-----------------")
            return j + 1  

class Etiqueta_meta2_70:

    def executa(self, navegador):
        wait = WebDriverWait(navegador, 10)
        
        for gab in range(1, 7):
            processos = self.manipula_planilha(gab)
            self.seleciona_gabinete(wait, navegador, gab)
            flag = 1

            for numero in processos:
                print(flag)
                print(numero)
                flag = self.pesquisa_processo(wait, navegador, numero, flag) 
                
        navegador.quit()
        return "-----Executei a tarefa-----"
    
    # Seleciona o gabinete para realizar a pesquisa
    def seleciona_gabinete(self, wait, navegador, gab):
    
        if gab == 1:
            # Seleção do perfil
            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/nav/div/div[2]/ul/li/a')))
            navegador.find_element(By.XPATH, '/html/body/nav/div/div[2]/ul/li/a').click()
            navegador.find_element(By.XPATH, '/html/body/nav/div/div[2]/ul/li/div/form/div/div/table[1]/tbody/tr/td/input').send_keys('GABJ01 - Gabinete Jurista 1 / Assessoria / Assessor Chefe')
            time.sleep(2)

            try:
                perfil = wait.until(EC.presence_of_element_located((By.XPATH, f'/html/body/nav/div/div[2]/ul/li/div/form/div/div/table[2]/tbody/tr/td[2]/a')))
                texto_completo = perfil.text
            except NoSuchElementException:
                texto_completo = " "
                print("Elemento não encontrado.")

            if "Assessor Chefe" in texto_completo:
                navegador.find_element(By.XPATH, f'/html/body/nav/div/div[2]/ul/li/div/form/div/div/table[2]/tbody/tr/td[2]/a').click()
                print("Entrei no GABJ01")
                time.sleep(5)
        
        elif gab == 2:
            # Seleção do perfil
            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/nav/div/div[2]/ul/li/a')))
            navegador.find_element(By.XPATH, '/html/body/nav/div/div[2]/ul/li/a').click()
            navegador.find_element(By.XPATH, '/html/body/nav/div/div[2]/ul/li/div/form/div/div/table[1]/tbody/tr/td/input').send_keys('GABJ02 - Gabinete Juiz de Direito 1 / Assessoria / Assessor Chefe')
            time.sleep(2)

            try:
                perfil = wait.until(EC.presence_of_element_located((By.XPATH, f'/html/body/nav/div/div[2]/ul/li/div/form/div/div/table[2]/tbody/tr/td[2]/a')))
                texto_completo = perfil.text
            except NoSuchElementException:
                texto_completo = " "
                print("Elemento não encontrado.")

            if "Assessor Chefe" in texto_completo:
                navegador.find_element(By.XPATH, f'/html/body/nav/div/div[2]/ul/li/div/form/div/div/table[2]/tbody/tr/td[2]/a').click()
                print("Entrei no GABJ02")
                time.sleep(5)

        elif gab == 3:
            # Seleção do perfil
            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/nav/div/div[2]/ul/li/a')))
            navegador.find_element(By.XPATH, '/html/body/nav/div/div[2]/ul/li/a').click()
            navegador.find_element(By.XPATH, '/html/body/nav/div/div[2]/ul/li/div/form/div/div/table[1]/tbody/tr/td/input').send_keys('GABJ03 - Gabinete Jurista 2 / Assessoria / Assessor Chefe')
            time.sleep(2)

            try:
                perfil = wait.until(EC.presence_of_element_located((By.XPATH, f'/html/body/nav/div/div[2]/ul/li/div/form/div/div/table[2]/tbody/tr/td[2]/a')))
                texto_completo = perfil.text
            except NoSuchElementException:
                texto_completo = " "
                print("Elemento não encontrado.")

            if "Assessor Chefe" in texto_completo:
                navegador.find_element(By.XPATH, f'/html/body/nav/div/div[2]/ul/li/div/form/div/div/table[2]/tbody/tr/td[2]/a').click()
                print("Entrei no GABJ03")
                time.sleep(5)

        elif gab == 4:
            # Seleção do perfil
            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/nav/div/div[2]/ul/li/a')))
            navegador.find_element(By.XPATH, '/html/body/nav/div/div[2]/ul/li/a').click()
            navegador.find_element(By.XPATH, '/html/body/nav/div/div[2]/ul/li/div/form/div/div/table[1]/tbody/tr/td/input').send_keys('GABJ04 - Gabinete Juiz de Direito 2 / Assessoria / Assessor Chefe')
            time.sleep(2)

            try:
                perfil = wait.until(EC.presence_of_element_located((By.XPATH, f'/html/body/nav/div/div[2]/ul/li/div/form/div/div/table[2]/tbody/tr/td[2]/a')))
                texto_completo = perfil.text
            except NoSuchElementException:
                texto_completo = " "
                print("Elemento não encontrado.")

            if "Assessor Chefe" in texto_completo:
                navegador.find_element(By.XPATH, f'/html/body/nav/div/div[2]/ul/li/div/form/div/div/table[2]/tbody/tr/td[2]/a').click()
                print("Entrei no GABJ04")
                time.sleep(5)
        
        elif gab == 5:
            # Seleção do perfil
            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/nav/div/div[2]/ul/li/a')))
            navegador.find_element(By.XPATH, '/html/body/nav/div/div[2]/ul/li/a').click()
            navegador.find_element(By.XPATH, '/html/body/nav/div/div[2]/ul/li/div/form/div/div/table[1]/tbody/tr/td/input').send_keys('GABJ05 - Gabinete Vice Presidência / Assessoria / Assessor Chefe')
            time.sleep(2)

            try:
                perfil = wait.until(EC.presence_of_element_located((By.XPATH, f'/html/body/nav/div/div[2]/ul/li/div/form/div/div/table[2]/tbody/tr/td[2]/a')))
                texto_completo = perfil.text
            except NoSuchElementException:
                texto_completo = " "
                print("Elemento não encontrado.")

            if "Assessor Chefe" in texto_completo:
                navegador.find_element(By.XPATH, f'/html/body/nav/div/div[2]/ul/li/div/form/div/div/table[2]/tbody/tr/td[2]/a').click()
                print("Entrei no GABJ05")
                time.sleep(5)

        elif gab == 6:
            # Seleção do perfil
            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/nav/div/div[2]/ul/li/a')))
            navegador.find_element(By.XPATH, '/html/body/nav/div/div[2]/ul/li/a').click()
            navegador.find_element(By.XPATH, '/html/body/nav/div/div[2]/ul/li/div/form/div/div/table[1]/tbody/tr/td/input').send_keys('GABJ06 - Gabinete Juiz Federal / Assessoria / Assessor Chefe')
            time.sleep(2)

            try:
                perfil = wait.until(EC.presence_of_element_located((By.XPATH, f'/html/body/nav/div/div[2]/ul/li/div/form/div/div/table[2]/tbody/tr/td[2]/a')))
                texto_completo = perfil.text
            except NoSuchElementException:
                texto_completo = " "
                print("Elemento não encontrado.")

            if "Assessor Chefe" in texto_completo:
                navegador.find_element(By.XPATH, f'/html/body/nav/div/div[2]/ul/li/div/form/div/div/table[2]/tbody/tr/td[2]/a').click()
                print("Entrei no GABJ06")
                time.sleep(5)

    # Pesquisa o processo dentro do gabinete
    def pesquisa_processo(self, wait, navegador, numero, flag):
        
        verifica = False #variável para verificar a presença do processo no gabinete
        
        #wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'ngFrame')))
        #print("iFrame carregado. Contexto mudado para o iFrame.")
        time.sleep(1)
        print("ok")
        if(flag == 1):
            navegador.switch_to.default_content()
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'ngFrame')))
            print("iFrame carregado. Contexto mudado para o iFrame.")
            navegador.find_element(By.XPATH, '/html/body/app-root/selector/div/div/div[2]/right-panel/div/div/div[3]/tarefas/div/div[1]/div').click()
            print("filtro")

        time.sleep(2)
        print(numero)
        #campo = navegador.find_element(By.XPATH, '/html/body/app-root/selector/div/div/div[2]/right-panel/div/div/div[3]/tarefas/div/div[2]/filtro-tarefas-pendentes/div/form/fieldset/div[1]/input').send_keys(numero)
        
        campo = WebDriverWait(navegador, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/app-root/selector/div/div/div[2]/right-panel/div/div/div[3]/tarefas/div/div[2]/filtro-tarefas-pendentes/div/form/fieldset/div[1]/input'))
        )

        # Limpa o campo
        campo.clear()

        # Insere o novo texto
        campo.send_keys(numero)

        navegador.find_element(By.XPATH, '/html/body/app-root/selector/div/div/div[2]/right-panel/div/div/div[3]/tarefas/div/div[2]/filtro-tarefas-pendentes/div/form/fieldset/div[4]/button[1]').click()
        time.sleep(2)

        # Verifica se o processo está no gabinete
        try:
            elemento = navegador.find_element(By.XPATH, '/html/body/app-root/selector/div/div/div[2]/right-panel/div/div/div[3]/tarefas/div/div[3]/div[1]/div/a/div/span[1]')
            elemento.click()
            verifica = True
        except NoSuchElementException:
            print("Elemento não encontrado, prosseguindo.1")
        try:
            elemento = navegador.find_element(By.XPATH, '/html/body/app-root/selector/div/div/div[2]/right-panel/div/div/div[3]/tarefas/div/div[3]/div/div/a/div/span[1]')
            elemento.click()
            verifica = True
        except NoSuchElementException:
            print("Elemento não encontrado, prosseguindo.2")

        if(verifica):
            flag = self.etiqueta(wait, navegador)
        else:
            flag = 2

        return flag

    # Adiciona a etiqueta no processo encontrado
    def etiqueta(self, wait, navegador):
        
        #wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'ngFrame')))
        #print("iFrame carregado. Contexto mudado para o iFrame.")
        time.sleep(2)

        navegador.find_element(By.XPATH, '/html/body/app-root/selector/div/div/div[2]/right-panel/div/processos-tarefa/div[1]/div[2]/div/div[1]/p-datalist/div/div/ul/li[1]/processo-datalist-card/div/div[2]/button/i').click()
        navegador.find_element(By.XPATH, '/html/body/app-root/selector/div/div/div[2]/right-panel/div/processos-tarefa/div[1]/div[2]/div/div[1]/div[1]/acoes-processos-tarefa/div/div/div/button[2]/i').click()
        navegador.find_element(By.XPATH, '//*[@id="itPesquisarEtiquetas"]').send_keys('META 02 - 70%')
        navegador.find_element(By.XPATH, '/html/body/app-root/selector/div/div/div[2]/right-panel/div/processos-tarefa/div[3]/etiquetar-lote/div/div/div/div[2]/div/pje-selecionar-etiquetas/div/div/table/tbody/tr/td[1]/button/i').click()
        time.sleep(1)
        navegador.find_element(By.XPATH, '/html/body/app-root/selector/div/div/div[2]/right-panel/div/processos-tarefa/div[3]/etiquetar-lote/div/div/div/div[3]/div/button[1]/span').click()
        time.sleep(5)
        navegador.find_element(By.XPATH, '/html/body/app-root/selector/div/div/div[2]/right-panel/div/processos-tarefa/div[3]/etiquetar-lote/div/div/div/div[1]/button/span').click()
        time.sleep(2)
        navegador.find_element(By.XPATH, '/html/body/app-root/selector/div/div/div[1]/side-bar/nav/ul/li[1]/a/i').click()

        return 1
    
    # Manipulação da planilha
    def manipula_planilha(self, gab):
        pasta = "Meta 02 - 70%"
        coluna = "numero"

        base_name = "Metas 2024_GABJ_0"
        suffix = "_Out"
        planilha = f"{base_name}{gab}{suffix}.xlsx"

        df = pd.read_excel(planilha, sheet_name=pasta)

        processos = df[coluna].dropna()
        return processos
    
class ProcBaixa:

    def executa(self, navegador):
        wait = WebDriverWait(navegador, 10)
        
        processos = self.manipula_planilha()
        self.abre_pesquisa(wait, navegador)
        for numero in processos:
            print(numero)
            self.pesquisa_processo(wait, navegador, numero)
                
        navegador.quit()
        return "-----Executei a tarefa-----"
    
    # Manipulação da planilha
    def manipula_planilha(self):
        coluna = "numero"

        planilha = f"analise.xlsx"

        df = pd.read_excel(planilha)

        processos = df[coluna].dropna()
        return processos

    # Abre a parte de pesquisar o processo
    def abre_pesquisa(self, wait, navegador):
        #clica na barra
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/nav/div/div[1]/ul/li/a/span')))
        navegador.find_element(By.XPATH, '/html/body/nav/div/div[1]/ul/li/a/span').click()
        #processo
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div/nav/div[2]/ul/li[2]/a')))
        navegador.find_element(By.XPATH, '/html/body/div[5]/div/nav/div[2]/ul/li[2]/a').click()
        #pesquisar
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div/nav/div[2]/ul/li[2]/div/ul/li[6]/a')))
        navegador.find_element(By.XPATH, '/html/body/div[5]/div/nav/div[2]/ul/li[2]/div/ul/li[6]/a').click()
        #processo
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div/nav/div[2]/ul/li[2]/div/ul/li[6]/div/ul/li[1]/a')))
        navegador.find_element(By.XPATH, '/html/body/div[5]/div/nav/div[2]/ul/li[2]/div/ul/li[6]/div/ul/li[1]/a').click()

        time.sleep(0.5)

    # Pesquisa o processo
    def pesquisa_processo(self, wait, navegador, numero):
        abas = navegador.window_handles

        pyperclip.copy(numero) 
        input_element = navegador.find_element('xpath', '//*[@id="fPP:numeroProcesso:numeroSequencial"]')
        input_element.clear() 
        input_element.send_keys(Keys.CONTROL, 'v')
        navegador.find_element('xpath', '//*[@id="fPP:searchProcessos"]').click()
        time.sleep(3)

        try:
            #abre os autos
            elemento = navegador.find_element(By.XPATH, '//*[starts-with(@id, "fPP:processosTable:") and contains(@id, ":j_id489")]')
            elemento.click()
            baixa = self.verifica_baixa(wait, abas, navegador)
            if baixa:
                self.salvar_processo(numero, "com_baixa")
            else:
                self.salvar_processo(numero, "sem_baixa")
        except NoSuchElementException:
            self.salvar_processo(numero, "nao_encontrado")                     
            print(f"-----------------Processo {numero} não encontrado-----------------")

    # Verifica se existe o movimento de baixa na árvore do processo
    def verifica_baixa(self, wait, abas, navegador):
        time.sleep(2) 
        novas_abas = navegador.window_handles

        if len(novas_abas) > len(abas):
            navegador.switch_to.window(novas_abas[1])
            #print("Nova aba aberta e foco trocado para a nova aba.")
        else:
            print("Não foi possível abrir uma nova aba.")

        elementos = navegador.find_elements(By.CLASS_NAME, "texto-movimento")

        baixa = any("baixa definitiva" in el.text.lower() for el in elementos)

        if baixa:
            print("Encontrado: BAIXA DEFINITIVA")
            time.sleep(0.5)
            navegador.close()
            time.sleep(0.5)
            abas = navegador.window_handles
            navegador.switch_to.window(abas[0])
            time.sleep(0.5)
            return True
        else:
            print("Não encontrado")
            time.sleep(0.5)
            navegador.close()
            time.sleep(0.5)
            abas = navegador.window_handles
            navegador.switch_to.window(abas[0])
            time.sleep(0.5)
            return False

    # Salva o processo na planilha com sua situação correspondente: sembaixa, com baixa ou não encontrado
    def salvar_processo(self, numero_processo, categoria):
        nome_arquivo = "processos.xlsx"
        caminho_arquivo = os.path.join(os.getcwd(), nome_arquivo)

        # Verifica se o arquivo já existe
        if os.path.exists(caminho_arquivo):
            workbook = load_workbook(caminho_arquivo)
            sheet = workbook.active
        else:
            workbook = Workbook()
            sheet = workbook.active
            # Cabeçalhos nas colunas A, B, C
            sheet["A1"] = "Processos Sem Baixa"
            sheet["B1"] = "Processos Com Baixa"
            sheet["C1"] = "Processos Não Encontrados"

        # Define a coluna baseada na categoria
        colunas = {
            "sem_baixa": "A",
            "com_baixa": "B",
            "nao_encontrado": "C"
        }

        if categoria not in colunas:
            print(f"Categoria inválida: {categoria}")
            return

        letra_coluna = colunas[categoria]

        # Encontra a próxima linha vazia na coluna
        linha = 2
        while sheet[f"{letra_coluna}{linha}"].value is not None:
            linha += 1

        # Insere o número do processo
        sheet[f"{letra_coluna}{linha}"] = numero_processo

        # Salva
        workbook.save(caminho_arquivo)
        print(f"Processo {numero_processo} salvo na coluna {letra_coluna} ({categoria}).")