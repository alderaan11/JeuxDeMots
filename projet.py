import requests
from math import *
import statistics
import json
import os 

'''
Ce qu'on a déjà fait:
- On stocke les 10 relations sortantes les plus importantes d'un noeud dans un fichier node_relation.json
- On fait un intersection des relations sortantes d'un noeud avec les relations entrantes d'un autre noeud
- On fait des relations inductives, déductives, transitives et synonymes


TODO:
    - faire le ménage dans le code (dans le désordre)
    - gérer les relations négatives 
    - est-ce qu'on doit afficher tous les types de relations (directes, inductives,...) ou demander à l'utilisateur comme fait actuellement?
    - gérer scoring avec annotations (lent pour relations sortantes, boucle infinie pour relations entrantes)
    - polysemie
    - chercher des schémas de relations supplémentaires (ex: relation de synonymie)
'''
#raffsem  id=1
#raffmorpho id=2

with open("relations.json", "r") as f:
    data = json.load(f)


url = "https://jdm-api.demo.lirmm.fr/v0/"

#Fct qui prend en paramètre un noeud et un id de relation et qui retourne les relations du noeud avec le type de relation donné par poids décroissant
#Résultats sotckés dans un fichier node_relation.json
#https://jdm-api.demo.lirmm.fr/v0/relations/from/{node_name}?types_ids={relation_id}
def relationDepuisUnNoeud(node,relationType):
    directory = "requetes/relations"
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    filename = os.path.join(directory, f"{node}_{nomRelationParType(relationType)}.json")
    if os.path.exists(filename):
        with(open(filename,"r")) as f:
            return json.load(f)
    else: 
        req = f"{url}relations/from/{node}?types_ids={relationType}"
        r = requests.get(req)

        if r.status_code == 200:
            data = r.json()

            scoring(data)

            #Trier par poids décroissant
            data_sorted = sorted(data["relations"], key=lambda x: x["w"], reverse=True) 
            data = {**data, "relations": data_sorted} 

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return data
        
        else:
            print(f"Erreur {r.status_code} lors de la requête : {req}")
            return None
        


#https://jdm-api.demo.lirmm.fr/v0/relations/to/{node2_name}
def relationVersUnNoeud(node,relationType):
    directory = "requetes/relations"
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = os.path.join(directory, f"{nomRelationParType(relationType)}_{node}.json")
    if os.path.exists(filename):
        with(open(filename,"r")) as f:
            return json.load(f)
    else: 
        req = f"{url}relations/to/{node}?types_ids={relationType}"
        r = requests.get(req)
        
        if r.status_code == 200:
            data = r.json()
            #scoring(data) 
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return data
        
        else:
            print(f"Erreur {r.status_code} lors de la requête : {req}")
            return None
    
#https://jdm-api.demo.lirmm.fr/v0/node_by_id/{node_id}
#Fct qui prend en paramètre un id de noeud et qui retourne les informations du noeud
def noeudParId(nodeid):
    req = url+"node_by_id/"+str(nodeid)
    return requests.get(req).json()


#https://jdm-api.demo.lirmm.fr/v0/from/:r{relation_id}?types_ids=998
#lien pour tester : https://jdm-api.demo.lirmm.fr/v0/relations/from/:r1863523?types_ids=998
#Fct qui prend en paramètre un id de relation et qui retourne les annotations de la relation
def getAnnotations(relationId):
    req = url+"relations/from/:r"+str(relationId)+"?types_ids=998"
    r = requests.get(req)
    if r.status_code != 200:
        return []
    else:
        r=r.json()
        annotations=[]
        for node in r["nodes"]:
            annotations.append(node["name"])
        return annotations




def normalisation(data): 
    poids = [x["w"] for x in data["relations"]]
    maxi = max(poids)
    mini = min(poids)
    for i in range(len(data["relations"])):
        data["relations"][i]["w"] = round(((data["relations"][i]["w"]-mini)/(maxi-mini)),3)
    return data
    

#Fct qui prend en paramètre un fichier et qui normalise les poids des relations
def normalisation_fichier(fichier): 
    with open(fichier, "r") as f:
        data = json.load(f)
    poids = [x["w"] for x in data["relations"]]

    maxi = max(poids)
    mini = min(poids)
    for i in range(len(data["relations"])):
        data["relations"][i]["w"] = round(((data["relations"][i]["w"]-mini)/(maxi-mini)),3)

    with open(fichier, "w") as f:
        json.dump(data, f, indent=4)





