import sys
import re
import os

def parse_lammps_data(filename):
    """
    Parse LAMMPS data file and extract atomic information.
    
    Parameters:
    -----------
    filename : str
        Path to the LAMMPS data file
    
    Returns:
    --------
    dict
        Dictionary containing atoms data, box dimensions, and masses
    """
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Initialize variables
    atoms = []
    masses = {}
    box_bounds = {}
    n_atoms = 0
    n_atom_types = 0
    
    # Parse header information
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Get number of atoms and atom types
        if 'atoms' in line and not line.startswith('#'):
            n_atoms = int(line.split()[0])
        elif 'atom types' in line and not line.startswith('#'):
            n_atom_types = int(line.split()[0])
        
        # Get box bounds
        elif 'xlo xhi' in line:
            bounds = line.split()
            box_bounds['x'] = [float(bounds[0]), float(bounds[1])]
        elif 'ylo yhi' in line:
            bounds = line.split()
            box_bounds['y'] = [float(bounds[0]), float(bounds[1])]
        elif 'zlo zhi' in line:
            bounds = line.split()
            box_bounds['z'] = [float(bounds[0]), float(bounds[1])]
        elif 'xy xz yz' in line:
            # For triclinic boxes
            tilt = line.split()
            box_bounds['tilt'] = [float(tilt[0]), float(tilt[1]), float(tilt[2])]
    
    # Find and parse Masses section
    masses_start = None
    for i, line in enumerate(lines):
        if line.strip().lower() == 'masses':
            masses_start = i + 1
            break
    
    if masses_start:
        for i in range(masses_start, len(lines)):
            line = lines[i].strip()
            if not line or line.startswith('#'):
                continue
            if line.lower().startswith('atoms') or line.lower().startswith('velocities') or line.lower().startswith('bonds'):
                break
            
            parts = line.split()
            if len(parts) >= 2:
                atom_type = int(parts[0])
                mass = float(parts[1])
                masses[atom_type] = mass
    
    # Find and parse Atoms section
    atoms_start = None
    for i, line in enumerate(lines):
        if 'atoms' in line.lower() and ('#' in line.lower() or 'atomic' in line.lower()):
            atoms_start = i + 1
            break
    
    if atoms_start:
        for i in range(atoms_start, len(lines)):
            line = lines[i].strip()
            if not line or line.startswith('#'):
                continue
            if line.lower().startswith('velocities') or line.lower().startswith('bonds'):
                break
            
            parts = line.split()
            if len(parts) >= 5:  # atom_id, atom_type, x, y, z (minimum)
                atom_id = int(parts[0])
                atom_type = int(parts[1])
                x = float(parts[2])
                y = float(parts[3])
                z = float(parts[4])
                
                atoms.append({
                    'id': atom_id,
                    'type': atom_type,
                    'x': x,
                    'y': y,
                    'z': z
                })
    
    return {
        'atoms': atoms,
        'masses': masses,
        'box_bounds': box_bounds,
        'n_atoms': n_atoms,
        'n_atom_types': n_atom_types
    }

def mass_to_element(mass):
    """
    Convert atomic mass to element symbol (approximate matching).
    
    Parameters:
    -----------
    mass : float
        Atomic mass in amu
    
    Returns:
    --------
    str
        Element symbol
    """
    
    # Common elements and their approximate atomic masses
    mass_to_element_map = {
        1.008: 'H',
        4.003: 'He',
        6.941: 'Li',
        9.012: 'Be',
        10.811: 'B',
        12.011: 'C',
        14.007: 'N',
        15.999: 'O',
        18.998: 'F',
        20.180: 'Ne',
        22.990: 'Na',
        24.305: 'Mg',
        26.982: 'Al',
        28.086: 'Si',
        30.974: 'P',
        32.065: 'S',
        35.453: 'Cl',
        39.948: 'Ar',
        39.098: 'K',
        40.078: 'Ca',
        44.956: 'Sc',
        47.867: 'Ti',
        50.942: 'V',
        51.996: 'Cr',
        54.938: 'Mn',
        55.845: 'Fe',
        58.933: 'Co',
        58.693: 'Ni',
        63.546: 'Cu',
        65.380: 'Zn',
        69.723: 'Ga',
        72.640: 'Ge',
        74.922: 'As',
        78.960: 'Se',
        79.904: 'Br',
        83.798: 'Kr'
    }
    
    # Find closest mass match
    closest_mass = min(mass_to_element_map.keys(), key=lambda x: abs(x - mass))
    
    # If the difference is too large, return generic symbol
    if abs(closest_mass - mass) > 2.0:
        return f'X{int(mass)}'
    
    return mass_to_element_map[closest_mass]

