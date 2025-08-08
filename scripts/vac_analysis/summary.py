import os
import re

# Regular expression patterns to extract energies
total_energy_pattern = r"Total energy \(eV\)\s*=\s*(-?\d+\.\d+);"
cohesive_energy_pattern = r"Cohesive energy \(eV\)\s*=\s*(-?\d+\.\d+);"

# Output file to save results
output_file = "e_summary.txt"

# Get parent directory energy (En)
parent_energy = None
parent_out_file = os.path.join('..', 'out.run') if os.path.exists(os.path.join('..', 'out.run')) else 'out.run'

if os.path.exists(parent_out_file):
    try:
        with open(parent_out_file, 'r') as f:
            content = f.read()
            parent_match = re.search(total_energy_pattern, content)
            if parent_match:
                parent_energy = float(parent_match.group(1))
                print(f"Parent directory energy (En) found: {parent_energy} eV")
            else:
                print("Warning: Could not find total energy in parent directory out.run")
    except Exception as e:
        print(f"Error processing parent directory out.run: {str(e)}")
else:
    print("Warning: No out.run found in parent directory")

# Get crystal directory cohesive energy for formation energy calculation
crystal_cohesive_energy = None
crystal_out_file = os.path.join('..', 'crystal', 'out.run')

if os.path.exists(crystal_out_file):
    try:
        with open(crystal_out_file, 'r') as f:
            content = f.read()
            crystal_cohesive_match = re.search(cohesive_energy_pattern, content)
            if crystal_cohesive_match:
                crystal_cohesive_energy = float(crystal_cohesive_match.group(1))
                print(f"Crystal cohesive energy found: {crystal_cohesive_energy} eV")
            else:
                print("Warning: Could not find cohesive energy in crystal/out.run")
    except Exception as e:
        print(f"Error processing crystal/out.run: {str(e)}")
else:
    print("Warning: No out.run found in crystal directory")

# Open output file in write mode
with open(output_file, 'w') as out_f:
    # Write header
    out_f.write("Folder\tTotal Energy (eV)\tCohesive Energy (eV)\tΔE = (E_{n-1} + ΔE_c) - E_n (eV)\tFormation Energy (eV)\n")
    
    # Process all folders in current directory
    for folder in sorted(os.listdir('.')):
        if os.path.isdir(folder):
            out_file = os.path.join(folder, 'out.run')
            
            # Check if out.run exists
            if os.path.exists(out_file):
                try:
                    with open(out_file, 'r') as f:
                        content = f.read()
                        
                        # Find energies
                        total_match = re.search(total_energy_pattern, content)
                        cohesive_match = re.search(cohesive_energy_pattern, content)
                        
                        if total_match and cohesive_match:
                            total_energy = float(total_match.group(1))
                            cohesive_energy = float(cohesive_match.group(1))
                            
                            # Calculate ΔE if parent energy is available
                            delta_e = None
                            if parent_energy is not None:
                                delta_e = (total_energy + cohesive_energy) - parent_energy
                            
                            # Calculate formation energy using the same formula as ΔE
                            # but with crystal cohesive energy instead of defect cohesive energy
                            # Formation Energy = (E_{N-1} + ΔE_r_crystal) - E_N
                            # where E_{N-1} is total energy of defective system
                            # E_N is total energy of perfect system (parent)
                            # ΔE_r_crystal is cohesive energy of crystal
                            formation_energy = None
                            if crystal_cohesive_energy is not None and parent_energy is not None:
                                formation_energy = (total_energy + crystal_cohesive_energy) - parent_energy
                            
                            # Write results
                            delta_e_str = f"{delta_e}" if delta_e is not None else "N/A"
                            formation_e_str = f"{formation_energy}" if formation_energy is not None else "N/A"
                            
                            out_f.write(f"{folder}\t{total_energy}\t{cohesive_energy}\t{delta_e_str}\t{formation_e_str}\n")
                            
                            print(f"Folder {folder}: Energies extracted")
                            if delta_e is not None:
                                print(f"  ΔE = {delta_e} eV")
                            if formation_energy is not None:
                                print(f"  Formation Energy = {formation_energy} eV")
                        else:
                            print(f"Warning: No energies found in {folder}")
                except Exception as e:
                    print(f"Error processing {folder}: {str(e)}")
            else:
                print(f"Warning: No out.run found in {folder}")

print(f"\nProcess completed. Results saved in {output_file}")
print(f"Summary:")
print(f"- Parent energy: {parent_energy} eV" if parent_energy else "- Parent energy: Not found")
print(f"- Crystal cohesive energy: {crystal_cohesive_energy} eV" if crystal_cohesive_energy else "- Crystal cohesive energy: Not found")
