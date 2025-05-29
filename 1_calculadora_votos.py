class CalculadoraVotos:
    def __init__(self, total_eleitores, votos_validos, votos_brancos, votos_nulos):
        self.total_eleitores = total_eleitores
        self.votos_validos = votos_validos
        self.votos_brancos = votos_brancos
        self.votos_nulos = votos_nulos

    def percentual_validos(self):
        return (self.votos_validos / self.total_eleitores) * 100

    def percentual_brancos(self):
        return (self.votos_brancos / self.total_eleitores) * 100

    def percentual_nulos(self):
        return (self.votos_nulos / self.total_eleitores) * 100

# Exemplo de uso com os dados fornecidos:
total_eleitores = 1000
votos_validos = 800
votos_brancos = 150
votos_nulos = 50

calculadora = CalculadoraVotos(total_eleitores, votos_validos, votos_brancos, votos_nulos)

print(f"Percentual de votos válidos: {calculadora.percentual_validos():.2f}%")
print(f"Percentual de votos brancos: {calculadora.percentual_brancos():.2f}%")
print(f"Percentual de votos nulos: {calculadora.percentual_nulos():.2f}%")
