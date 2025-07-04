# Pondération des critères
ALPHA, BETA, GAMMA, DELTA = 0.4, 0.1, 0.4, 0.1
USER_LOAD_UNITS = 1
# Métriques initiales des liens
"""original_link_metrics = {
    ('gNB1', 'I-UPF'):        {'latency': 10,  'distance': 10, 'load': 0, 'capacity': 800},
    ('I-UPF', 'PSA-UPF'):     {'latency': 10,  'distance': 10, 'load': 0, 'capacity': 800},
    ('I-UPF', 'I-UPF2'):      {'latency': 10,  'distance': 10, 'load': 0, 'capacity': 800},
    ('I-UPF2', 'PSA-UPF2'):   {'latency': 10,  'distance': 10, 'load': 0, 'capacity': 800},
    ('I-UPF', 'I-UPF3'):      {'latency': 10,  'distance': 10, 'load': 0, 'capacity': 800},
    ('I-UPF3', 'PSA-UPF3'):   {'latency': 10,  'distance': 10, 'load': 0, 'capacity': 800},
}"""
original_link_metrics = {
    ('gNB1', 'I-UPF'):        {'latency': 4,  'distance': 10, 'load': 0, 'capacity': 20},
    ('I-UPF', 'I-UPF2'):      {'latency': 8,  'distance': 12, 'load': 0, 'capacity': 20},
    ('I-UPF2', 'I-UPF3'):     {'latency': 5,  'distance': 8,  'load': 0, 'capacity': 20},
    ('I-UPF3', 'PSA-UPF'):    {'latency': 2,  'distance': 11, 'load': 0, 'capacity': 20},
    ('I-UPF', 'I-UPF4'):      {'latency': 3,  'distance': 14, 'load': 0, 'capacity': 20},
    ('I-UPF4', 'PSA-UPF2'):   {'latency': 4,  'distance': 9,  'load': 0, 'capacity': 20},
    ('I-UPF', 'I-UPF5'):      {'latency': 5,  'distance': 16, 'load': 0, 'capacity': 20},
    ('I-UPF5', 'PSA-UPF3'):   {'latency': 5,  'distance': 11, 'load': 0, 'capacity': 20},
    
    
}


# Liste des chemins
paths = {
    "path1": [('gNB1', 'I-UPF'), ('I-UPF', 'I-UPF2'), ('I-UPF2', 'I-UPF3'), ('I-UPF3', 'PSA-UPF')],
    "path2": [('gNB1', 'I-UPF'), ('I-UPF', 'I-UPF4'), ('I-UPF4', 'PSA-UPF2')],
    "path3": [('gNB1', 'I-UPF'), ('I-UPF', 'I-UPF5'), ('I-UPF5', 'PSA-UPF3')],
}

# Fonction pour calculer le coût d’un lien
def compute_link_cost(metrics):
    return round(
        ALPHA * metrics['latency'] +
        BETA * metrics['distance'] +
        GAMMA * metrics['load'] +
        DELTA * (1 / metrics['capacity']),
        4
    )

# Fonction pour recalculer tous les coûts des liens
def recalculate_link_costs(link_metrics):
    return {link: compute_link_cost(metrics) for link, metrics in link_metrics.items()}

# Fonction pour calculer le coût total d’un chemin
def compute_path_cost(path, link_costs):
    total = 0
    for hop in path:
        total += link_costs.get(hop, 9999)
    return round(total, 4)

# Fonction pour recalculer tous les coûts des chemins
def recalculate_path_costs(paths, link_costs):
    return {name: compute_path_cost(path, link_costs) for name, path in paths.items()}

# Fonction pour incrémenter le load sur les liens utilisés
# OOOOOLD version
def increase_load(path, link_metrics):
    for hop in path:
        if hop in link_metrics:
            link_metrics[hop]['load'] += 1 
# new version 
"""def increase_load(path, link_metrics):
    for hop in path:
        if hop in link_metrics:
            capacity = link_metrics[hop]['capacity']
            link_metrics[hop]['load'] += USER_LOAD_UNITS 
            # S'assurer que le load ne dépasse pas 1.0
            link_metrics[hop]['load'] = min(link_metrics[hop]['load'], 1.0)

"""
# Initialiser les données modifiables
link_metrics = {k: v.copy() for k, v in original_link_metrics.items()}
link_costs = recalculate_link_costs(link_metrics)
path_costs = recalculate_path_costs(paths, link_costs)

