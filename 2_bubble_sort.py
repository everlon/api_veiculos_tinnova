def bubble_sort(vetor):
    n = len(vetor)
    for i in range(n):
        for j in range(0, n - 1 - i):
            if vetor[j] > vetor[j + 1]:
                vetor[j], vetor[j + 1] = vetor[j + 1], vetor[j]
        print(f"Iteração {i + 1}: {vetor}")

    return vetor


vetor = [5, 3, 2, 4, 7, 1, 0, 6]
print("Vetor original:", vetor)

vetor_ordenado = bubble_sort(vetor)
print("Vetor ordenado:", vetor_ordenado)
