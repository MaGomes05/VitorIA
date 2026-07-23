import time

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import URL_PJE, TEMPO_ESPERA_LOGIN
from utilitarios import caminho_arquivo, criar_wait

# ============================================================
# LOGIN
# ============================================================

class Inicial:
    """Responsável por iniciar o Firefox e efetuar o login no PJe."""

    def login(self, usuario: str, senha: str):
        servico = Service(
            executable_path=str(caminho_arquivo("drivers/geckodriver.exe"))
        )

        navegador = webdriver.Firefox(service=servico)
        wait = criar_wait(navegador, TEMPO_ESPERA_LOGIN)

        try:
            navegador.get(URL_PJE)

            navegador.switch_to.default_content()

            # Primeiro tenta localizar os campos diretamente na página principal.
            try:
                campo_usuario = WebDriverWait(
                    navegador,
                    3,
                ).until(
                    EC.presence_of_element_located(
                        (By.ID, "username")
                    )
                )

                campo_senha = navegador.find_element(
                    By.ID,
                    "password"
                )

                print("Campos de login encontrados no conteúdo principal.")

            except TimeoutException:
                print(
                    "Campos não encontrados no conteúdo principal. "
                    "Procurando dentro do ssoFrame..."
                )

                navegador.switch_to.default_content()

                try:
                    WebDriverWait(
                        navegador,
                        5,
                    ).until(
                        EC.frame_to_be_available_and_switch_to_it(
                            (By.ID, "ssoFrame")
                        )
                    )

                    campo_usuario = WebDriverWait(
                        navegador,
                        5,
                    ).until(
                        EC.presence_of_element_located(
                            (By.ID, "username")
                        )
                    )

                    campo_senha = navegador.find_element(
                        By.ID,
                        "password"
                    )

                    print("Campos de login encontrados dentro do ssoFrame.")

                except TimeoutException as erro:
                    raise RuntimeError(
                        "Não foi possível localizar os campos de login "
                        "nem no conteúdo principal nem no ssoFrame."
                    ) from erro

            campo_usuario.clear()
            campo_usuario.send_keys(usuario)

            campo_senha.clear()
            campo_senha.send_keys(senha)

            navegador.find_element(
                By.XPATH,
                '//input[@value="Entrar"]'
            ).click()

            navegador.switch_to.default_content()

            # Aguarda o usuário preencher o 2FA manualmente.
            self.aguardar_conclusao_login(
                navegador,
                tempo_limite=300,
            )

            return navegador

        except Exception:
            # O navegador é fechado quando o login não pôde ser concluído.
            navegador.quit()
            raise

    def aguardar_conclusao_login(
        self,
        navegador,
        tempo_limite: int = 300,
    ) -> bool:
        print(
            "Aguardando o preenchimento manual e a validação do 2FA..."
        )

        navegador.switch_to.default_content()

        localizador_token = (
            By.XPATH,
            (
                "//a["
                "normalize-space(.)='Prosseguir sem o Token'"
                " or contains(@onclick, 'tokenAcessoForm')"
                "]"
            ),
        )

        localizador_menu_perfil = (
            By.XPATH,
            "/html/body/nav/div/div[2]/ul/li/a",
        )

        # -------------------------------------------------
        # 1. Aguarda o 2FA realmente terminar
        # -------------------------------------------------

        url_antes_2fa = navegador.current_url

        def saiu_da_etapa_2fa(driver):
            try:
                driver.switch_to.default_content()

                if driver.find_elements(*localizador_token):
                    return True

                if driver.current_url != url_antes_2fa:
                    return True

                return False

            except Exception:
                return False

        try:
            WebDriverWait(
                navegador,
                tempo_limite,
                poll_frequency=1,
            ).until(saiu_da_etapa_2fa)

        except TimeoutException as erro:
            raise TimeoutException(
                "O tempo para preencher e validar o código 2FA expirou."
            ) from erro

        print("O 2FA foi validado. Verificando a próxima etapa...")

        # Dá alguns segundos para a tela intermediária do Token renderizar.
        time.sleep(3)

        # -------------------------------------------------
        # 2. Procura a etapa opcional do Token
        # -------------------------------------------------

        try:
            link_token = WebDriverWait(
                navegador,
                12,
                poll_frequency=0.5,
                ignored_exceptions=(
                    StaleElementReferenceException,
                ),
            ).until(
                EC.element_to_be_clickable(
                    localizador_token
                )
            )

            print(
                "Tela opcional do Token PJe identificada:",
                repr(link_token.text.strip()),
            )

            link_token.click()

            print(
                "Clique em 'Prosseguir sem o Token' realizado."
            )

            time.sleep(2)

        except TimeoutException:
            print(
                "A etapa opcional do Token PJe não foi exibida."
            )

        # -------------------------------------------------
        # 3. Aguarda a tela principal
        # -------------------------------------------------

        def menu_perfil_visivel(driver):
            try:
                driver.switch_to.default_content()

                menus = driver.find_elements(
                    *localizador_menu_perfil
                )

                return any(
                    menu.is_displayed()
                    for menu in menus
                )

            except StaleElementReferenceException:
                return False

        try:
            WebDriverWait(
                navegador,
                60,
                poll_frequency=1,
                ignored_exceptions=(
                    StaleElementReferenceException,
                ),
            ).until(menu_perfil_visivel)

        except TimeoutException as erro:
            raise TimeoutException(
                "A autenticação foi concluída, mas a tela principal "
                "do PJe não foi identificada."
            ) from erro

        navegador.switch_to.default_content()

        print(
            "Login, 2FA e etapa opcional do Token PJe concluídos."
        )

        return True

    @staticmethod
    def _pular_token_pje(navegador) -> bool:
        """
        Clica em “Prosseguir sem o Token” quando a tela opcional
        do Token PJe aparecer.
        """
        navegador.switch_to.default_content()

        localizadores = [
            (
                By.XPATH,
                "//a[normalize-space(.)='Prosseguir sem o Token']",
            ),
            (
                By.XPATH,
                "//a[contains(@onclick, 'tokenAcessoForm')]",
            ),
            (
                By.CSS_SELECTOR,
                "a.btn.btn-default[onclick*='tokenAcessoForm']",
            ),
        ]

        for localizador in localizadores:
            try:
                link = WebDriverWait(
                    navegador,
                    2,
                    ignored_exceptions=(
                        StaleElementReferenceException,
                    ),
                ).until(
                    EC.element_to_be_clickable(localizador)
                )

                print(
                    "Opção encontrada:",
                    repr(link.text.strip()),
                )

                # O onclick executa jsfcljs; o clique comum é preferível
                # ao JavaScript click nesse caso.
                link.click()

                print(
                    "Clique em 'Prosseguir sem o Token' executado."
                )

                time.sleep(2)
                return True

            except TimeoutException:
                continue
            except StaleElementReferenceException:
                continue
            except Exception as erro:
                print(
                    "Falha no clique comum:",
                    repr(erro),
                )

                try:
                    link = navegador.find_element(*localizador)

                    # Dispara MouseEvent real, preservando o onclick.
                    navegador.execute_script(
                        """
                        arguments[0].dispatchEvent(
                            new MouseEvent('click', {
                                bubbles: true,
                                cancelable: true,
                                view: window
                            })
                        );
                        """,
                        link,
                    )

                    print(
                        "Clique alternativo em "
                        "'Prosseguir sem o Token' executado."
                    )

                    time.sleep(2)
                    return True

                except Exception as erro_alternativo:
                    print(
                        "Falha no clique alternativo:",
                        repr(erro_alternativo),
                    )

        return False