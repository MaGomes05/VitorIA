import re
import time

from datetime import datetime

import pyperclip

from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import URL_DJE
from utilitarios import (
    aceitar_cookies,
    caminho_arquivo,
    clicar_js,
    criar_wait,
    extrair_data,
    extrair_numero_processo,
    trocar_aba,
    trocar_para_iframe,
)

# ============================================================
# TAREFA: VISUALIZAR EXPEDIENTE DJE
# ============================================================

class Tarefa_visualizaDJE:
    """
    Automação da tarefa "Visualizar expediente DJE".

    Fluxo:
    1. Seleciona o perfil Coordenador de Processamento.
    2. Abre a tarefa Visualizar expediente DJE no PJe.
    3. Abre o DJE em uma segunda aba e mantém essa aba aberta.
    4. Para cada processo:
       - volta ao PJe;
       - abre o processo;
       - abre os autos em uma terceira aba;
       - consulta a data do expediente;
       - fecha somente a aba dos autos;
       - vai para a aba do DJE;
       - pesquisa o processo;
       - volta ao PJe;
       - finaliza ou mantém o processo na tarefa.
    """

    XPATH_MENU_PERFIL = "/html/body/nav/div/div[2]/ul/li/a"
    XPATH_CAMPO_PERFIL = (
        "/html/body/nav/div/div[2]/ul/li/div/form/div/"
        "div/table[1]/tbody/tr/td/input"
    )

    def __init__(self):
        self.aba_pje = None
        self.aba_dje = None

    def executa(self, navegador):
        wait = criar_wait(navegador)

        self.aba_pje = navegador.current_window_handle

        self.selecionar_perfil(wait, navegador)
        self.abrir_tarefa(wait, navegador)
        self.abrir_dje(wait, navegador)
        self.processar_processos(wait, navegador)

        return "Tarefa 'Visualizar expediente DJE' concluída."

    def selecionar_perfil(self, wait, navegador) -> None:
        trocar_aba(navegador, self.aba_pje)
        navegador.switch_to.default_content()

        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, self.XPATH_MENU_PERFIL)
            )
        ).click()

        campo = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, self.XPATH_CAMPO_PERFIL)
            )
        )

        campo.clear()
        campo.send_keys("Coordenador de Processamento")

        xpath_link_perfil = (
            "/html/body/nav/div/div[2]/ul/li/div/form/div/"
            "div/table[2]/tbody/tr/td//a["
            "contains("
            "translate(normalize-space(.), "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
            "'abcdefghijklmnopqrstuvwxyz'), "
            "'coordenador de processamento'"
            ")"
            "]"
        )

        try:
            link_perfil = WebDriverWait(
                navegador,
                30,
                ignored_exceptions=(
                    StaleElementReferenceException,
                ),
            ).until(
                EC.element_to_be_clickable(
                    (By.XPATH, xpath_link_perfil)
                )
            )

            navegador.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                link_perfil,
            )

            link_perfil = navegador.find_element(
                By.XPATH,
                xpath_link_perfil,
            )

            navegador.execute_script(
                "arguments[0].click();",
                link_perfil,
            )

            print(
                "Perfil 'Coordenador de Processamento' selecionado."
            )

            navegador.switch_to.default_content()
            WebDriverWait(navegador, 30).until(
                EC.presence_of_element_located(
                    (By.ID, "ngFrame")
                )
            )

        except TimeoutException as erro:
            raise RuntimeError(
                "O perfil 'Coordenador de Processamento' "
                "não apareceu na lista."
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
                    "A tarefa 'Visualizar expediente DJE' "
                    "não foi encontrada."
                ) from erro

            texto_completo = elemento.text.strip()
            texto_sem_quantidade = re.match(
                r"^[^\d]*",
                texto_completo,
            ).group().strip()

            if texto_sem_quantidade == "Visualizar expediente DJE":
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
                    "Tarefa 'Visualizar expediente DJE' aberta."
                )

                time.sleep(2)
                return

            indice += 1

    def abrir_dje(self, wait, navegador) -> None:
        # Começa na aba principal do PJe
        trocar_aba(navegador, self.aba_pje)

        abas_antes = set(navegador.window_handles)

        # Abre uma nova aba vazia
        navegador.execute_script(
            "window.open('about:blank', '_blank');"
        )

        # Aguarda a nova aba ser criada
        WebDriverWait(
            navegador,
            15,
        ).until(
            lambda driver: len(
                set(driver.window_handles) - abas_antes
            ) == 1
        )

        # Salva o identificador da aba do DJE
        self.aba_dje = (
            set(navegador.window_handles) - abas_antes
        ).pop()

        # Abre o DJE na aba nova
        trocar_aba(navegador, self.aba_dje)
        navegador.get(URL_DJE)

        # Aguarda a página carregar.
        # Use um elemento que realmente exista no novo site.
        WebDriverWait(
            navegador,
            30,
        ).until(
            lambda driver: (
                driver.execute_script(
                    "return document.readyState"
                ) == "complete"
            )
        )

        # Tenta fechar o banner de cookies
        aceitar_cookies(
            navegador,
            tempo=3,
        )

        # Entra no iframe do novo DJE
        trocar_para_iframe(
            navegador,
            wait,
            By.CSS_SELECTOR,
            'iframe[src*="/dje-consulta"]',
        )

        campo = WebDriverWait(
            navegador,
            20,
        ).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/app-root/div/app-calendario/div/div[2]/app-pesquisa/app-pesquisa-form/div/div[5]/button[2]/span")
            )
        )

        navegador.execute_script(
            """
            arguments[0].scrollIntoView({
                block: 'center',
                inline: 'nearest'
            });
            """,
            campo,
        )

        time.sleep(0.5)

        print("DJE aberto em uma aba separada.")

        # Volta obrigatoriamente para a aba do PJe
        trocar_aba(navegador, self.aba_pje)

        # Volta ao conteúdo principal antes de entrar no ngFrame
        navegador.switch_to.default_content()

        trocar_para_iframe(
            navegador,
            wait,
            By.ID,
            "ngFrame",
        )

        print("Retornou à tarefa no PJe.")

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
        trocar_aba(navegador, self.aba_pje)
        trocar_para_iframe(
            navegador,
            wait,
            By.ID,
            "ngFrame",
        )

        xpath_processo = self.xpath_processo(indice_lista)

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

        clicar_js(navegador, elemento_processo)
        print(f"Número do processo: {numero_processo}")

        data_expediente = self.obter_data_expediente(
            wait,
            navegador,
        )

        data_publicacao = self.pesquisar_no_dje(
            wait,
            navegador,
            numero_processo,
        )

        trocar_aba(navegador, self.aba_pje)

        deve_finalizar = self.compara_data(
            data_expediente,
            data_publicacao,
        )

        if deve_finalizar:
            self.finalizar_processo(wait, navegador)

            data_atual = datetime.now().strftime("%d-%m-%Y")
            self.log_processos(
                numero_processo,
                data_atual,
            )

            time.sleep(10)
            return indice_lista

        print(
            f"Processo {numero_processo} ainda não foi publicado."
        )
        return indice_lista + 1

    def obter_data_expediente(self, wait, navegador):
        trocar_aba(navegador, self.aba_pje)
        trocar_para_iframe(
            navegador,
            wait,
            By.ID,
            "ngFrame",
        )

        xpath_abrir_autos = (
            "/html/body/app-root/selector/div/div/div[2]/"
            "right-panel/div/processos-tarefa/div[2]/"
            "conteudo-tarefa/div[1]/div/div/div[2]/button[3]/i"
        )

        abas_antes = set(navegador.window_handles)

        botao_autos = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, xpath_abrir_autos)
            )
        )
        clicar_js(navegador, botao_autos)

        WebDriverWait(navegador, 20).until(
            lambda driver: len(
                set(driver.window_handles) - abas_antes
            ) == 1
        )

        aba_autos = (
            set(navegador.window_handles) - abas_antes
        ).pop()

        try:
            navegador.switch_to.window(aba_autos)

            botao_expedientes = WebDriverWait(
                navegador,
                30,
            ).until(
                EC.element_to_be_clickable(
                    (By.ID, "navbar:linkAbaExpedientes1")
                )
            )
            clicar_js(navegador, botao_expedientes)

            data_expediente = (
                self.procurar_data_diario_eletronico(navegador)
            )

            if not data_expediente:
                raise RuntimeError(
                    "Data do expediente no Diário Eletrônico "
                    "não encontrada."
                )

            print(
                "Data do expediente: "
                f"{data_expediente.strftime('%d/%m/%Y')}"
            )

            return data_expediente

        finally:
            if aba_autos in navegador.window_handles:
                navegador.switch_to.window(aba_autos)
                navegador.close()

            trocar_aba(navegador, self.aba_pje)

    @staticmethod
    def procurar_data_diario_eletronico(navegador):
        indice = 1

        while True:
            xpath_data = (
                "/html/body/div[1]/div[2]/div[2]/table/tbody/"
                "tr[2]/td/table/tbody/tr/td/div/div/div/div/"
                "div/div[2]/span/div/table/tbody/"
                f"tr[{indice}]/td[1]/span/div/span/div[2]"
            )

            try:
                elemento = WebDriverWait(
                    navegador,
                    5,
                ).until(
                    EC.presence_of_element_located(
                        (By.XPATH, xpath_data)
                    )
                )
            except TimeoutException:
                return None

            if "Diário Eletrônico" in elemento.text:
                return extrair_data(elemento.text)

            indice += 1

    def pesquisar_no_dje(
        self,
        wait,
        navegador,
        numero_processo: str,
    ):
        trocar_aba(
            navegador,
            self.aba_dje,
        )

        navegador.switch_to.default_content()

        # Entra no iframe do novo DJE
        trocar_para_iframe(
            navegador,
            wait,
            By.CSS_SELECTOR,
            'iframe[src*="/dje-consulta"]',
        )

        print("Entrou no iframe do DJE.")

        data_default = datetime(2001, 5, 17)

        xpath_select_tribunal = (
            '//*[@id="mat-select-1"]/div/div[1]'
        )
        xpath_tre_pb = (
            '//*[@id="mat-option-49"]/span'
        )
        xpath_pesquisar = (
            "//button[.//span[contains("
            "translate(normalize-space(.), "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀÂÃÉÊÍÓÔÕÚÇ', "
            "'abcdefghijklmnopqrstuvwxyzáàâãéêíóôõúç'), "
            "'pesquisar'"
            ")]]"
        )
        xpath_resultado_data = (
            '//*[@id="mat-tab-content-0-0"]/div/div/div[2]/app-card-diario-binario[1]/button/span/div[1]/span[2]/b'
        )

        try:
            WebDriverWait(navegador, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, xpath_select_tribunal)
                )
            ).click()

            WebDriverWait(navegador, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, xpath_tre_pb)
                )
            ).click()
        except TimeoutException:
            pass

        campo = WebDriverWait(
            navegador,
            20,
        ).until(
            EC.presence_of_element_located(
                (By.ID, "mat-input-0")
            )
        )

        campo.clear()
        pyperclip.copy(numero_processo)
        campo.send_keys(Keys.CONTROL, "v")

        campo = WebDriverWait(
            navegador,
            20,
        ).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/app-root/div/app-calendario/div/div[2]/app-pesquisa/app-pesquisa-form/div/div[5]/button[2]/span")
            )
        )

        navegador.execute_script(
            """
            arguments[0].scrollIntoView({
                block: 'center',
                inline: 'nearest'
            });
            """,
            campo,
        )

        time.sleep(0.5)

        WebDriverWait(navegador, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH, xpath_pesquisar)
            )
        ).click()

        time.sleep(8)

        try:
            elemento_data = WebDriverWait(
                navegador,
                10,
            ).until(
                EC.presence_of_element_located(
                    (By.XPATH, xpath_resultado_data)
                )
            )
            data_publicacao = extrair_data(
                elemento_data.text
            )
        except TimeoutException:
            data_publicacao = None

        if data_publicacao:
            print(
                "Data da publicação no DJE: "
                f"{data_publicacao.strftime('%d/%m/%Y')}"
            )
            return data_publicacao

        print("Data da publicação não encontrada no DJE.")
        return data_default

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
    def compara_data(data_processo, data_publicacao) -> bool:
        return data_processo <= data_publicacao

    @staticmethod
    def log_processos(numero_processo: str, data_atual: str) -> None:
        nome_arquivo = f"processos_manipulados_{data_atual}.txt"
        caminho = caminho_arquivo(nome_arquivo)

        with caminho.open("a", encoding="utf-8") as arquivo:
            arquivo.write(f"{numero_processo}\n")

        print(
            f"Processo {numero_processo} salvo em {nome_arquivo}."
        )