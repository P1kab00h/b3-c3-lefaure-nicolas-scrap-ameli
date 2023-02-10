# Liste des librairies à importer pour le scrapping ==>
# pip install requests
# pip install beautifulsoup4
# pip install pandas
import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd

# URL WEB sur lequel on va lancer le scrapp ==>
url = "http://annuairesante.ameli.fr/recherche.html"
# Les différents types de header possible (selon le navigateur), trouvable avec le f12 ; onglet headers ; section "Request headers" => "User-Agents" ==>
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/189.8.0.8 Safari/537.36"
}
# création de la var req (session de request créé)
req = requests.session()

# On ajoute les paramètres de notre recherche, avec f12 récupérer recherche.html ; payload ; puis récupérer les infos "id" : "value" ==>
payload = {
    "type": "ps",
    "ps_profession": "34",
    "ps_profession_label": "Médecin généraliste",
    "ps_localisation": "HERAULT (34)",
    "localisation_category": "departements",
}

# On effectue une requête post avec 3 paramètres, l'url de la recherche, les éléments de recherche et le header
# qui permet de simuler le fonctionnement d'un navigateur web
page = req.post(url, params=payload, headers=header)

# Si retour OK alors
if page.status_code == 200:
    lienrecherche = page.url

# beautifulSoup, outil de scrapping, va nous permettre de récupérer les infos html d'un page (https://beautiful-soup-4.readthedocs.io/en/latest/)
soup = BeautifulSoup(page.text, 'html.parser')

# Pour scrapper, on isole dans un premier temps la div dans laquelle les informations que l'on souhaite récupérer se trouvent, puis la class (pour afiner la sélection).
# ici le .find_all va récupérer tous les éléments correspondant au tag 'div avec la class 'item-professionnel')
medecins = soup.find_all("div", class_="item-professionnel")

# Je déclare un tableau vide, qui va acceuilir les données récupérées
listeMedecins = []

# Pour remplir ce tableau, j'effectue un for
# L'idée est qu'on ne consultera que la page sur laquelle on tombe, sauf que la page est chargée aléatoirement
# Il y a plus de 1000 médecins en tout donc (20 par pages sur 50 pages) donc je boucle sur 1001
for i in range(1001):
    for medecin in medecins[:71]:
        # Je récupère le nom du médecin en ciblant précisément la div dans laquelle il est, le .strip() pour se débarasser des exapces avant après (par défaut si rien dans les ())
        nomMedecins = medecin.find("div", class_="nom_pictos").text.strip()
        # Certains numéros sont "Null", le "None" permet d'éviter une erreur (si pas de numéro valeur par défaut)
        numeroMedecins = None
        if medecin.find("div", class_="tel") is not None:
            numeroMedecins = medecin.find("div", class_="tel").text.strip()
        adresseMedecins = medecin.find("div", class_="adresse").text.strip()
        # Je rentre dans mon tableau listeMedecins toutes les informations avec les entêtes marquées entre guillemets
        listeMedecins.append(
            {"nom": nomMedecins, "numero": numeroMedecins, "adresse": adresseMedecins})

# Création du fichier csv "medecins_generalistes.csv"
# Le 'w+' permet d'écrire dans le fichier, comme en linux (r w x). Si tu veux donner le pouvoir d'écraser tout le fichier pour réécrire dessus mets un r+
# Bien penser à créer le fichier csv avant d'exécuter le code, tu lances un excel et tu le transformes en csv. Sinon erreur ==>
with open('medecins_generalistes.csv', 'w+') as fichier_csv:
    # On configure le fichier CSV
    writer = csv.DictWriter(
        fichier_csv, fieldnames=listeMedecins[0].keys(), delimiter=";")
    # Va nous permettre de définir le "noms des colonnes" (en lien avec nom, numero, adresse)
    writer.writeheader()
    # J'écris chaque ligne en reprenant mon tableau
    writer.writerows(listeMedecins)

############
# Cette partie doit permettre d'enlever les doublons se trouvant dans le fichier CSV.
# Utilisation de la lib Pandas =>
# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop_duplicates.html
file_name = open("medecins_generalistes.csv", "r")
file_name_output = open("medecins_generalistes_without_dupes.csv", "w+")

df = pd.read_csv(file_name, sep="\t or ,")

# Notes:
# - the `subset=None` means that every column is used
#    to determine if two rows are different; to change that specify
#    the columns as an array
# - the `inplace=True` means that the data structure is changed and
#   the duplicate rows are gone
df.drop_duplicates(inplace=True)

# Write the results to a different file
df.to_csv(file_name_output, index=False)

# Pour vérification =>
print(listeMedecins)
