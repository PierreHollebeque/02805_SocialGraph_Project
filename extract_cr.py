import json
import requests
from pathlib import Path
import time
from typing import Set

def collect_seance_refs(vote_folder: str) -> Set[str]:
    """
    Collect all unique seanceRef values from vote files.
    
    Args:
        vote_folder: Path to the vote folder
        
    Returns:
        Set of unique seanceRef values (excluding None/null)
    """
    print(f"Collecting seanceRef from vote files in {vote_folder}...")
    vote_folder_path = Path(vote_folder)
    seance_refs = set()
    
    for vote_file in vote_folder_path.glob("*.json"):
        try:
            data = json.loads(vote_file.read_text(encoding="utf-8"))
            scrutin = data.get("scrutin", {})
            seance_ref = scrutin.get("seanceRef")

            if seance_ref:  # Only add non-null values
                seance_refs.add(seance_ref)
                
        except Exception as e:
            print(f"Error processing {vote_file.name}: {e}")
            continue
    
    print(f"Found {len(seance_refs)} unique Seance references")
    return seance_refs


def get_compte_rendu_ref(seance_id: str) -> str:
    """
    Download seance data and extract compteRenduRef.
    
    Args:
        seance_id: The Seance ID
        
    Returns:
        The compteRenduRef value, or None if not found
    """
    url = f"https://www.assemblee-nationale.fr/dyn/opendata/{seance_id}.json"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        compte_rendu_ref = data.get("compteRenduRef")
        
        return compte_rendu_ref
        
    except Exception as e:
        print(f"  ✗ Error getting compteRenduRef for {seance_id}: {e}")
        return None


def download_compte_rendu(cr_id: str, output_folder: Path) -> bool:
    """
    Download a Compte Rendu in both XML formats.
    
    Args:
        cr_id: The Compte Rendu ID
        output_folder: Folder to save the downloaded files
        
    Returns:
        True if successful, False otherwise
    """
    xml_file = output_folder / f"{cr_id}.xml"
    
    # Skip if file already exist
    if xml_file.exists():
        print(f"  ✓ {cr_id} already exists (XML), skipping")
        return True
    
    success = True
    
    # Download XML
    if not xml_file.exists():
        try:
            xml_url = f"https://www.assemblee-nationale.fr/dyn/opendata/{cr_id}.xml"
            response = requests.get(xml_url, timeout=30)
            response.raise_for_status()
            
            with open(xml_file, "w", encoding="utf-8") as f:
                f.write(response.text)
            
            print(f"  ✓ Downloaded {cr_id}.xml")
            
        except Exception as e:
            print(f"  ✗ {cr_id}.xml error: {e}")
            success = False
    
    return success


def download_all_compte_rendus(vote_folder: str, output_folder: str, delay: float = 0.5):
    """
    Download all Compte Rendu files from vote folder seanceRef values.
    
    Args:
        vote_folder: Path to the vote folder
        output_folder: Path to save downloaded Compte Rendu files
        delay: Delay between requests in seconds
    """
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Collect all seance references
    seance_refs = collect_seance_refs(vote_folder)
    
    if not seance_refs:
        print("No Seance references found!")
        return
    
    # Get compte rendu references from seance data
    print(f"\nFetching Compte Rendu references from {len(seance_refs)} seances...")
    cr_refs = set()
    
    for i, seance_id in enumerate(sorted(seance_refs), 1):
        print(f"[{i}/{len(seance_refs)}] {seance_id}")
        cr_ref = get_compte_rendu_ref(seance_id)
        
        if cr_ref and cr_ref.startswith("CRSAN"):
            cr_refs.add(cr_ref)
            print(f"  → {cr_ref}")
        
        if i < len(seance_refs):
            time.sleep(delay)
    
    print(f"\nFound {len(cr_refs)} unique Compte Rendu references")
    
    if not cr_refs:
        print("No Compte Rendu references found!")
        return
    
    # Download each Compte Rendu
    print(f"\nDownloading {len(cr_refs)} Compte Rendu files...")
    print(f"Output folder: {output_path.absolute()}\n")
    
    successful = 0
    failed = 0
    
    for i, cr_id in enumerate(sorted(cr_refs), 1):
        print(f"[{i}/{len(cr_refs)}] {cr_id}")
        
        if download_compte_rendu(cr_id, output_path):
            successful += 1
        else:
            failed += 1
        
        if i < len(cr_refs):
            time.sleep(delay)
    
    print(f"\n=== Download Complete ===")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {len(cr_refs)}")


if __name__ == '__main__':
    vote_folder_15 = "data/vote/15"
    compte_rendu_folder_15 = "data/cr/15"

    vote_folder_16 = "data/vote/16"
    compte_rendu_folder_16 = "data/cr/16"
    
    vote_folder_17 = "data/vote/17"
    compte_rendu_folder_17 = "data/cr/17"

    download_all_compte_rendus(vote_folder_15, compte_rendu_folder_15, delay=0)
    download_all_compte_rendus(vote_folder_16, compte_rendu_folder_16, delay=0)
    download_all_compte_rendus(vote_folder_17, compte_rendu_folder_17, delay=0)