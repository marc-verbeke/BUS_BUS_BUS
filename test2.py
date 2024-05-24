import pandas as pd
from mip import Model, xsum, maximize, BINARY

diensten_nummer = []
diensten_stelplaats = []
diensten_type = []
diensten_subtype = []

voertuigen_nummer = []
voertuigen_stelplaats = []
voertuigen_type = []
voertuigen_subtype = []
voertuigen_beschikbaar = []

excel_file_path_diensten = "data/test_diensten.xlsx"
diensten = pd.read_excel(excel_file_path_diensten)

excel_file_path_voertuigen = "data/test_voertuigen.xlsx"
voertuigen = pd.read_excel(excel_file_path_voertuigen)

aantal_voertuigen = len(voertuigen)
aantal_diensten = len(diensten)

for x in range(len(diensten)):
    diensten_nummer.append(diensten.iloc[x, 0])
    diensten_stelplaats.append(diensten.iloc[x, 1])
    diensten_type.append(diensten.iloc[x, 2])
    diensten_subtype.append(diensten.iloc[x, 3])

for x in range(len(voertuigen)):
    voertuigen_nummer.append(voertuigen.iloc[x, 0])
    voertuigen_stelplaats.append(voertuigen.iloc[x, 1])
    voertuigen_type.append(voertuigen.iloc[x, 2])
    voertuigen_subtype.append(voertuigen.iloc[x, 3])
    voertuigen_beschikbaar.append(voertuigen.iloc[x, 11])

# Maak een MIP-model
m = Model("Voertuig-toewijzing")

# Voeg beslissingsvariabelen toe (1 als voertuig i aan rit j wordt toegewezen, anders 0)
x = [[m.add_var(var_type=BINARY) for j in range(aantal_diensten)] for i in range(aantal_voertuigen)]

# Voeg beperkingen toe: elk voertuig wordt aan maximaal één rit toegewezen
for i in range(aantal_voertuigen):
    m += xsum(x[i][j] for j in range(aantal_diensten)) <= 1

# elke rit wordt aan precies één voertuig toegewezen
for j in range(aantal_diensten):
    m += xsum(x[i][j] for i in range(aantal_voertuigen)) == 1

# elk toegewezen voertuig moet beschikbaar zijn
for j in range(aantal_diensten):
    m += xsum(x[i][j] * voertuigen_beschikbaar[i] for i in range(aantal_voertuigen)) == 1

# diensten_type moet gelijk zijn aan voertuigen_type
for j in range(aantal_diensten):
    for i in range(aantal_voertuigen):
        if diensten_type[j] == voertuigen_type[i]:
            m += x[i][j] == 1
        else:
            m += x[i][j] == 0

# Optimaliseer het model
m.optimize()

# Toon de toegewezen voertuigen aan ritten (bijvoorbeeld)
toegewezen_voertuigen = []
for j in range(aantal_diensten):
    for i in range(aantal_voertuigen):
        if x[i][j].x >= 0.99:
            toegewezen_voertuigen.append(i + 1)

print(f"Toegewezen voertuigen aan ritten: {toegewezen_voertuigen}")
