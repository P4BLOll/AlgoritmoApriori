# Importa Enum para criar estados fixos
from enum import Enum

# Facilita a criação de classes que armazenam dados
from dataclasses import dataclass

# Algoritmo Apriori para mineração de regras de associação
from apyori import apriori

# Parâmetros mínimos para geração das regras
MIN_SUPPORT = 0.2       # Regra deve aparecer em pelo menos 20% das transações
MIN_CONFIDENCE = 0.5    # Confiança mínima de 50%
MIN_LIFT = 1.0          # Relação mínima entre os itens

# Limites utilizados para classificar a compra
LIMITE_SUSPEITA = 60
LIMITE_BLOQUEIO = 120

# Estados possíveis de uma compra
class StatusCompra(Enum):
    NORMAL = "NORMAL"
    SUSPEITA = "SUSPEITA"
    BLOQUEADA = "BLOQUEADA"
    INVALIDA = "INVALIDA"

# Classe que representa uma compra
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

    # Converte os dados da compra em uma lista de características
    # para que o algoritmo Apriori possa analisar
    def gerar_transacao(self):
        transacao = []

        # Considera muitos ingressos quando a quantidade é >= 6
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

# Histórico de compras utilizado para gerar as regras de associação
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

# Executa o algoritmo Apriori para descobrir padrões frequentes
def gerar_regras():
    regras = apriori(
        historico_compras,
        min_support=MIN_SUPPORT,
        min_confidence=MIN_CONFIDENCE,
        min_lift=MIN_LIFT
    )

    return list(regras)

# Exibe as regras encontradas pelo Apriori
def exibir_regras(regras):
    print(" REGRAS DE ASSOCIAÇÃO ENCONTRADAS ")

    for regra in regras:
        suporte = regra.support

        for estatistica in regra.ordered_statistics:
            antecedente = list(estatistica.items_base)
            consequente = list(estatistica.items_add)

            confianca = estatistica.confidence
            lift = estatistica.lift

            # Mostra apenas regras completas
            if antecedente and consequente:

                print(f"REGRA: {antecedente} => {consequente}")
                print(f"SUPORTE: {suporte:.2f}")
                print(f"CONFIANÇA: {confianca:.2f}")
                print(f"LIFT: {lift:.2f}")

                print("-" * 40)

# Classe responsável pela análise antifraude
class FraudDetector:

    # Ao criar o detector, as regras são carregadas
    def __init__(self):
        self.regras = gerar_regras()

    # Calcula uma pontuação de risco para a compra
    def calcular_score(self, compra):
        score = 0

        # Transação da compra atual
        transacao_atual = compra.gerar_transacao()

        # Percorre todas as regras encontradas
        for regra in self.regras:

            itens_regra = set(regra.items)

            # Verifica quantos itens da regra aparecem na compra
            intersecao = itens_regra.intersection(transacao_atual)

            # Quanto mais coincidências, maior o score
            if len(intersecao) >= 2:

                # Peso baseado no suporte da regra
                score += regra.support * 100

                for estatistica in regra.ordered_statistics:

                    # Peso baseado na confiança
                    score += estatistica.confidence * 50

                    # Peso baseado no lift
                    score += estatistica.lift * 10

        return round(score, 2)

    # Classifica a compra de acordo com o score
    def classificar(self, compra):

        # Validação básica
        if compra.quantidade <= 0:
            return StatusCompra.INVALIDA, 0

        score = self.calcular_score(compra)

        # Compra bloqueada
        if score >= LIMITE_BLOQUEIO:
            return StatusCompra.BLOQUEADA, score

        # Compra suspeita
        if score >= LIMITE_SUSPEITA:
            return StatusCompra.SUSPEITA, score

        # Compra normal
        return StatusCompra.NORMAL, score

# Lê uma resposta s/n e converte para True ou False
def ler_booleano(texto):
    resposta = input(texto).strip().lower()
    return resposta == "s"

# Coleta os dados da compra digitados pelo usuário
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

    # Retorna um objeto Compra preenchido
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

# Exibe o resultado final da análise
def mostrar_resultado(compra, status, score):

    print(" RESULTADO DA ANÁLISE ")

    print(f"Cliente: {compra.nome}")
    print(f"CPF: {compra.cpf}")

    # Mostra as características detectadas
    print(f"Features detectadas: {compra.gerar_transacao()}")

    print(f"Score de fraude: {score}")
    print(f"Status: {status.value}")

    print()

    # Mensagem específica para cada classificação
    match status:

        case StatusCompra.NORMAL:
            print("Compra aprovada.")

        case StatusCompra.SUSPEITA:
            print("Compra enviada para análise manual.")

        case StatusCompra.BLOQUEADA:
            print("Possível cambismo/fraude detectado.")

        case StatusCompra.INVALIDA:
            print("Compra inválida.")

# Exibe o cabeçalho do sistema
def mostrar_menu():
    print(" SISTEMA ANTIFRAUDE - CORINTHIANS ")

# Função principal
def main():

    # Mostra o menu inicial
    mostrar_menu()

    # Cria o detector e gera as regras
    detector = FraudDetector()

    # Exibe as regras descobertas
    exibir_regras(detector.regras)

    # Recebe uma nova compra
    compra = criar_compra()

    # Analisa a compra
    status, score = detector.classificar(compra)

    # Mostra o resultado da análise
    mostrar_resultado(compra, status, score)

# Ponto de entrada do programa
if __name__ == "__main__":
    main()