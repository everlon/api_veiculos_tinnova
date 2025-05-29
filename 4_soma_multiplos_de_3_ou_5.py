def soma_multiplos_de_3_ou_5(limite: int) -> int:
    if not isinstance(limite, int):
        raise TypeError("O limite deve ser um número inteiro.")
    if limite < 0:
        return 0

    soma = 0
    for i in range(limite):
        if i % 3 == 0 or i % 5 == 0:
            soma += i

    return soma

numero_limite = 10
print(f"A soma dos múltiplos de 3 ou 5 abaixo de {numero_limite} é {soma_multiplos_de_3_ou_5(numero_limite)}")

numero_limite_maior = 1000 # Exemplo comum deste tipo de problema
print(f"A soma dos múltiplos de 3 ou 5 abaixo de {numero_limite_maior} é {soma_multiplos_de_3_ou_5(numero_limite_maior)}")

print(f"A soma dos múltiplos de 3 ou 5 abaixo de 0 é {soma_multiplos_de_3_ou_5(0)}")
print(f"A soma dos múltiplos de 3 ou 5 abaixo de 3 é {soma_multiplos_de_3_ou_5(3)}")
