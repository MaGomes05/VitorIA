# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================

URL_PJE = "https://pje.tre-pb.jus.br/pje/login.seam"
URL_DJE = "https://www.tse.jus.br/servicos-judiciais/publicacoes-oficiais/diario-da-justica-eletronico"

TEMPO_ESPERA_PADRAO= 10
TEMPO_ESPERA_LOGIN = 20
TEMPO_CLICK = 0.7
TEMPO_TROCA_ABA = 0.7
TEMPO_TROCA_IFRAME = 0.5

DOCUMENTO_PROCURADO = "certidao de julgamento"

PADRAO_NUMERO_PROCESSO = (
    r"\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}"
)

PERFIS_GABINETES = {
    1: "GABJ01 - Gabinete Jurista 1 / Assessoria / Assessor Chefe",
    2: "GABJ02 - Gabinete Juiz de Direito 1 / Assessoria / Assessor Chefe",
    3: "GABJ03 - Gabinete Jurista 2 / Assessoria / Assessor Chefe",
    4: "GABJ04 - Gabinete Juiz de Direito 2 / Assessoria / Assessor Chefe",
    5: "GABJ05 - Gabinete Vice Presidência / Assessoria / Assessor Chefe",
    6: "GABJ06 - Gabinete Juiz Federal / Assessoria / Assessor Chefe",
}