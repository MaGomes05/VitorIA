import time

import pandas as pd
import pyperclip

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)

from utilitarios import (
    caminho_arquivo,
    clicar_js,
    criar_wait,
    trocar_aba,
    trocar_para_iframe,
)

from config import PERFIS_GABINETES

# ============================================================
# TAREFA: ETIQUETA META 02 - 70%
# ============================================================

class Etiqueta_meta2_70:
    """Aplica a etiqueta 'META 02 - 70%' nos processos informados."""

    XPATH_MENU_PERFIL = "/html/body/nav/div/div[2]/ul/li/a"
    XPATH_CAMPO_PERFIL = (
        "/html/body/nav/div/div[2]/ul/li/div/form/div/"
        "div/table[1]/tbody/tr/td/input"
    )
    XPATH_RESULTADO_PERFIL = (
        "/html/body/nav/div/div[2]/ul/li/div/form/div/"
        "div/table[2]/tbody/tr/td[2]/a"
    )

    def executa(self, navegador):
        wait = criar_wait(navegador)

        for gabinete in range(1, 7):
            processos = self.manipula_planilha(gabinete)
            self.seleciona_gabinete(
                wait,
                navegador,
                gabinete
            )

            primeira_pesquisa = True

            for numero in processos:
                print(f"Pesquisando processo {numero}")

                primeira_pesquisa = self.pesquisa_processo(
                    wait,
                    navegador,
                    str(numero),
                    primeira_pesquisa,
                )

        return "Tarefa 'Etiqueta META 02 - 70%' concluída."

    def seleciona_gabinete(
        self,
        wait,
        navegador,
        gabinete: int,
    ) -> None:
        nome_perfil = PERFIS_GABINETES.get(gabinete)

        if not nome_perfil:
            raise ValueError(f"Gabinete inválido: {gabinete}")

        navegador.switch_to.default_content()

        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, self.XPATH_MENU_PERFIL)
            )
        ).click()

        campo = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, self.XPATH_CAMPO_PERFIL)
            )
        )

        campo.clear()
        campo.send_keys(nome_perfil)

        perfil = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, self.XPATH_RESULTADO_PERFIL)
            )
        )

        if "Assessor Chefe" not in perfil.text:
            raise RuntimeError(
                f"Perfil do gabinete {gabinete} não encontrado."
            )

        perfil.click()
        print(f"Perfil do gabinete {gabinete} selecionado.")
        time.sleep(5)

    def pesquisa_processo(
        self,
        wait,
        navegador,
        numero: str,
        primeira_pesquisa: bool,
    ) -> bool:
        if primeira_pesquisa:
            trocar_para_iframe(
                navegador,
                wait,
                By.ID,
                "ngFrame",
            )

            xpath_filtro = (
                "/html/body/app-root/selector/div/div/div[2]/"
                "right-panel/div/div/div[3]/tarefas/div/div[1]/div"
            )

            wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, xpath_filtro)
                )
            ).click()

        xpath_campo = (
            "/html/body/app-root/selector/div/div/div[2]/"
            "right-panel/div/div/div[3]/tarefas/div/div[2]/"
            "filtro-tarefas-pendentes/div/form/fieldset/"
            "div[1]/input"
        )
        xpath_botao_pesquisar = (
            "/html/body/app-root/selector/div/div/div[2]/"
            "right-panel/div/div/div[3]/tarefas/div/div[2]/"
            "filtro-tarefas-pendentes/div/form/fieldset/"
            "div[4]/button[1]"
        )

        campo = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, xpath_campo)
            )
        )

        campo.clear()
        campo.send_keys(numero)

        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, xpath_botao_pesquisar)
            )
        ).click()

        time.sleep(2)

        if self._abrir_resultado_pesquisa(navegador):
            self.etiqueta(wait, navegador)
            return True

        print(f"Processo {numero} não encontrado no gabinete.")
        return False

    @staticmethod
    def _abrir_resultado_pesquisa(navegador) -> bool:
        xpaths = [
            (
                "/html/body/app-root/selector/div/div/div[2]/"
                "right-panel/div/div/div[3]/tarefas/div/div[3]/"
                "div[1]/div/a/div/span[1]"
            ),
            (
                "/html/body/app-root/selector/div/div/div[2]/"
                "right-panel/div/div/div[3]/tarefas/div/div[3]/"
                "div/div/a/div/span[1]"
            ),
        ]

        for xpath in xpaths:
            try:
                navegador.find_element(By.XPATH, xpath).click()
                return True
            except NoSuchElementException:
                continue

        return False

    @staticmethod
    def etiqueta(wait, navegador) -> None:
        xpaths = {
            "selecionar_processo": (
                "/html/body/app-root/selector/div/div/div[2]/"
                "right-panel/div/processos-tarefa/div[1]/div[2]/"
                "div/div[1]/p-datalist/div/div/ul/li[1]/"
                "processo-datalist-card/div/div[2]/button/i"
            ),
            "abrir_etiquetas": (
                "/html/body/app-root/selector/div/div/div[2]/"
                "right-panel/div/processos-tarefa/div[1]/div[2]/"
                "div/div[1]/div[1]/acoes-processos-tarefa/"
                "div/div/div/button[2]/i"
            ),
            "adicionar_etiqueta": (
                "/html/body/app-root/selector/div/div/div[2]/"
                "right-panel/div/processos-tarefa/div[3]/"
                "etiquetar-lote/div/div/div/div[2]/div/"
                "pje-selecionar-etiquetas/div/div/table/"
                "tbody/tr/td[1]/button/i"
            ),
            "confirmar": (
                "/html/body/app-root/selector/div/div/div[2]/"
                "right-panel/div/processos-tarefa/div[3]/"
                "etiquetar-lote/div/div/div/div[3]/div/"
                "button[1]/span"
            ),
            "fechar": (
                "/html/body/app-root/selector/div/div/div[2]/"
                "right-panel/div/processos-tarefa/div[3]/"
                "etiquetar-lote/div/div/div/div[1]/button/span"
            ),
            "voltar": (
                "/html/body/app-root/selector/div/div/div[1]/"
                "side-bar/nav/ul/li[1]/a/i"
            ),
        }

        for chave in ("selecionar_processo", "abrir_etiquetas"):
            wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, xpaths[chave])
                )
            ).click()

        campo_etiqueta = wait.until(
            EC.presence_of_element_located(
                (By.ID, "itPesquisarEtiquetas")
            )
        )
        campo_etiqueta.clear()
        campo_etiqueta.send_keys("META 02 - 70%")

        for chave in (
            "adicionar_etiqueta",
            "confirmar",
            "fechar",
            "voltar",
        ):
            wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, xpaths[chave])
                )
            ).click()

            if chave == "confirmar":
                time.sleep(5)
            else:
                time.sleep(1)

    @staticmethod
    def manipula_planilha(gabinete: int):
        nome_planilha = f"Metas 2024_GABJ_0{gabinete}_Out.xlsx"
        caminho = caminho_arquivo(nome_planilha)

        if not caminho.exists():
            raise FileNotFoundError(
                f"Planilha não encontrada: {caminho}"
            )

        df = pd.read_excel(
            caminho,
            sheet_name="Meta 02 - 70%"
        )

        if "numero" not in df.columns:
            raise KeyError(
                f"A coluna 'numero' não existe em {nome_planilha}."
            )

        return df["numero"].dropna().astype(str)