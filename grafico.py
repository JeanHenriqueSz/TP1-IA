import matplotlib.pyplot as plt


melhor_com_elitismo = [1144.3582887700536, 1137.01, 1137.01, 1137.01, 1137.01, 1137.01, 1217.4866310160428, 1137.01, 1137.01, 1137.01, 1137.01, 1137.01, 1137.01, 1137.01, 1137.01, 1137.01, 1137.01, 1137.01, 1137.01, 1137.01]
melhor_sem_elitismo = [1139.3582887700536, 707.01, 769.3582887700535, 469.68983957219257, 250.79144385026757, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

plt.figure(figsize=(10,5))
plt.plot(melhor_com_elitismo, label="Com Elitismo", linewidth=2)
plt.plot(melhor_sem_elitismo, label="Sem Elitismo", linewidth=2)

plt.title("Evolução da Melhor Aptidão por Geração")
plt.xlabel("Geração")
plt.ylabel("Fitness (Valor Total)")
plt.legend()
plt.grid(True)
plt.show()
