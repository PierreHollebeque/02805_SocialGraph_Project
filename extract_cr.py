import json
from py_compile import main
import requests
from pathlib import Path
import time
from typing import Set, List

def collect_compte_rendu_refs(reunion_folder: str) -> Set[str]:
    """
    Collect all unique compteRenduRef values from reunion files.
    
    Args:
        reunion_folder: Path to the reunion folder
        
    Returns:
        Set of unique compteRenduRef values (excluding None/null)
    """
    print("Collecting compteRenduRef from reunion files...")
    reunion_folder_path = Path(reunion_folder)
    compte_rendu_refs = set()
    
    for reunion_file in reunion_folder_path.glob("*.json"):
        try:
            data = json.loads(reunion_file.read_text(encoding="utf-8"))
            reunion = data.get("reunion", {})
            compte_rendu_ref = reunion.get("compteRenduRef")

            if compte_rendu_ref and compte_rendu_ref.startswith("CRSAN"):  # Only add non-null values and CRSAN beginning
                compte_rendu_refs.add(compte_rendu_ref)
                
        except Exception as e:
            print(f"Error processing {reunion_file.name}: {e}")
            continue
    
    print(f"Found {len(compte_rendu_refs)} unique Compte Rendu references")
    return compte_rendu_refs


def download_compte_rendu(cr_id: str, output_folder: Path) -> bool:
    """
    Download a single Compte Rendu from the API and save it as JSON.
    
    Args:
        cr_id: The Compte Rendu ID
        output_folder: Folder to save the downloaded file
        
    Returns:
        True if successful, False otherwise
    """
    
    url = f"https://www.assemblee-nationale.fr/dyn/opendata/{cr_id}.json"
    output_file = output_folder / f"{cr_id}.json"
    
    # Skip if file already exists
    if output_file.exists():
        print(f"  ✓ {cr_id} already exists, skipping")
        return True
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Parse JSON to validate it
        data = response.json()
        
        # Save to file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Downloaded {cr_id}")
        return True
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"  ✗ {cr_id} not found (404)")
        else:
            print(f"  ✗ {cr_id} HTTP error: {e}")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"  ✗ {cr_id} request error: {e}")
        return False
        
    except json.JSONDecodeError as e:
        print(f"  ✗ {cr_id} invalid JSON: {e}")
        return False
        
    except Exception as e:
        print(f"  ✗ {cr_id} unexpected error: {e}")
        return False


def download_all_compte_rendus(reunion_folder: str, output_folder: str, delay: float = 0.5):
    """
    Download all Compte Rendu files mentioned in reunion folder.
    
    Args:
        reunion_folder: Path to the reunion folder
        output_folder: Path to save downloaded Compte Rendu files
        delay: Delay between requests in seconds (to be respectful to the server)
    """
    # Create output folder if it doesn't exist
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Collect all Compte Rendu references
    cr_refs = collect_compte_rendu_refs(reunion_folder)
    
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
        
        # Be respectful to the server - add delay between requests
        if i < len(cr_refs):  # Don't delay after last request
            time.sleep(delay)
    
    print(f"\n=== Download Complete ===")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {len(cr_refs)}")


if __name__ == '__main__':
    reunion_folder_16 = "data/reunion/16"
    compte_rendu_folder_16 = "data/cr/16"
    
    reunion_folder_17 = "data/reunion/17"
    compte_rendu_folder_17 = "data/cr/17"

    download_all_compte_rendus(reunion_folder_16, compte_rendu_folder_16, delay=0.1)
    download_all_compte_rendus(reunion_folder_17, compte_rendu_folder_17, delay=0.1)