from enum import Enum
from dataclasses import dataclass
from apyori import apriori

MIN_SUPPORT = 0.2
MIN_CONFIDENCE = 0.5
MIN_LIFT = 1.0

LIMITE_SUSPEITA = 60
LIMITE_BLOQUEIO = 120

class StatusCompra(Enum):
    NORMAL = "NORMAL"
    SUSPEITA = "SUSPEITA"
    BLOQUEADA = "BLOQUEADA"
    INVALIDA = "INVALIDA"

@dataclass
class Compra:
    nome: str
    cpf: str
    quantidade: int
    pagamento_pix: bool
    compra_madrugada: bool
    jogo_final: bool
    cpf_recente: bool
    cartao_virtual: bool
    muitas_tentativas: bool

    def gerar_transacao(self):
        transacao = []

        if self.quantidade >= 6:
            transacao.append("muitos_ingressos")

        if self.pagamento_pix:
            transacao.append("pagamento_pix")

        if self.compra_madrugada:
            transacao.append("compra_madrugada")

        if self.jogo_final:
            transacao.append("jogo_final")

        if self.cpf_recente:
            transacao.append("cpf_recente")

        if self.cartao_virtual:
            transacao.append("cartao_virtual")

        if self.muitas_tentativas:
            transacao.append("muitas_tentativas")

        return transacao

historico_compras = [
    ["muitos_ingressos", "pagamento_pix", "jogo_final"],

    ["muitos_ingressos", "compra_madrugada"],

    ["cpf_recente", "muitos_ingressos"],

    ["pagamento_pix", "compra_madrugada"],

    ["muitos_ingressos", "cpf_recente", "pagamento_pix"],

    ["jogo_final", "pagamento_pix"],

    ["muitos_ingressos", "compra_madrugada", "pagamento_pix"],

    ["cpf_recente", "pagamento_pix"],

    ["muitos_ingressos", "jogo_final"],

    ["muitas_tentativas", "pagamento_pix"],

    ["cartao_virtual", "muitos_ingressos"],

    ["compra_madrugada", "cpf_recente"],

    ["cartao_virtual", "pagamento_pix"],

    ["muitas_tentativas", "compra_madrugada"],

    ["cartao_virtual", "cpf_recente"]
]

def gerar_regras():
    regras = apriori(
        historico_compras,
        min_support=MIN_SUPPORT,
        min_confidence=MIN_CONFIDENCE,
        min_lift=MIN_LIFT
    )

    return list(regras)

def exibir_regras(regras):
    print(" REGRAS DE ASSOCIAÇÃO ENCONTRADAS ")

    for regra in regras:
        suporte = regra.support

        for estatistica in regra.ordered_statistics:
            antecedente = list(estatistica.items_base)
            consequente = list(estatistica.items_add)

            confianca = estatistica.confidence
            lift = estatistica.lift

            if antecedente and consequente:

                print(f"REGRA: {antecedente} => {consequente}")
                print(f"SUPORTE: {suporte:.2f}")
                print(f"CONFIANÇA: {confianca:.2f}")
                print(f"LIFT: {lift:.2f}")

                print("-" * 40)

class FraudDetector:
    def __init__(self):
        self.regras = gerar_regras()

    def calcular_score(self, compra):
        score = 0

        transacao_atual = compra.gerar_transacao()

        for regra in self.regras:
            itens_regra = set(regra.items)

            intersecao = itens_regra.intersection(transacao_atual)

            if len(intersecao) >= 2:
                score += regra.support * 100

                for estatistica in regra.ordered_statistics:

                    score += estatistica.confidence * 50
                    score += estatistica.lift * 10

        return round(score, 2)

    def classificar(self, compra):
        if compra.quantidade <= 0:
            return StatusCompra.INVALIDA, 0

        score = self.calcular_score(compra)

        if score >= LIMITE_BLOQUEIO:
            return StatusCompra.BLOQUEADA, score

        if score >= LIMITE_SUSPEITA:
            return StatusCompra.SUSPEITA, score

        return StatusCompra.NORMAL, score

def ler_booleano(texto):
    resposta = input(texto).strip().lower()

    return resposta == "s"


def criar_compra():
    print(" NOVA COMPRA ")

    nome = input("Nome do cliente: ")

    cpf = input("CPF: ")

    quantidade = int(
        input("Quantidade de ingressos: ")
    )

    pagamento_pix = ler_booleano(
        "Pagamento via PIX? (s/n): "
    )

    compra_madrugada = ler_booleano(
        "Compra realizada de madrugada? (s/n): "
    )

    jogo_final = ler_booleano(
        "Partida importante/final? (s/n): "
    )

    cpf_recente = ler_booleano(
        "CPF criado recentemente? (s/n): "
    )

    cartao_virtual = ler_booleano(
        "Utilizou cartão virtual? (s/n): "
    )

    muitas_tentativas = ler_booleano(
        "Muitas tentativas anteriores? (s/n): "
    )

    return Compra(
        nome=nome,
        cpf=cpf,
        quantidade=quantidade,
        pagamento_pix=pagamento_pix,
        compra_madrugada=compra_madrugada,
        jogo_final=jogo_final,
        cpf_recente=cpf_recente,
        cartao_virtual=cartao_virtual,
        muitas_tentativas=muitas_tentativas
    )

def mostrar_resultado(compra, status, score):
    print(" RESULTADO DA ANÁLISE ")

    print(f"Cliente: {compra.nome}")

    print(f"CPF: {compra.cpf}")

    print(f"Features detectadas: {compra.gerar_transacao()}")

    print(f"Score de fraude: {score}")

    print(f"Status: {status.value}")

    print()

    match status:
        case StatusCompra.NORMAL:
            print("Compra aprovada.")

        case StatusCompra.SUSPEITA:
            print("Compra enviada para análise manual.")

        case StatusCompra.BLOQUEADA:
            print("Possível cambismo/fraude detectado.")

        case StatusCompra.INVALIDA:
            print("Compra inválida.")

def mostrar_menu():
    print(" SISTEMA ANTIFRAUDE - CORINTHIANS ")

def main():
    mostrar_menu()

    detector = FraudDetector()

    exibir_regras(detector.regras)

    compra = criar_compra()

    status, score = detector.classificar(compra)

    mostrar_resultado(compra, status, score)

if __name__ == "__main__":

    main()