import os,json, pandas as pd, numpy as np
from datetime import datetime

def create_deputee_base(id):
    path_file = 'data/all_actors/acteur/' + id +'.json'
    with open(path_file,'r') as f :
        data = json.load(f)
    name = data['acteur']['etatCivil']['ident']['nom'] + ' ' + data['acteur']['etatCivil']['ident']['prenom']
    return {
        'name' : name,
        'chair_numbers': [],
        'organ' : {}
    }

def get_organ_name(id) :
    path_file = 'data/all_actors/organe/' + id + '.json'
    if os.path.exists(path_file):
        with open(path_file,'r') as f :
            data = json.load(f)
        return {
            'id': id,
            'name' : data['organe']['libelle'],
            'name_from' : data['organe']['libelleEdition'],
            'name_short' : data['organe']['libelleAbrege'],
            'color' : data['organe']['couleurAssociee']
        }
    else :
        return {}


from datetime import datetime

def compare_date(date1_str, date2_str):
  format_date = "%Y-%m-%d"
  try:
    date1 = datetime.strptime(date1_str, format_date)
    date2 = datetime.strptime(date2_str, format_date)
    if date1 > date2:
      return True
    return False
  except ValueError:
    return "Error a date doesn't have the format AAAA-MM-JJ."
  


path = 'data/vote/'
deputees = {}

def main():
    if os.path.exists(path):
        for votes_filename in os.listdir(path):
            print(votes_filename,end='\r')
            path_file = os.path.join(path, votes_filename)
            try:
                with open(path_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Defensive coding: check if keys exist before accessing
                if 'scrutin' not in data or 'ventilationVotes' not in data['scrutin']:
                    continue

                organs_list = data['scrutin']['ventilationVotes']['organe']['groupes']['groupe']
                date = data['scrutin']['dateScrutin']

                for organ in organs_list:
                    # Assuming get_organ_name is a function you have defined
                    organ_id = organ['organeRef']
                    organ_data = get_organ_name(organ_id)
                    if organ_data :
                        votes_by_position = organ['vote']['decompteNominatif']
                        
                        # Iterate through vote positions ('pour', 'contre', 'abstention', etc.)
                        for position in votes_by_position.values():
                            # Process only if there are voters for this position
                            if position and 'votant' in position:
                                votants_data = position['votant']
                                if isinstance(votants_data, dict):
                                    votants_list = [votants_data]
                                else:
                                    votants_list = votants_data
                                for votant in votants_list:
                                    acteur_ref = votant['acteurRef']
                                    chair_number = votant['numPlace']
                                    # Get the deputy from our main dict, or create a new one
                                    deputee = deputees.get(acteur_ref)
                                    if not deputee:
                                        # Assuming create_deputee_base is a function you have defined
                                        deputee = create_deputee_base(acteur_ref)
                                    
                                    if chair_number not in deputee['chair_numbers'] :
                                        deputee['chair_numbers'].append(chair_number)
                                    
                                    if organ_id != deputee['organ'].get('id',False) and compare_date(date,deputee['organ'].get('date','1900-01-01')) :
                                        deputee['organ'] = organ_data
                                        deputee['organ']['date'] = date
                                        deputees[acteur_ref] = deputee
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Could not process file {path_file}: {e}")


    for deputee_data in deputees.values():
        # On vérifie si 'organ' existe et si 'date' est dans 'organ' avant de supprimer
        if 'organ' in deputee_data and 'date' in deputee_data['organ']:
            del deputee_data['organ']['date']

    output_dir = 'data/processed/'
    output_filename = 'deputees.json'
    with open(os.path.join(output_dir, output_filename), 'w', encoding='utf-8') as f:
        json.dump(deputees, f, indent=1, ensure_ascii=False)

    print(f"Successfully saved {len(deputees)} deputees to {output_filename}")


if __name__ == '__main__':
    main()

