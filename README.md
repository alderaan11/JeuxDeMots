## Comment intérroger la console
Pour intérroger la console il suffit de lancer le code, ensuite, le terminal vous demandera un mot source, un mot cible et le nom d'une relation.    

**Exemple :**  
baobab peut voler ?  
Mot source : baobab  
Mot cible : voler  
Nom relation : r_agent-1  

On vous demandera ensuite le type d'inférence que vous voulez utiliser pour afficher la réponse, les choix sont déductive, inductive, transitive et par synonyme.
Vous répondrez par d pour déductive, i pour inductive, t pour transitive ou s pour synonyme.

## Inférences 
Voici une liste explicatives des différentes inférences que nous avons mis en place :  

- **Déduction** : Cette inférence va trouver un générique du mot source pour lequel la relation avec le mot cible existe.
 Pour trouver un générique on utilise la relation r_isa sur le mot source:  
 _mot_source r_isa générique & générique nom_relation mot_cible_ 

- **Induction** : Cette inférence trouve un spécifique du mot source pour lequel la relation est vraie.
  Pour trouver un spécifique on utilise la relation r_hipo sur le mot source:  
 _mot_source r_hypo spécifique & spécifique nom_relation mot_cible_ 

- **Transitivité** : Cette inférence trouve un mot intérmédiaire tel que le mot source est vraie avec le mot cible par transitivité.  
  _mot_source nom_relation mot_intermediaire & mot_intermediaire nom_relation mot_cible_ 
  

