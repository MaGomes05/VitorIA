import time
import re

from datetime import datetime

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utilitarios import (
    caminho_arquivo,
    clicar_js,
    criar_wait,
    extrair_numero_processo,
    normalizar_texto,
    trocar_aba,
    trocar_para_iframe,
)

from config import DOCUMENTO_PROCURADO

# ============================================================
# TAREFA: FINALIZAR PROCESSOS JULGADOS
# ============================================================

class ProcJulgado:
    """
    Automação da tarefa "Processo julgado".

    Fluxo:
    1. Seleciona o perfil Assessor-Chefe de Plenário.
    2. Abre a tarefa Processo julgado no PJe.
    3. Para cada processo:
       - abre o processo;
       - abre os autos em uma segunda aba;
       - consulta se tem acórdão;
       - fecha somente a aba dos autos;
       - volta para a tarfea no PJe;
       - finaliza ou mantém o processo na tarefa.
    """

    XPATH_MENU_PERFIL = "/html/body/nav/div/div[2]/ul/li/a"
    XPATH_CAMPO_PERFIL = (
        "/html/body/nav/div/div[2]/ul/li/div/form/div/"
        "div/table[1]/tbody/tr/td/input"
    )

    def __init__(self):
        self.aba_pje = None

    def executa(self, navegador):
        wait = criar_wait(navegador)

        self.aba_pje = navegador.current_window_handle

        self.selecionar_perfil(wait, navegador)
        self.abrir_tarefa(wait, navegador)
        self.processar_processos(wait, navegador)

        return "Tarefa 'Processo julgado' concluída."

    def selecionar_perfil(self, wait, navegador) -> None:
        trocar_aba(navegador, self.aba_pje)
        navegador.switch_to.default_content()

        # Abre o seletor de perfis
        botao_perfis = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, self.XPATH_MENU_PERFIL)
            )
        )
        clicar_js(navegador, botao_perfis)

        # Pesquisa pelo perfil
        campo = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, self.XPATH_CAMPO_PERFIL)
            )
        )

        campo.clear()
        campo.send_keys("Assessor-Chefe de Plenário")

        # Aguarda a tabela de resultados ser atualizada
        xpath_linhas = (
            "/html/body/nav/div/div[2]/ul/li/div/form/div/"
            "div/table[2]/tbody/tr"
        )

        try:
            WebDriverWait(
                navegador,
                30,
                ignored_exceptions=(
                    StaleElementReferenceException,
                ),
            ).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, xpath_linhas)
                )
            )

            time.sleep(1)

            linhas = navegador.find_elements(
                By.XPATH,
                xpath_linhas,
            )

            for linha in linhas:
                texto_linha = linha.text.strip().lower()

                print(f"Perfil encontrado: {linha.text.strip()}")

                if (
                    "assessor-chefe" in texto_linha
                    and "plenário" in texto_linha
                ):
                    # Procura o link na célula do nome do perfil,
                    # evitando clicar na estrela de favorito.
                    links_perfil = linha.find_elements(
                        By.XPATH,
                        "./td[2]//a"
                    )

                    if not links_perfil:
                        continue

                    # Localiza novamente a linha para evitar elemento obsoleto
                    linhas_atualizadas = navegador.find_elements(
                        By.XPATH,
                        xpath_linhas,
                    )

                    for linha_atualizada in linhas_atualizadas:
                        texto_atualizado = (
                            linha_atualizada.text.strip().lower()
                        )

                        if (
                            "assessor-chefe" in texto_atualizado
                            and "plenário" in texto_atualizado
                        ):
                            link_perfil = linha_atualizada.find_element(
                                By.XPATH,
                                "./td[2]//a"
                            )

                            clicar_js(
                                navegador,
                                link_perfil,
                            )

                            print(
                                "Perfil 'Assessor-Chefe de Plenário' "
                                "selecionado."
                            )

                            navegador.switch_to.default_content()

                            WebDriverWait(
                                navegador,
                                30,
                            ).until(
                                EC.presence_of_element_located(
                                    (By.ID, "ngFrame")
                                )
                            )

                            return

            raise RuntimeError(
                "O perfil 'Assessor-Chefe de Plenário' "
                "não foi encontrado entre os resultados."
            )

        except TimeoutException as erro:
            raise RuntimeError(
                "A lista de perfis não apareceu após a pesquisa."
            ) from erro

    def abrir_tarefa(self, wait, navegador) -> None:
        trocar_aba(navegador, self.aba_pje)
        trocar_para_iframe(
            navegador,
            wait,
            By.ID,
            "ngFrame",
        )

        indice = 1

        while True:
            xpath_tarefa = (
                "/html/body/app-root/selector/div/div/div[2]/"
                "right-panel/div/div/div[3]/tarefas/div/div[3]/"
                f"div[{indice}]/div/a/div/span[1]"
            )

            try:
                elemento = WebDriverWait(
                    navegador,
                    10,
                ).until(
                    EC.presence_of_element_located(
                        (By.XPATH, xpath_tarefa)
                    )
                )
            except TimeoutException as erro:
                raise RuntimeError(
                    "A tarefa 'Processo julgado' "
                    "não foi encontrada."
                ) from erro

            texto_completo = elemento.text.strip()
            texto_sem_quantidade = re.match(
                r"^[^\d]*",
                texto_completo,
            ).group().strip()

            if texto_sem_quantidade == "Processo julgado":
                elemento = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, xpath_tarefa)
                    )
                )

                clicar_js(
                    navegador,
                    elemento
                )

                print(
                    "Tarefa 'Processo julgado' aberta."
                )

                time.sleep(2)
                return

            indice += 1

    def processar_processos(self, wait, navegador) -> None:
        quantidade = self.obter_quantidade_processos(wait)

        if quantidade is None:
            raise RuntimeError(
                "A quantidade de processos não foi encontrada."
            )

        print(f"Quantidade de processos: {quantidade}")

        indice_lista = 1

        for numero_ordem in range(1, quantidade + 1):
            print(
                f"Processando {numero_ordem} de {quantidade}."
            )

            indice_lista = self.processar_um_processo(
                wait=wait,
                navegador=navegador,
                indice_lista=indice_lista,
            )

            time.sleep(2)

        print("Todos os processos foram percorridos.")

    @staticmethod
    def obter_quantidade_processos(wait):
        xpath_quantidade = (
            "/html/body/app-root/selector/div/div/div[2]/"
            "right-panel/div/processos-tarefa/div[1]/div[1]/"
            "filtro-tarefas/div/div[1]/div[2]/span"
        )

        elemento = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, xpath_quantidade)
            )
        )

        correspondencia = re.search(r"\d+", elemento.text)
        return int(correspondencia.group()) if correspondencia else None

    @staticmethod
    def xpath_processo(indice: int) -> str:
        return (
            "/html/body/app-root/selector/div/div/div[2]/"
            "right-panel/div/processos-tarefa/div[1]/div[2]/"
            "div/div[1]/p-datalist/div/div/ul/"
            f"li[{indice}]/processo-datalist-card/div/div[3]/"
            "a/div/span[2]"
        )

    def processar_um_processo(
        self,
        wait,
        navegador,
        indice_lista: int,
    ) -> int:
        # Garante que estamos na aba principal do PJe
        trocar_aba(navegador, self.aba_pje)
        trocar_para_iframe(
            navegador,
            wait,
            By.ID,
            "ngFrame",
        )

        xpath_processo = self.xpath_processo(
            indice_lista
        )

        elemento_processo = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, xpath_processo)
            )
        )

        numero_processo = extrair_numero_processo(
            elemento_processo.text
        )

        if not numero_processo:
            raise RuntimeError(
                "Número do processo não encontrado no cartão."
            )

        clicar_js(
            navegador,
            elemento_processo
        )

        print(
            f"Número do processo: {numero_processo}"
        )

        # Abre os autos e verifica se existe acórdão
        existe_certidao_julgamento = self.verifica_certidao_julgamento(
            wait,
            navegador,
        )

        # Depois da consulta, volta à aba principal do PJe
        trocar_aba(
            navegador,
            self.aba_pje
        )

        if existe_certidao_julgamento:
            self.finalizar_processo(
                wait,
                navegador
            )

            data_atual = datetime.now().strftime(
                "%d-%m-%Y"
            )

            self.log_processos(
                numero_processo,
                data_atual,
            )

            # Como o processo sai da lista, mantém o mesmo índice
            time.sleep(10)
            return indice_lista

        print(
            f"Processo {numero_processo} ainda não possui acórdão."
        )

        # Como o processo continua na lista, avança o índice
        return indice_lista + 1
    
    def verifica_certidao_julgamento(
        self,
        wait,
        navegador,
    ) -> bool:
        """
        Abre os autos, pesquisa por acórdão no texto visível da página,
        fecha somente a aba dos autos e volta à aba principal do PJe.
        """

        trocar_aba(
            navegador,
            self.aba_pje
        )

        trocar_para_iframe(
            navegador,
            wait,
            By.ID,
            "ngFrame",
        )

        xpath_abrir_autos = (
            "/html/body/app-root/selector/div/div/div[2]/"
            "right-panel/div/processos-tarefa/div[2]/"
            "conteudo-tarefa/div[1]/div/div/div[2]/"
            "button[3]/i"
        )

        abas_antes = set(
            navegador.window_handles
        )

        botao_autos = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, xpath_abrir_autos)
            )
        )

        clicar_js(
            navegador,
            botao_autos
        )

        WebDriverWait(
            navegador,
            30,
        ).until(
            lambda driver: len(
                set(driver.window_handles) - abas_antes
            ) == 1
        )

        abas_novas = (
            set(navegador.window_handles) - abas_antes
        )

        aba_autos = abas_novas.pop()

        try:
            trocar_aba(
                navegador,
                aba_autos
            )

            navegador.switch_to.default_content()

            WebDriverWait(
                navegador,
                30,
            ).until(
                EC.presence_of_element_located(
                    (By.TAG_NAME, "body")
                )
            )

            # Dá tempo para a árvore/documentos serem carregados.
            time.sleep(3)

            existe_certidao_julgamento = self.procurar_certidao_julgamento_pagina(
                navegador
            )

            if existe_certidao_julgamento:
                print("Encontrado: Certidão de Julgamento")
            else:
                print("Certidão de Julgamento não encontrada.")

            return existe_certidao_julgamento

        finally:
            if aba_autos in navegador.window_handles:
                trocar_aba(
                    navegador,
                    aba_autos
                )
                navegador.close()

            trocar_aba(
                navegador,
                self.aba_pje
            )
    
    def procurar_certidao_julgamento_pagina(
        self,
        navegador,
    ) -> bool:
        """
        Procura o documento 'certidão de julgamento' no conteúdo principal e nos iframes.
        """

        navegador.switch_to.default_content()

        # Primeiro verifica o conteúdo principal da página.
        texto_principal = navegador.execute_script(
            "return document.body ? document.body.innerText : '';"
        )

        texto_normalizado = normalizar_texto(
            texto_principal or ""
        )

        print(
            "Texto principal contém 'certidao de julgamento':",
            DOCUMENTO_PROCURADO in texto_normalizado
        )

        if DOCUMENTO_PROCURADO in texto_normalizado:
            self.imprimir_trechos_certidao_julgamento(
                texto_principal
            )
            return True

        # Depois verifica possíveis iframes.
        iframes = navegador.find_elements(
            By.TAG_NAME,
            "iframe"
        )

        print(
            f"Quantidade de iframes nos autos: {len(iframes)}"
        )

        for indice in range(len(iframes)):
            try:
                navegador.switch_to.default_content()

                # Localiza novamente para evitar elemento obsoleto.
                iframes_atualizados = navegador.find_elements(
                    By.TAG_NAME,
                    "iframe"
                )

                navegador.switch_to.frame(
                    iframes_atualizados[indice]
                )

                texto_iframe = navegador.execute_script(
                    "return document.body ? document.body.innerText : '';"
                )

                texto_iframe_normalizado = normalizar_texto(
                    texto_iframe or ""
                )

                print(
                    f"Iframe {indice} contém 'certidao de julgamento':",
                    DOCUMENTO_PROCURADO in texto_iframe_normalizado
                )

                if DOCUMENTO_PROCURADO in texto_iframe_normalizado:
                    self.imprimir_trechos_certidao_julgamento(
                        texto_iframe
                    )

                    navegador.switch_to.default_content()
                    return True

            except (
                StaleElementReferenceException,
                NoSuchElementException,
            ):
                continue

        navegador.switch_to.default_content()
        return False
    
    @staticmethod
    def imprimir_trechos_certidao_julgamento(texto: str) -> None:
        """
        Mostra no terminal as linhas em que aparece a palavra acórdão.
        """

        for linha in texto.splitlines():
            if DOCUMENTO_PROCURADO in normalizar_texto(linha):
                print(
                    f"Trecho encontrado: {linha.strip()}"
                )
    
    def finalizar_processo(self, wait, navegador) -> None:
        trocar_aba(navegador, self.aba_pje)
        trocar_para_iframe(
            navegador,
            wait,
            By.ID,
            "ngFrame",
        )

        botao_transicao = wait.until(
            EC.element_to_be_clickable(
                (By.ID, "btnTransicoesTarefa")
            )
        )
        clicar_js(navegador, botao_transicao)

        xpath_opcao = (
            "/html/body/app-root/selector/div/div/div[2]/"
            "right-panel/div/processos-tarefa/div[2]/"
            "conteudo-tarefa/div[1]/div/div/div[2]/"
            "div[2]/ul/li/a"
        )

        opcao = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, xpath_opcao)
            )
        )
        clicar_js(navegador, opcao)

    @staticmethod
    def log_processos(numero_processo: str, data_atual: str) -> None:
        nome_arquivo = f"processos_julgados_finalizados_{data_atual}.txt"
        caminho = caminho_arquivo(nome_arquivo)

        with caminho.open("a", encoding="utf-8") as arquivo:
            arquivo.write(f"{numero_processo}\n")

        print(
            f"Processo {numero_processo} salvo em {nome_arquivo}."
        )