from enum import Enum
from apyori import apriori

LIMITE_NORMAL = 5
LIMITE_MAXIMO = 10

class StatusCompra(Enum):
    NORMAL = 1
    SUSPEITA = 2
    BLOQUEADA = 3
    INVALIDA = 4

historico_compras = [

    ["muitos_ingressos", "pagamento_pix", "jogo_final"],
    ["muitos_ingressos", "compra_madrugada"],
    ["cpf_recente", "muitos_ingressos"],
    ["pagamento_pix", "compra_madrugada"],
    ["muitos_ingressos", "cpf_recente"],
    ["jogo_final", "pagamento_pix"]
]

def mostrar_menu():

    print("===================================")
    print(" SISTEMA DE VENDA DE INGRESSOS ")
    print("         CORINTHIANS")
    print("===================================\n")

def cadastrar_cliente():

    nome = input("Digite o nome do cliente: ")
    cpf = input("Digite o CPF do cliente: ")

    return nome, cpf

def solicitar_quantidade():

    return int(input("Quantidade de ingressos desejada: "))

def analisar_padroes_apriori():

    regras = apriori(
        historico_compras,
        min_support=0.3,
        min_confidence=0.5,
        min_lift=1
    )

    return list(regras)

def classificar_compra(quantidade):

    if quantidade <= 0:
        return StatusCompra.INVALIDA

    regras = analisar_padroes_apriori()

    atributos_compra = []

    if quantidade > LIMITE_NORMAL:
        atributos_compra.append("muitos_ingressos")

    for regra in regras:

        itens = list(regra.items)

        if "muitos_ingressos" in itens:

            return StatusCompra.SUSPEITA

    if quantidade <= LIMITE_NORMAL:
        return StatusCompra.NORMAL

    if quantidade > LIMITE_MAXIMO:
        return StatusCompra.BLOQUEADA

    return StatusCompra.NORMAL


def gerar_mensagem(status, nome, quantidade):

    match status:

        case StatusCompra.NORMAL:
            return (
                f"Compra aprovada para {nome}.\n"
                f"{quantidade} ingresso(s) liberado(s).\n"
                "Compra considerada NORMAL."
            )

        case StatusCompra.SUSPEITA:
            return (
                f"ATENÇÃO: compra de {quantidade} ingressos.\n"
                "Padrão suspeito identificado pelo algoritmo Apriori.\n"
                "Compra enviada para análise manual."
            )

        case StatusCompra.BLOQUEADA:
            return (
                f"Compra BLOQUEADA para {nome}.\n"
                "Possível tentativa de cambismo."
            )

        case StatusCompra.INVALIDA:
            return "Quantidade inválida."


def main():

    mostrar_menu()

    nome, cpf = cadastrar_cliente()

    quantidade = solicitar_quantidade()

    status = classificar_compra(quantidade)

    mensagem = gerar_mensagem(status, nome, quantidade)

    print("\nRESULTADO DA ANÁLISE")
    print(mensagem)

    print("\nObrigado por utilizar o sistema!")

main()