def convert_data_to_xyz(data_filename, xyz_filename=None, include_lattice=False):
    """
    Convert LAMMPS data file to XYZ format.
    
    Parameters:
    -----------
    data_filename : str
        Path to the LAMMPS data file
    xyz_filename : str, optional
        Output XYZ filename. If None, uses input filename with .xyz extension
    include_lattice : bool, optional
        Whether to include lattice information in XYZ comment line
    
    Returns:
    --------
    str
        Path to the created XYZ file
    """
    
    # Parse LAMMPS data file
    data = parse_lammps_data(data_filename)
    
    # Generate output filename if not provided
    if xyz_filename is None:
        base_name = os.path.splitext(data_filename)[0]
        xyz_filename = f"{base_name}.xyz"
    
    # Sort atoms by ID to maintain order
    atoms = sorted(data['atoms'], key=lambda x: x['id'])
    
    # Create element mapping from masses
    type_to_element = {}
    for atom_type, mass in data['masses'].items():
        type_to_element[atom_type] = mass_to_element(mass)
    
    # Write XYZ file
    with open(xyz_filename, 'w') as f:
        # Write number of atoms
        f.write(f"{len(atoms)}\n")
        
        # Write comment line
        comment = f"Converted from {os.path.basename(data_filename)}"
        
        # Add lattice information if requested and available
        if include_lattice and 'x' in data['box_bounds']:
            box = data['box_bounds']
            if 'tilt' in box:
                # Triclinic box
                lx = box['x'][1] - box['x'][0]
                ly = box['y'][1] - box['y'][0]
                lz = box['z'][1] - box['z'][0]
                xy, xz, yz = box['tilt']
                comment += f' Lattice="{lx} 0.0 0.0 {xy} {ly} 0.0 {xz} {yz} {lz}"'
            else:
                # Orthogonal box
                lx = box['x'][1] - box['x'][0]
                ly = box['y'][1] - box['y'][0]
                lz = box['z'][1] - box['z'][0]
                comment += f' Lattice="{lx} 0.0 0.0 0.0 {ly} 0.0 0.0 0.0 {lz}"'
        
        f.write(f"{comment}\n")
        
        # Write atomic coordinates
        for atom in atoms:
            element = type_to_element.get(atom['type'], f"X{atom['type']}")
            f.write(f"{element:2s} {atom['x']:12.6f} {atom['y']:12.6f} {atom['z']:12.6f}\n")
    
    return xyz_filename

def main():
    """
    Main function for command line usage.
    """
    
    if len(sys.argv) < 2:
        print("Usage: python data_to_xyz.py input.data [output.xyz] [--lattice]")
        print("  input.data  : LAMMPS data file to convert")
        print("  output.xyz  : Output XYZ file (optional, defaults to input.xyz)")
        print("  --lattice   : Include lattice information in XYZ comment line")
        sys.exit(1)
    
    data_file = sys.argv[1]
    
    # Check if input file exists
    if not os.path.exists(data_file):
        print(f"Error: File '{data_file}' not found!")
        sys.exit(1)
    
    # Parse command line arguments
    xyz_file = None
    include_lattice = False
    
    for i in range(2, len(sys.argv)):
        if sys.argv[i] == '--lattice':
            include_lattice = True
        elif not xyz_file:
            xyz_file = sys.argv[i]
    
    try:
        # Convert file
        output_file = convert_data_to_xyz(data_file, xyz_file, include_lattice)
        print(f"Successfully converted '{data_file}' to '{output_file}'")
        
        # Print some statistics
        data = parse_lammps_data(data_file)
        print(f"Number of atoms: {len(data['atoms'])}")
        print(f"Number of atom types: {len(data['masses'])}")
        
        if data['masses']:
            print("Atom types and elements:")
            for atom_type, mass in data['masses'].items():
                element = mass_to_element(mass)
                print(f"  Type {atom_type}: {element} (mass = {mass:.3f})")
    
    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