# Structure pour stocker les chemins choisis pour chaque user
user_assignments = {}

# Boucle sur les utilisateurs
N = 60 # elle egal a la somme des capacite des upf terminal(PSA-UPFs) donc elle genere des le demarage de reseau les path optimal pour la capacite que le reseau peut simuler 
# ensuite chaq utilisateur va etre affacetr a son chemin par rapport a son id car dans la creation de users , les id sont auto incrementer 
start_imsi = 208930000000001

for i in range(N):
    user_id = f"imsi-{start_imsi + i}"

    # Trouver le chemin avec coût minimal
    best_path_name = min(path_costs, key=path_costs.get)
    best_path = paths[best_path_name]

    # Reformater le chemin dans le format souhaité
    formatted_path = [{'A': hop[0], 'B': hop[1]} for hop in best_path]

    # Stocker l’assignement
    user_assignments[user_id] = {
        'chosen_path': best_path_name,
        'path_cost': path_costs[best_path_name],
        'full_path': formatted_path  # format structuré A → B
    }

    # Mettre à jour les charges
    increase_load(best_path, link_metrics)
    link_costs = recalculate_link_costs(link_metrics)
    path_costs = recalculate_path_costs(paths, link_costs)

# ✅ Affichage final avec format structuré
print("\n=== Affectation des utilisateurs ===")
for user, data in user_assignments.items():
    print(f"\n{user} -> {data['chosen_path']} | Total Cost: {data['path_cost']}")
    print("  Topology:")
    for hop in data['full_path']:
        print(f"    - A: {hop['A']}\n      B: {hop['B']}")
# ✅ Regroupement 
from collections import defaultdict

# Regroupement des utilisateurs par chemin
path_to_users = defaultdict(list)
path_to_topology = {}

# Construire une clé unique pour chaque chemin
for user_id, data in user_assignments.items():
    # Clé : tuple de tuples ((A1,B1), (A2,B2), ...)
    path_key = tuple((hop['A'], hop['B']) for hop in data['full_path'])
    path_to_users[path_key].append(user_id)
    path_to_topology[path_key] = data['full_path']

# Création de la structure groupée
grouped_users = {}
for idx, (path_key, users) in enumerate(path_to_users.items(), start=1):
    group_name = f"UE{idx}"
    grouped_users[group_name] = {
        'members': users,
        'topology': path_to_topology[path_key]
    }

# ✅ Affichage final du regroupement
print("\n=== Regroupement des utilisateurs par chemin ===")
for group_name, group_data in grouped_users.items():
    print(f"\n{group_name}:")
    print("  members:")
    for user in group_data['members']:
        print(f"    - {user}")
    print("  topology:")
    for hop in group_data['topology']:
        print(f"    - A: {hop['A']}\n      B: {hop['B']}")




# UPDATIIIIIIING FOR THIS PART 
import yaml

# Construction du dictionnaire YAML final
routing_data = {
    'info': {
        'version': '1.0.7',
        'description': 'Routing information for UE'
    },
    'ueRoutingInfo': {}
}

for group_name, group_data in grouped_users.items():
    routing_data['ueRoutingInfo'][group_name] = {
        'members': group_data['members'],
        'topology': [{'A': hop['A'], 'B': hop['B']} for hop in group_data['topology']]
    }

# ✅ Affichage au format YAML
print("\n=== YAML Routing Structure ===")
print(yaml.dump(routing_data, sort_keys=False))

import os
import yaml

# === Construction du dictionnaire YAML (déjà fait dans les étapes précédentes) ===
routing_data = {
    'info': {
        'version': '1.0.7',
        'description': 'Routing information for UE'
    },
    'ueroutingInfo': {}
}

for group_name, group_data in grouped_users.items():
    routing_data['ueroutingInfo'][group_name] = {
        'members': group_data['members'],
        'topology': [{'A': hop['A'], 'B': hop['B']} for hop in group_data['topology']]
    }

# === Écriture dans le fichier YAML dans le même dossier ===
file_path = os.path.join(os.getcwd(), "uerouting.yaml")

with open(file_path, "w") as f:
    yaml.dump(routing_data, f, sort_keys=False)

print(f"\n✅ Données YAML injectées avec succès dans le fichier : {file_path}")
