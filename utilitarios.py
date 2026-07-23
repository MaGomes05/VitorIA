import os
import re
import sys
import time
import unicodedata

from datetime import datetime
from pathlib import Path

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By

from config import (
    TEMPO_CLICK,
    TEMPO_ESPERA_PADRAO,
    TEMPO_TROCA_ABA,
    TEMPO_TROCA_IFRAME,
    PADRAO_NUMERO_PROCESSO,
)

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def caminho_base() -> Path:
    """
    Retorna a pasta do programa.

    Funciona tanto durante a execução pelo Python quanto em um
    executável criado pelo PyInstaller.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


def caminho_arquivo(nome: str) -> Path:
    """Monta o caminho absoluto de um arquivo do projeto."""
    return caminho_base() / nome


def criar_wait(navegador, tempo=TEMPO_ESPERA_PADRAO) -> WebDriverWait:
    """Cria uma espera explícita para o navegador informado."""
    return WebDriverWait(navegador, tempo)


def clicar_js(
        navegador,
        elemento,
        pausa=TEMPO_CLICK,
        rolar=False
    ):
        """
        Clica em um elemento com uma pequena pausa.

        O scroll só acontece quando rolar=True.
        """
        if rolar:
            navegador.execute_script(
                """
                arguments[0].scrollIntoView({
                    block: 'center',
                    inline: 'center'
                });
                """,
                elemento
            )
            time.sleep(pausa)

        navegador.execute_script(
            "arguments[0].click();",
            elemento
        )

        time.sleep(pausa)

def normalizar_texto(texto: str) -> str:
    """
    Converte o texto para minúsculas e remove os acentos.

    Exemplo:
    'ACÓRDÃO' -> 'acordao'
    """
    texto = texto.lower().strip()

    return "".join(
        caractere
        for caractere in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caractere) != "Mn"
    )

def trocar_aba(navegador, aba):
    navegador.switch_to.window(aba)
    time.sleep(TEMPO_TROCA_ABA)

def extrair_data(texto: str):
    """Extrai uma data no formato DD/MM/AAAA e retorna datetime."""
    correspondencia = re.search(r"\d{2}/\d{2}/\d{4}", texto)

    if not correspondencia:
        return None

    return datetime.strptime(correspondencia.group(), "%d/%m/%Y")


def extrair_numero_processo(texto: str):
    """Extrai o número CNJ de um processo."""
    correspondencia = re.search(PADRAO_NUMERO_PROCESSO, texto)
    return correspondencia.group() if correspondencia else None


def trocar_para_iframe(
    navegador,
    wait,
    by,
    valor,
):
    """
    Troca para um iframe usando qualquer estratégia
    (ID, XPATH, CSS_SELECTOR, NAME...).
    """

    navegador.switch_to.default_content()

    wait.until(
        EC.frame_to_be_available_and_switch_to_it(
            (by, valor)
        )
    )

    time.sleep(TEMPO_TROCA_IFRAME)

def aceitar_cookies(navegador, tempo=5) -> bool:
    """
    Tenta aceitar o banner de cookies.

    Retorna True quando encontrou e clicou.
    Retorna False quando o banner não apareceu.
    """
    xpaths_possiveis = [
        "//button[contains(translate(normalize-space(.), "
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀÂÃÉÊÍÓÔÕÚÇ', "
        "'abcdefghijklmnopqrstuvwxyzáàâãéêíóôõúç'), "
        "'aceitar todos')]",

        "//button[contains(translate(normalize-space(.), "
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀÂÃÉÊÍÓÔÕÚÇ', "
        "'abcdefghijklmnopqrstuvwxyzáàâãéêíóôõúç'), "
        "'aceitar cookies')]",

        "//button[contains(translate(normalize-space(.), "
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀÂÃÉÊÍÓÔÕÚÇ', "
        "'abcdefghijklmnopqrstuvwxyzáàâãéêíóôõúç'), "
        "'aceitar')]",

        "//a[contains(translate(normalize-space(.), "
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÀÂÃÉÊÍÓÔÕÚÇ', "
        "'abcdefghijklmnopqrstuvwxyzáàâãéêíóôõúç'), "
        "'aceitar')]",
    ]

    navegador.switch_to.default_content()

    for xpath in xpaths_possiveis:
        try:
            botao = WebDriverWait(
                navegador,
                tempo,
            ).until(
                EC.element_to_be_clickable(
                    (By.XPATH, xpath)
                )
            )

            print(
                f"Botão de cookies encontrado: "
                f"{botao.text.strip()}"
            )

            clicar_js(
                navegador,
                botao,
            )

            print("Cookies aceitos.")
            return True

        except TimeoutException:
            continue
        except StaleElementReferenceException:
            continue

    print("Banner de cookies não apareceu.")
    return False