#!/usr/bin/env python3
"""
Script to verify vac_* folders and identify which ones don't have energies in out.run
"""

import os
import glob
import re

def check_energy_in_output(file_path):
    """
    Verifies if the out.run file contains energy information.

    Args:
        file_path (str): Path to the out.run file

    Returns:
        dict: Information about the energies found
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Search for different energy patterns
        energy_patterns = [
            r'Total energy \(eV\) = ([-\d.]+)',  # Final total energy
            r'Cohesive energy \(eV\) = ([-\d.]+)',  # Cohesive energy
            r'PotEng\s+([-\d.]+)',  # Potential energy in columns
            r'Step\s+PotEng',  # Table header with potential energy
        ]

        info = {
            'has_total_energy': False,
            'has_cohesive_energy': False,
            'has_potential_energy_data': False,
            'has_energy_header': False,
            'total_energy': None,
            'cohesive_energy': None,
            'file_exists': True,
            'file_size': os.path.getsize(file_path)
        }

        # Check total energy
        total_energy_match = re.search(energy_patterns[0], content)
        if total_energy_match:
            info['has_total_energy'] = True
            info['total_energy'] = float(total_energy_match.group(1))

        # Check cohesive energy
        cohesive_energy_match = re.search(energy_patterns[1], content)
        if cohesive_energy_match:
            info['has_cohesive_energy'] = True
            info['cohesive_energy'] = float(cohesive_energy_match.group(1))

        # Check potential energy data
        if re.search(energy_patterns[2], content):
            info['has_potential_energy_data'] = True

        # Check energy header
        if re.search(energy_patterns[3], content):
            info['has_energy_header'] = True

        return info

    except FileNotFoundError:
        return {
            'has_total_energy': False,
            'has_cohesive_energy': False,
            'has_potential_energy_data': False,
            'has_energy_header': False,
            'total_energy': None,
            'cohesive_energy': None,
            'file_exists': False,
            'file_size': 0
        }
    except Exception as e:
        return {
            'has_total_energy': False,
            'has_cohesive_energy': False,
            'has_potential_energy_data': False,
            'has_energy_header': False,
            'total_energy': None,
            'cohesive_energy': None,
            'file_exists': True,
            'file_size': 0,
            'error': str(e)
        }

def get_out_run_path(directory):
    """
    Gets the path to the out.run file in a directory.

    Args:
        directory (str): Directory to search

    Returns:
        str: Path to the out.run file or None if it doesn't exist
    """
    out_run_path = os.path.join(directory, 'out.run')
    return out_run_path if os.path.exists(out_run_path) else None

def main():
    """Main function of the script."""
    print("=== Energy Checker for out.run ===\n")

    # Search for all vac_* folders
    vac_folders = glob.glob('vac_*')

    if not vac_folders:
        print("No folders found with pattern 'vac_*'")
        return

    # Sort folders numerically if possible
    try:
        vac_folders.sort(key=lambda x: int(re.search(r'vac_(\d+)', x).group(1)))
    except:
        vac_folders.sort()

    print(f"Checking {len(vac_folders)} vac_* folders...\n")

    folders_without_energy = []
    missing_files = []

    for folder in vac_folders:
        if not os.path.isdir(folder):
            continue

        # Search for out.run file
        out_run_path = get_out_run_path(folder)

        if not out_run_path:
            missing_files.append(folder)
            continue

        # Check energies in the file
        energy_info = check_energy_in_output(out_run_path)

        # Determine if important energies are missing
        has_key_energies = (energy_info['has_total_energy'] or
                           energy_info['has_cohesive_energy'] or
                           energy_info['has_potential_energy_data'])

        if not has_key_energies:
            folders_without_energy.append((folder, energy_info))

    # Show results
    print("FOLDERS WITHOUT ENERGIES IN out.run:")
    print("="*50)

    if not folders_without_energy and not missing_files:
        print("✅ All folders have energies in their out.run files")
        return

    if missing_files:
        print(f"\n❌ Folders without out.run file ({len(missing_files)}):")
        for folder in missing_files:
            print(f"   {folder}")

    if folders_without_energy:
        print(f"\n❌ Folders with out.run but without energies ({len(folders_without_energy)}):")
        for folder, info in folders_without_energy:
            size_kb = info['file_size'] / 1024
            status_details = []

            if not info['file_exists']:
                status_details.append("file doesn't exist")
            elif info['file_size'] == 0:
                status_details.append("empty file")
            elif size_kb < 1:
                status_details.append(f"{info['file_size']} bytes")
            else:
                status_details.append(f"{size_kb:.1f} KB")

            if info.get('error'):
                status_details.append(f"error: {info['error']}")

            status = " - " + ", ".join(status_details) if status_details else ""
            print(f"   {folder}{status}")

    # Final summary
    total_problematic = len(folders_without_energy) + len(missing_files)
    total_folders = len(vac_folders)

    print(f"\nSUMMARY:")
    print(f"  Total vac_* folders: {total_folders}")
    print(f"  Folders with problems: {total_problematic}")
    print(f"  Folders OK: {total_folders - total_problematic}")

    if total_problematic > 0:
        print(f"\n⚠️  {total_problematic} folders require attention.")
    else:
        print(f"\n✅ All folders are OK.")

if __name__ == "__main__":
    main()
