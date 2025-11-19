import os
import json

# Define constants for file paths - now supporting multiple legislatures
LEGISLATURE_CONFIGS = {
    '14': {
        'path': './data/vote/14/Scrutins_XIV.json',
        'output': './data/processed/vote_14.json',
        'is_single_file': True
    },
    '15': {
        'path': './data/vote/15',
        'output': './data/processed/vote_15.json',
        'is_single_file': False
    },
    '16': {
        'path': './data/vote/16',
        'output': './data/processed/vote_16.json',
        'is_single_file': False
    },
    '17': {
        'path': './data/vote/17',
        'output': './data/processed/vote_17.json',
        'is_single_file': False
    }
}


def get_voters_list(voters_data: dict or None) -> list:
    """
    Extracts a list of 'acteurRef' identifiers from a specific vote structure.
    Handles cases where 'votant' is a single dictionary (one voter) 
    or a list of dictionaries (multiple voters).

    Args:
        voters_data: A dictionary containing the 'votant' key, or None. 
                     Expected keys are 'pours', 'contres', etc.

    Returns:
        A list of 'acteurRef' strings, or an empty list if data is missing or None.
    """
    # Handle non-dict types (strings, None, etc.)
    if not isinstance(voters_data, dict):
        return []
    
    votants = voters_data.get("votant")
    if votants is None:
        return []

    if isinstance(votants, list):
        # List comprehension is a concise way to extract all 'acteurRef'
        return [voter.get("acteurRef", "") for voter in votants if isinstance(voter, dict)]
    elif isinstance(votants, dict):
        # Single voter case
        acteur_ref = votants.get("acteurRef", "")
        return [acteur_ref] if acteur_ref else []
    else:
        return []


# --- NEW helper to accept multiple possible key names (singular/plural) ---
def extend_from_positions(collector: list, voters: dict, *keys):
    """
    Add voters to collector checking multiple possible keys (e.g. "pours" or "pour").
    """
    if not isinstance(voters, dict):
        return
    for k in keys:
        collector.extend(get_voters_list(voters.get(k)))


def process_single_vote_json(scrutin: dict) -> dict or None:
    """
    Processes a single vote (scrutin) structure and returns the vote data.
    
    Args:
        scrutin: A dictionary containing vote information
    
    Returns:
        A dictionary with vote data, or None if vote_id is missing
    """
    vote_id = scrutin.get("uid")
    date_scrutin = scrutin.get("dateScrutin")
    type_vote_data = scrutin.get("typeVote", {})
    code_type_vote = type_vote_data.get("codeTypeVote") if isinstance(type_vote_data, dict) else None
    
    if not vote_id:
        print(f"Missing vote ID in scrutin, skipping.")
        return None

    # Initialize lists to hold actor references
    votes_for = []
    votes_against = []
    votes_novote = []
    votes_abs = []

    # Access the list of groups, handling potential missing keys and unexpected types
    ventilation = scrutin.get("ventilationVotes", {})
    if not isinstance(ventilation, dict):
        # If ventilationVotes is not a dict (e.g., empty string), skip vote processing
        return {
            "date": date_scrutin,
            "type": code_type_vote,
            "votes_for": votes_for,
            "votes_against": votes_against,
            "votes_abs": votes_abs
        }
    
    organe = ventilation.get("organe", {})
    if not isinstance(organe, dict):
        return {
            "date": date_scrutin,
            "type": code_type_vote,
            "votes_for": votes_for,
            "votes_against": votes_against,
            "votes_abs": votes_abs
        }
    
    groupes_data = organe.get("groupes", {})
    if not isinstance(groupes_data, dict):
        return {
            "date": date_scrutin,
            "type": code_type_vote,
            "votes_for": votes_for,
            "votes_against": votes_against,
            "votes_abs": votes_abs
        }
    
    organ_list = groupes_data.get("groupe")
    
    # Handle the case where 'groupe' might be a single dict instead of a list
    if not organ_list:
        organ_list = []
    elif isinstance(organ_list, dict):
        organ_list = [organ_list]
    elif not isinstance(organ_list, list):
        organ_list = []

    # Iterate through all groups and aggregate votes
    for organ in organ_list:
        if not isinstance(organ, dict):
            continue
            
        vote_data = organ.get("vote", {})
        if not isinstance(vote_data, dict):
            continue
            
        voters = vote_data.get("decompteNominatif", {})
        if not isinstance(voters, dict):
            continue
            
        # Support both plural (pours/contres) and singular (pour/contre) keys used across legislatures
        extend_from_positions(votes_for, voters, "pours", "pour")
        extend_from_positions(votes_against, voters, "contres", "contre")
        extend_from_positions(votes_novote, voters, "nonVotants", "nonVotant")
        extend_from_positions(votes_abs, voters, "abstentions", "abstention")

    return {
        "date": date_scrutin,
        "type": code_type_vote,
        "votes_for": votes_for,
        "votes_against": votes_against,
        "votes_abs": votes_abs
    }


def process_folder_format(folder: str) -> dict:
    """
    Processes vote JSON files from a folder (legislatures 15, 16, 17).
    
    Args:
        folder: The path to the folder containing the JSON files.
    
    Returns:
        Dictionary with vote_id as keys and vote data as values
    """
    legislature_vote = {}
    
    for entry in os.scandir(folder):
        if entry.is_file() and entry.name.endswith('.json'):
            file_name = entry.name
            complete_path = entry.path
            print(f"--- Processing file: {file_name} ---")

            try:
                with open(complete_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"JSON decoding error in {file_name}: {e}")
                continue

            scrutin = json_data.get("scrutin", {})
            vote_data = process_single_vote_json(scrutin)
            
            if vote_data:
                vote_id = scrutin.get("uid")
                legislature_vote[vote_id] = vote_data

    return legislature_vote


def process_single_file_format(file_path: str) -> dict:
    """
    Processes a single JSON file containing all votes (legislature 14).
    
    Args:
        file_path: The path to the JSON file
    
    Returns:
        Dictionary with vote_id as keys and vote data as values
    """
    legislature_vote = {}
    
    print(f"--- Processing single file: {file_path} ---")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"JSON decoding error in {file_path}: {e}")
        return legislature_vote
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return legislature_vote
    
    # Extract the list of scrutins
    scrutins_list = json_data.get("scrutins", {}).get("scrutin", [])
    
    if not isinstance(scrutins_list, list):
        print(f"Warning: 'scrutin' is not a list in {file_path}")
        return legislature_vote
    
    print(f"Found {len(scrutins_list)} votes in file")
    
    for scrutin in scrutins_list:
        vote_data = process_single_vote_json(scrutin)
        
        if vote_data:
            vote_id = scrutin.get("uid")
            legislature_vote[vote_id] = vote_data
    
    return legislature_vote


def process_legislature(config: dict) -> None:
    """
    Processes a legislature based on its configuration.
    
    Args:
        config: Dictionary with 'path', 'output', and 'is_single_file' keys
    """
    path = config['path']
    output_file = config['output']
    is_single_file = config['is_single_file']
    
    print(f"\n{'='*60}")
    print(f"Processing: {path}")
    print(f"Output: {output_file}")
    print(f"{'='*60}\n")
    
    if is_single_file:
        legislature_vote = process_single_file_format(path)
    else:
        legislature_vote = process_folder_format(path)
    
    if legislature_vote:
        print(f"\n✅ Writing final output file: {output_file}")
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(legislature_vote, f, indent=4)
        print(f"✅ Successfully processed {len(legislature_vote)} votes")
    else:
        print(f"\n⚠️ No votes processed for {path}. Output file was not created.")


if __name__ == "__main__":
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