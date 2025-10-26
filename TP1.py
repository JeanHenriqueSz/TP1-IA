import random

# ============================================================
# PARÂMETROS FIXOS para facilitar os testes
# ============================================================
# [PARÂMETROS FIXOS]
CAMINHO_ARQUIVO = r"D:\UNA\IA-Sexta\TP1-IA\instancias\KNAPDATA40.TXT"
MODO_SELECAO = "torneio"      # opções: "torneio", "roleta", "misto"
MODO_PENALIZACAO = "linear"   # opções: "zero" (zera inviável), "linear" (pune proporcional)
MODO_AVALIACAO = "valor"      # opções: "valor" (benefício total), "razao" (benefício/peso)
ELITISMO = True               # manter melhor indivíduo em cada geração
TAMANHO_ELITE = 1             # quantos elites manter
TAMANHO_POPULACAO = 50
TAXA_CRUZAMENTO = 0.8
TAXA_MUTACAO = 0.1
NUMERO_GERACOES = 500
PROPORCAO_POP_INICIAL_VIAVEL = 0.5  # fração da população inicial tentando ser viável


# A classe Item representa um elemento candidato à mochila, com 'weight' (peso/custo)
# e 'value' (benefício).
class Item:
    def __init__(self, weight, value):
        self.weight = weight
        self.value = value

def main():
    # Exemplo de itens e capacidade da mochila
    # Comentário: estes itens servem como fallback quando o arquivo não for lido.
    items = [
        Item(2, 10),
        Item(3, 7),
        Item(4, 14),
        Item(5, 5),
        Item(6, 3)
    ]
    capacity = 10

    # Parâmetros do algoritmo genético
    population_size = TAMANHO_POPULACAO
    crossover_rate = TAXA_CRUZAMENTO
    mutation_rate = TAXA_MUTACAO
    num_generations = NUMERO_GERACOES

    
    # Lê instância no formato: 1ª linha = capacidade; 2ª = número de itens; demais = "nome,peso,beneficio"
    try:
        items_lidos, capacidade_lida = load_items_from_file(CAMINHO_ARQUIVO)
        if items_lidos and capacidade_lida is not None:
            items = items_lidos
            capacity = capacidade_lida
            print(f"Instância carregada: {len(items)} itens, capacidade={capacity}")
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}. Usando itens de exemplo (código padrão).")
    

    # Chamada para a função que implementa o algoritmo genético
    # Internamente, a função foi estendida (sem mudar assinatura) para:
    # - aplicar elitismo opcional,
    # - registrar evolução por geração,
    # - usar seleção configurável,
    # - penalização e métrica configuráveis.
    solution = genetic_algorithm_knapsack(items, capacity, population_size, crossover_rate, mutation_rate, num_generations)

    # Impressão da solução e de métricas auxiliares
    print("\nItens selecionados:")
    total_weight = 0
    total_value = 0
    for i, item in enumerate(items):
        if solution[i] == 1:
            print(f"Item {i+1}: Peso = {item.weight}, Valor = {item.value}")
            total_weight += item.weight
            total_value += item.value

    print(f"\nPeso total da solução: {total_weight} (capacidade = {capacity})")
    print(f"Valor total da solução: {total_value}")

    # Se disponível, imprime evolução da melhor aptidão por geração
    if hasattr(genetic_algorithm_knapsack, "_evolucao_melhor_por_geracao"):
        serie = genetic_algorithm_knapsack._evolucao_melhor_por_geracao
        print(f"Melhor fitness final: {serie[-1] if serie else 'N/A'}")
        print(f"Evolução (melhor por geração) — primeiros 20: {serie[:20]}")

