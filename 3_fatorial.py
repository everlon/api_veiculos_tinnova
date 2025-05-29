# com recursão:
def fatorial(n):
    if n < 0:
        raise ValueError("Fatorial não é definido para números negativos.")
    if n == 0:
        return 1
    return n * fatorial(n - 1)

for i in range(7):
    print(f"{i}! = {fatorial(i)}")


print('===================================')


# com laço, que mais eficiente para valores maiores:
def fatorial(n):
    if n < 0:
        raise ValueError("Fatorial não é definido para números negativos.")
    resultado = 1
    for i in range(2, n + 1):
        resultado *= i
    return resultado

for i in range(7):
    print(f"{i}! = {fatorial(i)}")


'''
Como sei? Assisti este video a poucos dias:
https://www.youtube.com/watch?v=Fwgwk3NBtxU
'''