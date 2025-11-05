import os
import json

# Define constants for file paths
FOLDER_PATH = './data/vote'
OUTPUT_FILE = './data/processed/vote_17.json'


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
    if voters_data is None:
        return []
    
    votants = voters_data.get("votant")
    if votants is None:
        return []

    if isinstance(votants, list):
        # List comprehension is a concise way to extract all 'acteurRef'
        return [voter["acteurRef"] for voter in votants]
    else: # Assumes it's a single dictionary
        return [votants["acteurRef"]]


def process_json_files(folder: str):
    """
    Processes all vote JSON files in a specified folder, aggregates the results,
    and writes the final structure to a single JSON file.
    
    Args:
        folder: The path to the folder containing the JSON files.
    """
    legislature_vote = {}
    
    for entry in os.scandir(folder):
        # Filter for files ending with '.json'
        if entry.is_file() and entry.name.endswith('.json'):
            file_name = entry.name
            complete_path = entry.path
            print(f"--- Processing file: {file_name} ---")

            try:
                # Open and load the JSON file
                with open(complete_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"JSON decoding error in {file_name}: {e}")
                continue # Skip to the next file upon error

            # Safely retrieve primary data using .get()
            scrutin = json_data.get("scrutin", {})
            vote_id = scrutin.get("uid")
            date_scrutin = scrutin.get("dateScrutin")
            code_type_vote = scrutin.get("typeVote", {}).get("codeTypeVote")
            
            if not vote_id:
                print(f"Missing vote ID in {file_name}, skipping.")
                continue

            # Initialize lists to hold actor references
            votes_for = []
            votes_against = []
            votes_novote = []
            votes_abs = []

            # Access the list of groups, handling potential missing keys
            groupes_data = scrutin.get("ventilationVotes", {}).get("organe", {}).get("groupes", {})
            organ_list = groupes_data.get("groupe")
            
            # Handle the case where 'groupe' might be a single dict instead of a list
            if not organ_list and isinstance(groupes_data.get("groupe"), dict):
                 organ_list = [groupes_data.get("groupe")]
            elif not organ_list:
                organ_list = [] # Ensure it's an iterable list

            # Iterate through all groups and aggregate votes
            for organ in organ_list:
                # Safely get the detailed vote count
                voters = organ.get("vote", {}).get("decompteNominatif", {})

                votes_for.extend(get_voters_list(voters.get("pours")))
                votes_against.extend(get_voters_list(voters.get("contres")))
                votes_novote.extend(get_voters_list(voters.get("nonVotants")))
                votes_abs.extend(get_voters_list(voters.get("abstentions")))

            # Store the vote data using the vote ID as the key
            legislature_vote[vote_id] = {
                "date": date_scrutin,
                "type": code_type_vote,
                "votes_for": votes_for,
                "votes_against": votes_against,
                # 'votes_novote' is gathered but not included in the final structure
                # to match the original function's output structure.
                "votes_abs": votes_abs
            }

    if legislature_vote:
        print(f"\n✅ Writing final output file: {OUTPUT_FILE}")
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            # Use indent=4 for readable formatting
            json.dump(legislature_vote, f, indent=4)
    else:
        print("\n⚠️ No votes processed. Output file was not created.")


if __name__ == "__main__":
    process_json_files(FOLDER_PATH)