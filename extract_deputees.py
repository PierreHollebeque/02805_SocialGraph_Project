import os,json
from datetime import datetime

# Legislature configurations
LEGISLATURE_CONFIGS = {
    '14': {
        'vote_path': 'data/vote/14/Scrutins_XIV.json',
        'cr_path': None,  # No compte rendu for 14
        'output': 'data/processed/deputees_14.json',
        'is_single_file': True
    },
    '15': {
        'vote_path': 'data/vote/15',
        'cr_path': None,  # No compte rendu for 15
        'output': 'data/processed/deputees_15.json',
        'is_single_file': False
    },
    '16': {
        'vote_path': 'data/vote/16',
        'cr_path': None,  # No compte rendu for 16
        'output': 'data/processed/deputees_16.json',
        'is_single_file': False
    },
    '17': {
        'vote_path': 'data/vote/17',
        'cr_path': 'data/cr/',
        'output': 'data/processed/deputees_17.json',
        'is_single_file': False
    }
}

def create_deputee_base(id):
    path_file = 'data/all_actors/acteur/' + id +'.json'
    with open(path_file,'r') as f :
        data = json.load(f)
    name = data['acteur']['etatCivil']['ident']['nom'] + ' ' + data['acteur']['etatCivil']['ident']['prenom']
    return {
        'name' : name,
        'chair_numbers': [],
        'organ' : {},
        'speeches': []
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
  


def process_compte_rendu_files(deputees, cr_path):
    """Process all compte_rendu JSON files to track deputy speeches."""
    
    if not cr_path or not os.path.exists(cr_path):
        print(f"Skipping compte_rendu processing (path: {cr_path})")
        return
    
    file_count = 0
    for cr_filename in os.listdir(cr_path):
        if not cr_filename.endswith('.json'):
            continue
            
        file_count += 1
        print(f"Processing compte_rendu: {cr_filename}", end='\r')
        
        cr_file_path = os.path.join(cr_path, cr_filename)
        try:
            with open(cr_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Navigate to contenu/point
            if 'contenu' not in data:
                continue
                
            contenu = data['contenu']
            
            # Handle both single point and list of points
            points = []
            if 'point' in contenu:
                point_data = contenu['point']
                if isinstance(point_data, list):
                    points = point_data
                elif isinstance(point_data, dict):
                    points = [point_data]
            
            # Process each point
            for point in points:
                if 'paragraphe' not in point:
                    continue
                
                paragraphes = point['paragraphe']
                if isinstance(paragraphes, dict):
                    paragraphes = [paragraphes]
                
                # Process each paragraph
                for para in paragraphes:
                    if not isinstance(para, dict):
                        continue
                    
                    # Check if paragraph has orateurs and a speaker
                    if 'orateurs' in para and para['orateurs']:
                        orateurs = para['orateurs']
                        
                        # Handle both single orateur and list of orateurs
                        orateur_list = []
                        if 'orateur' in orateurs:
                            orateur_data = orateurs['orateur']
                            if isinstance(orateur_data, list):
                                orateur_list = orateur_data
                            elif isinstance(orateur_data, dict):
                                orateur_list = [orateur_data]
                        
                        # Process each speaker
                        for orateur in orateur_list:
                            if 'id' in orateur:
                                acteur_id = 'PA' + orateur['id']
                                
                                # Get or create deputy
                                if acteur_id not in deputees:
                                    try:
                                        deputees[acteur_id] = create_deputee_base(acteur_id)
                                    except:
                                        continue
                                
                                # Extract text from paragraph
                                text = ""
                                if 'texte' in para:
                                    text = para['texte']

                                deputees[acteur_id]['speeches'].append(text)
        
        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            print(f"Could not process file {cr_file_path}: {e}")
    
    print(f"\nProcessed {file_count} compte_rendu files")

def process_single_vote_file(vote_data, deputees):
    """Process a single vote data structure (for both formats)."""
    try:
        # Check if this is a scrutin wrapper or direct scrutin
        scrutin = vote_data.get('scrutin', vote_data)
        
        if 'ventilationVotes' not in scrutin:
            return
        
        ventilation = scrutin['ventilationVotes']
        if not isinstance(ventilation, dict):
            return
            
        organe = ventilation.get('organe', {})
        if not isinstance(organe, dict):
            return
            
        groupes = organe.get('groupes', {})
        if not isinstance(groupes, dict):
            return
            
        organs_list = groupes.get('groupe', [])
        if isinstance(organs_list, dict):
            organs_list = [organs_list]
        
        date = scrutin.get('dateScrutin', '1900-01-01')

        for organ in organs_list:
            if not isinstance(organ, dict):
                continue
                
            organ_id = organ.get('organeRef')
            if not organ_id:
                continue
                
            organ_data = get_organ_name(organ_id)
            if not organ_data:
                continue
                
            vote_data_nested = organ.get('vote', {})
            if not isinstance(vote_data_nested, dict):
                continue
                
            votes_by_position = vote_data_nested.get('decompteNominatif', {})
            if not isinstance(votes_by_position, dict):
                continue
            
            # Iterate through vote positions
            for position in votes_by_position.values():
                if not isinstance(position, dict):
                    continue
                    
                if position and 'votant' in position:
                    votants_data = position['votant']
                    if isinstance(votants_data, dict):
                        votants_list = [votants_data]
                    else:
                        votants_list = votants_data
                    
                    for votant in votants_list:
                        if not isinstance(votant, dict):
                            continue
                            
                        acteur_ref = votant.get('acteurRef')
                        chair_number = votant.get('numPlace')
                        
                        if not acteur_ref:
                            continue
                        
                        # Get the deputy from our main dict, or create a new one
                        deputee = deputees.get(acteur_ref)
                        if not deputee:
                            try:
                                deputee = create_deputee_base(acteur_ref)
                            except:
                                continue
                        
                        if chair_number and chair_number not in deputee['chair_numbers']:
                            deputee['chair_numbers'].append(chair_number)
                        
                        if organ_id != deputee['organ'].get('id', False) and compare_date(date, deputee['organ'].get('date', '1900-01-01')):
                            deputee['organ'] = organ_data
                            deputee['organ']['date'] = date
                        
                        deputees[acteur_ref] = deputee
    except Exception as e:
        print(f"Error processing vote: {e}")

def process_folder_format(vote_path, deputees):
    """Process votes from a folder of JSON files."""
    if not os.path.exists(vote_path):
        print(f"Warning: Vote directory not found at {vote_path}")
        return
    
    file_count = 0
    for votes_filename in os.listdir(vote_path):
        if not votes_filename.endswith('.json'):
            continue
            
        file_count += 1
        print(f"Processing vote file: {votes_filename}", end='\r')
        
        path_file = os.path.join(vote_path, votes_filename)
        try:
            with open(path_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            process_single_vote_file(data, deputees)
        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            print(f"Could not process file {path_file}: {e}")
    
    print(f"\nProcessed {file_count} vote files from folder")

def process_single_file_format(vote_path, deputees):
    """Process votes from a single consolidated JSON file (legislature 14)."""
    if not os.path.exists(vote_path):
        print(f"Warning: Vote file not found at {vote_path}")
        return
    
    print(f"Processing single vote file: {vote_path}")
    
    try:
        with open(vote_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        scrutins_list = data.get("scrutins", {}).get("scrutin", [])
        
        if not isinstance(scrutins_list, list):
            print(f"Warning: 'scrutin' is not a list in {vote_path}")
            return
        
        print(f"Found {len(scrutins_list)} votes in file")
        
        for idx, scrutin in enumerate(scrutins_list):
            if idx % 100 == 0:
                print(f"Processing vote {idx}/{len(scrutins_list)}", end='\r')
            process_single_vote_file(scrutin, deputees)
        
        print(f"\nProcessed {len(scrutins_list)} votes from single file")
    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        print(f"Could not process file {vote_path}: {e}")

def process_legislature(config):
    """Process a single legislature based on its configuration."""
    vote_path = config['vote_path']
    cr_path = config['cr_path']
    output_path = config['output']
    is_single_file = config['is_single_file']
    
    print(f"\n{'='*60}")
    print(f"Processing: {vote_path}")
    print(f"Output: {output_path}")
    print(f"{'='*60}\n")
    
    deputees = {}
    
    # Process votes
    if is_single_file:
        process_single_file_format(vote_path, deputees)
    else:
        process_folder_format(vote_path, deputees)
    
    # Process compte rendu (only for legislature 17)
    if cr_path:
        print("\nProcessing compte_rendu files...")
        process_compte_rendu_files(deputees, cr_path)
    
    # Clean up temporary date fields
    for deputee_data in deputees.values():
        if 'organ' in deputee_data and 'date' in deputee_data['organ']:
            del deputee_data['organ']['date']
    
    # Save results
    if deputees:
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(deputees, f, indent=1, ensure_ascii=False)
        
        print(f"\n✅ Successfully saved {len(deputees)} deputees to {output_path}")
    else:
        print(f"\n⚠️ No deputees found for {vote_path}")

def main():
    # Process all legislatures
    for legislature_num, config in LEGISLATURE_CONFIGS.items():
        print(f"\n\n{'#'*60}")
        print(f"# LEGISLATURE {legislature_num}")
        print(f"{'#'*60}")
        
        try:
            process_legislature(config)
        except Exception as e:
            print(f"❌ Error processing legislature {legislature_num}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n\n{'='*60}")
    print("ALL LEGISLATURES PROCESSED")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()

