from mip import Model, xsum, maximize, BINARY

# Gegeven data
aantal_voertuigen = 15
aantal_ritten = 10

# Willekeurige gewichten en winsten voor de voertuigen en ritten (vervang deze door je eigen gegevens)

voertuig_beschikbaar = [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

# Maak een MIP-model
m = Model("Voertuig-toewijzing")

# Voeg beslissingsvariabelen toe (1 als voertuig i aan rit j wordt toegewezen, anders 0)
x = [[m.add_var(var_type=BINARY) for j in range(aantal_ritten)] for i in range(aantal_voertuigen)]

# Definieer de doelfunctie (maximaliseer de totale winst)
m.objective = maximize(0)

# Voeg beperkingen toe: elk voertuig wordt aan maximaal één rit toegewezen
for i in range(aantal_voertuigen):
    m += xsum(x[i][j] for j in range(aantal_ritten)) <= 1

# Voeg beperkingen toe: elke rit wordt aan precies één voertuig toegewezen
for j in range(aantal_ritten):
    m += xsum(x[i][j] for i in range(aantal_voertuigen)) == 1

# Voeg de extra constraint toe: elk toegewezen voertuig moet beschikbaar zijn
for j in range(aantal_ritten):
    m += xsum(x[i][j] * voertuig_beschikbaar[i] for i in range(aantal_voertuigen)) == 1

# Optimaliseer het model
m.optimize()

# Toon de toegewezen voertuigen aan ritten
toegewezen_voertuigen = []
for j in range(aantal_ritten):
    for i in range(aantal_voertuigen):
        if x[i][j].x >= 0.99:
            toegewezen_voertuigen.append(i+1)


print(f"Toegewezen voertuigen aan ritten: {toegewezen_voertuigen}")