#Fct qui modifie le scoring en fonction de l'annotation de la relation
def scoring_annotation(annotations):
    coefficients = {
        "toujours vrai": 2.0, "constitutif": 1.8, "pertinent": 1.7, "vrai": 1.6, "contrastif": 1.5,
        "possible": 1.1, "probable": 1.2, "factuel": 1.4, "fréquent": 1.3,
        "improbable": 0.8,  "peu pertinent": 0.7, "non pertinent": 0.6,
        "discoursable": 0.7, "incertain": 0.7, "imaginaire": 0.5,"impossible": 0.3}
    
    valeurs = [coefficients[ann] for ann in annotations if ann in coefficients]
    return sum(valeurs) / len(valeurs) if valeurs else 1.0

def scoring(data):
    for r in data["relations"]:
        annotations = getAnnotations(r["id"])
        score = scoring_annotation(annotations)
        r["w"] *= score
    normalisation(data)
    return data

#Fct qui prend en paramètre deux listes de relations et qui retourne une liste de tuples (noeud_commun, poids)
def intersection(rel_depuis,rel_vers):
    res = []
    for r in rel_depuis["relations"]:
        for s in rel_vers["relations"]:
            if r["node2"] == s["node1"] and r["w"]>0 and s['w']>0: #Pour l'instant on supprimes les relations avec des poids négatifs
                w = statistics.geometric_mean([r["w"],s["w"]])
                res.append((r["node2"],round(w,1)))
                if len(res) == 10:
                    res = sorted(res,key=lambda x: x[1],reverse=True)
                    return res
    res = sorted(res,key=lambda x: x[1],reverse=True)
    return res


#Fct qui prend en paramètre un id de noeud et qui retourne son nom
def nomNoeudParId(nodeid):
    #print(noeudParId(nodeid))
    return noeudParId(nodeid)["name"]


#Fct qui prend en paramètre un id de relation et qui retourne son nom
def nomRelationParType(relid):
    if relid<2002:
        return data[relid]["nom"]
    else: return relid

#Fct qui prend en paramètre un nom de relation et qui retourne son id
def idRelationParNom(nom):
    for i in range(len(data)):
        if data[i]["nom"] == nom:
            return i
    return -1

print()

def __main__():
    print("Bienvenue dans le projet de recherche de relations entre les mots")

    print("Veuillez entrer le mot source")
    mot_source = input()

    print("Veuillez entrer le mot cible")
    mot_cible = input()

    print("Veuillez entrer le nom de la relation")
    nom_relation = input()
    id_relation_2 = idRelationParNom(nom_relation)
    while id_relation_2 == -1:
        print("La relation n'existe pas")
        print("Veuillez entrer le nom de la relation")
        nom_relation = input()
        id_relation_2 = idRelationParNom(nom_relation)
    
    print("Quel type d'inférence voulez-vous faire ? (déductive (d) ,inductive (i) ,transitive (t), synonyme (s))")
    type_inference = input()
    while type_inference not in ["d","i","t","s"]:
        print("Type d'inférence non reconnu")
        print("Quel type d'inférence voulez-vous faire ? (déductive (d) ,inductive (i) ,transitive (t), synonyme (s))")
        type_inference = input()
    if type_inference == "d":
        id_relation_1 = 6
    elif type_inference == "i":
        id_relation_1 = 8
    elif type_inference == "t": 
        id_relation_1 = id_relation_2
    elif type_inference == "s":
        id_relation_1 = 5
    
    print("Chargement des résultats...")
    rel_depuis = relationDepuisUnNoeud(mot_source,id_relation_1)
    rel_vers = relationVersUnNoeud(mot_cible,id_relation_2)
    res = intersection(rel_depuis,rel_vers)
    if len(res) == 0:
        print("Il n'y a pas de relation entre les deux mots")

    else:
        print("Résultats: (max 10)")              
        for i in range (len(res)):
            print(i+1,"| oui |",mot_source,nomRelationParType(id_relation_1),nomNoeudParId(res[i][0]),"&",nomNoeudParId(res[i][0]),nomRelationParType(id_relation_2),mot_cible,"| ",res[i][1])



if __name__ == "__main__":
  __main__()