# Função para implementar o algoritmo genético para o Problema da Mochila 
def genetic_algorithm_knapsack(items, capacity, population_size, crossover_rate, mutation_rate, num_generations):
    population = generate_initial_population(len(items), population_size)

    # [POPULAÇÃO VIÁVEL]
    # Mistura parte da população com indivíduos inicialmente mais propensos a serem viáveis.
    qtd_viaveis = int(population_size * PROPORCAO_POP_INICIAL_VIAVEL)
    if qtd_viaveis > 0:
        viaveis = generate_viable_population(len(items), qtd_viaveis, items, capacity)
        population[:qtd_viaveis] = viaveis
    

    # Registro da melhor aptidão por geração para o relatório
    evolucao_melhor_por_geracao = []

    for gen in range(num_generations):
        next_generation = []

        # ELITISMO AJUSTADO
        # Mantém elites (preferencialmente viáveis). Se não houver viáveis, pega os melhores.
        if ELITISMO:
            elites = sorted(
                population,
                key=lambda x: fitness_function(x, items, capacity),
                reverse=True
            )
            elites_viaveis = [ind for ind in elites if is_viable(ind, items, capacity)]
            escolhidos = elites_viaveis[:TAMANHO_ELITE] if len(elites_viaveis) >= TAMANHO_ELITE else elites[:TAMANHO_ELITE]
            for elite in escolhidos:
                next_generation.append(elite[:])  # cópia
        

        # Geração de descendentes
        while len(next_generation) < population_size:
            # MODO DE SELEÇÃO
            if MODO_SELECAO == "torneio":
                parent1 = tournament_selection(population, items, capacity)
                parent2 = tournament_selection(population, items, capacity)
            elif MODO_SELECAO == "roleta":
                parent1 = roulette_selection(population, items, capacity)
                parent2 = roulette_selection(population, items, capacity)
            else:
                # "misto": p1 por torneio, p2 por roleta 
                parent1 = tournament_selection(population, items, capacity)
                parent2 = roulette_selection(population, items, capacity)
            

            offspring = crossover(parent1, parent2, crossover_rate)
            mutate(offspring, mutation_rate)
            next_generation.append(offspring)

        population = next_generation[:population_size]

        # Guardar melhor da geração para análise/relatório
        best_solution = max(population, key=lambda x: fitness_function(x, items, capacity))
        best_fit = fitness_function(best_solution, items, capacity)
        evolucao_melhor_por_geracao.append(best_fit)

    # Encontrar a melhor solução na última geração
    best_solution = max(population, key=lambda x: fitness_function(x, items, capacity))

    # expõe a evolução como atributo da função (sem mudar assinatura/retorno)
    genetic_algorithm_knapsack._evolucao_melhor_por_geracao = evolucao_melhor_por_geracao

    return best_solution

# Função para gerar uma população inicial aleatória 
def generate_initial_population(size, population_size):
    population = []
    for _ in range(population_size):
        individual = [random.randint(0, 1) for _ in range(size)]  # 0 ou 1 (selecionado ou não selecionado)
        population.append(individual)
    return population

# POPULAÇÃO VIÁVEL]
def generate_viable_population(size, qtd, items, capacity):
    """
    Gera indivíduos tentando respeitar a capacidade (heurística gulosa simples + aleatoriedade).
    Não substitui a população original; apenas compõe parte dela para acelerar a convergência.
    """
    viaveis = []
    # Ordena por razão valor/peso (aproximação gulosa)
    ordem = sorted(range(size), key=lambda i: (items[i].value / items[i].weight), reverse=True)
    for _ in range(qtd):
        peso = 0
        ind = [0]*size
        # Inclui alguns dos melhores primeiro
        for i in ordem:
            if random.random() < 0.7:  # 70% de chance de tentar pegar bons itens
                if peso + items[i].weight <= capacity:
                    ind[i] = 1
                    peso += items[i].weight
        # Faz pequenas variações aleatórias
        for i in range(size):
            if random.random() < 0.05:
                if ind[i] == 0 and peso + items[i].weight <= capacity:
                    ind[i] = 1
                    peso += items[i].weight
                elif ind[i] == 1:
                    ind[i] = 0
                    peso -= items[i].weight
        viaveis.append(ind)
    return viaveis


# FITNESS GUIADO + PENALIZAÇÃO
def is_viable(solution, items, capacity):
    """Retorna True se o indivíduo respeita a capacidade."""
    total_weight = sum(item.weight for item, selected in zip(items, solution) if selected == 1)
    return total_weight <= capacity

def fitness_function(solution, items, capacity):
    """
    Função de aptidão (fitness) com suporte a:
    - MODO_AVALIACAO: "valor" (benefício total) ou "razao" (benefício/peso)
    - MODO_PENALIZACAO: "zero" (zera inviável) ou "linear" (penalização proporcional)
    Observação: assinatura original mantida.
    """
    total_value = 0
    total_weight = 0
    for item, selected in zip(items, solution):
        if selected == 1:
            total_value += item.value
            total_weight += item.weight

    # Métrica base
    if MODO_AVALIACAO == "razao":
        base_score = (total_value / total_weight) if total_weight > 0 else 0
    else:
        base_score = total_value

    # Se for viável, retorno direto da métrica base (com pequeno incentivo quanto mais “folga” sob capacidade)
    if total_weight <= capacity:
        # bônus suave por folga (quanto mais leve que a capacidade, pequeno ganho)
        folga = capacity - total_weight
        incentivo_folga = 0.01 * folga  # pequeno
        return max(0, base_score + incentivo_folga)

    # Penalização para inviáveis
    if MODO_PENALIZACAO == "zero":
        return 0

    # Penalização linear (proporcional ao excesso)
    excesso = total_weight - capacity
    media_vpw = (sum(i.value for i in items) / sum(i.weight for i in items)) if sum(i.weight for i in items) > 0 else 1
    penalidade = excesso * media_vpw * 2.0  # fator 2 deixa a punição severa, mas não zera sempre
    return max(0, base_score - penalidade)


# Função para realizar a seleção por torneio (CÓDIGO PADRÃO, com uso da fitness atual)
def tournament_selection(population, items, capacity):
    tournament_size = 5  # Tamanho do torneio
    tournament = random.sample(population, min(tournament_size, len(population)))
    best_solution = max(tournament, key=lambda x: fitness_function(x, items, capacity))
    return best_solution

# Função para realizar a seleção por roleta (CÓDIGO PADRÃO, reforçado contra soma zero)
def roulette_selection(population, items, capacity):
    fitness_values = [fitness_function(individual, items, capacity) for individual in population]
    total_fitness = sum(fitness_values)
    if total_fitness <= 0:
        # Fallback: evita erros quando todos têm fitness 0
        return random.choice(population)

    random_fitness = random.uniform(0, total_fitness)
    cumulative_fitness = 0
    for individual, fit in zip(population, fitness_values):
        cumulative_fitness += fit
        if cumulative_fitness >= random_fitness:
            return individual
    return population[-1]  # segurança

# Função para realizar o cruzamento (crossover)
def crossover(parent1, parent2, crossover_rate):
    # COMPLETAR a função de cruzamento (padrão) — IMPLEMENTADO
    # CROSSOVER MELHORADO
    # Estratégia: crossover de 1 ponto com probabilidade 'crossover_rate'.
    # Fallback: se não cruzar, retorna cópia do pai mais promissor (por diversidade, escolhe aleatoriamente).
    if random.random() > crossover_rate:
        return parent1[:] if random.random() < 0.5 else parent2[:]

    n = len(parent1)
    if n < 2:
        return parent1[:] if random.random() < 0.5 else parent2[:]

    cut = random.randint(1, n - 1)
    filho = parent1[:cut] + parent2[cut:]

    # Heurística simples: chance de “consertar” excesso removendo alguns 1s aleatórios
    if random.random() < 0.2:  # 20% de chance de ajuste pós-crossover
        for i in range(n):
            if filho[i] == 1 and random.random() < 0.05:
                filho[i] = 0
    return filho

# Função para realizar a mutação
def mutate(solution, mutation_rate):
    # COMPLETAR a função de mutação (padrão) — IMPLEMENTADO
    # MUTAÇÃO MELHORADA
    # Estratégia base: bit-flip com probabilidade 'mutation_rate' por gene.
    # Ajuste leve: se indivíduo aparenta estar pesado, chance um pouco maior de desligar bits.
    pesado_bias = 0.0
    # Como não temos 'items' aqui, aplicamos um viés neutro (mantém assinatura original).
    # O "conserto" pesado é tratado no crossover e na penalização.
    for i in range(len(solution)):
        if random.random() < (mutation_rate + pesado_bias):
            solution[i] = 1 - solution[i]


# LEITURA DE ARQUIVO
def load_items_from_file(path):
    """
    Lê arquivo de instância no formato da UC:
    - 1ª linha: capacidade (int)
    - 2ª linha: número de itens (int) — usado apenas para aviso/validação
    - Demais linhas: 'nome,peso,beneficio'
    """
    items = []
    capacity = None
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f.readlines() if ln.strip()]

    capacity = int(lines[0])
    try:
        n_items_declared = int(lines[1])
    except:
        n_items_declared = None

    for ln in lines[2:]:
        parts = [p.strip() for p in ln.split(",")]
        if len(parts) < 3:
            continue
        # nome = parts[0]  # disponível se precisar
        weight = int(parts[1])
        value = int(parts[2])
        items.append(Item(weight, value))

    if n_items_declared is not None and n_items_declared != len(items):
        print(f"Aviso: arquivo declara {n_items_declared} itens, mas foram lidos {len(items)}.")
    return items, capacity


if __name__ == "__main__":
    main()
