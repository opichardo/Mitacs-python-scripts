def generate_job_sh(time, num_task, num_core, mem_per_cpu, file_name="script_job.sh"):
    """
    Generates a file .sh for SLURM with specific parameters.
    
    Args:
        time (str): Time for the job in this format "days-hours:minutes:seconds" (ex. "0-00:15:00")
        num_task (int): Number of tasks (--ntasks)
        num_core (int): Number of cores for mpirun (used in the command mpirun -np)
        mem_per_cpu (str): Memory per CPU (ej. "4G")
        file_name (str): Name of the ouput file (optional)
    """
    content = f"""#!/bin/sh
#SBATCH --account=def-belandl1
#SBATCH --ntasks={num_task}
#SBATCH --mem-per-cpu={mem_per_cpu}
#SBATCH --time={time}

# Load the modules:
module load StdEnv/2020 intel/2020.1.217 openmpi/4.0.3

export LD_LIBRARY_PATH=/home/oupc/mlip_2/mylammps/src:$LD_LIBRARY_PATH

echo "Starting run at: `date`"


#srun ${{lmp_exec}} -in ${{lmp_input}} > ${{lmp_output}}

#mpirun -np {num_core} ${{lmp_exec}} -p 10x4 -in ${{lmp_input}} > ${{lmp_output}}

srun /home/oupc/mlip_2/interface-lammps-mlip-2/lmp_mpi -in lammps.in > out.run


echo "Program finished with exit code $? at: `date`"
"""

    with open(file_name, 'w') as f:
        f.write(content)
    
    print(f"File {file_name} succesfully generated.")

# Example:
# generate_job_sh(time="0-01:30:00", num_task=4, num_core=40, mem_per_cpu="8G", file_name="mi_job.sh")

def generate_lammps_input(input_data_file, output_file="lammps.in"):
    """
    Genera un archivo de entrada para LAMMPS basado en el script proporcionado.
    
    Parámetros:
        input_data_file (str): Nombre del archivo de datos de entrada (para 'read_data').
        output_file (str): Nombre del archivo de salida (por defecto: 'lammps.in').
    """
    lammps_script = f"""# ---------- Initialize Simulation --------------------- 
clear 
units       metal 
dimension   3 
boundary    p p p 
atom_style  atomic 
atom_modify sort 0 1


# ---------- Create Atoms --------------------- 
read_data   {input_data_file}


# ---------- Define Interatomic Potential --------------------- 
pair_style  mlip mlip.ini
pair_coeff  * *

mass        1  28.0855

neighbor     2.0 bin 
neigh_modify delay 10 check yes 

# balance atoms per cpu
comm_style tiled
balance 1.1 rcb
 
# ---------- Define Settings --------------------- 
compute eng all pe/atom 
compute eatoms all reduce sum c_eng 


# ----------- OUTPUT
dump 10  all custom 1 config.dmp id type x y z fx fy fz

thermo 10 
thermo_style custom step pe fnorm lx ly lz press pxx pyy pzz c_eatoms 


# ----------- ARTn
plugin   load   /home/oupc/artn-plugin/Files_LAMMPS/libartn-lmp.so
plugin   list

fix             10 all artn alpha0 0.2 dmax 5.0
timestep 0.001


# ---------- Run Minimization --------------------- 
reset_timestep 0 

min_style fire 

minimize 1e-4 1e-5 2000 10000 


variable natoms equal "count(all)" 
variable teng equal "c_eatoms"
variable length equal "lx"
variable ecoh equal "v_teng/v_natoms"

print "Total energy (eV) = ${{teng}};"
print "Number of atoms = ${{natoms}};"
print "Lattice constant (Angstoms) = ${{length}};"
print "Cohesive energy (eV) = ${{ecoh}};"

write_data      FinalS.data             
write_restart   FinalS.restart          

print "All done!"
"""

    with open(output_file, 'w') as f:
        f.write(lammps_script)

    print(f"Archivo de entrada de LAMMPS generado: {output_file}")


# Example:
#generate_lammps_input(input_data_file="conf.sw", output_file="lammps.in")

import subprocess
import os

def submit_slurm_job(script_path, dependency=None):
    """
    Submits a .sh script to SLURM using sbatch.

    Args:
        script_path (str): Path to the .sh script
        dependency (str, optional): Previous job ID for dependency (e.g., "123456")

    Returns:
        str: Submitted job ID or None if error occurred
    """
    if not os.path.isfile(script_path):
        print(f"Error: File {script_path} does not exist")
        return None

    try:
        # Make script executable if it isn't already
        os.chmod(script_path, 0o755)

        # Build sbatch command
        command = ["sbatch"]

        # Add dependency if specified
        if dependency:
            command.extend(["--dependency=afterok", dependency])

        command.append(script_path)

        # Execute command
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Extract job ID from output (format: "Submitted batch job 123456")
        job_id = result.stdout.strip().split()[-1]
        print(f"Job submitted successfully. ID: {job_id}")
        return job_id

    except subprocess.CalledProcessError as e:
        print(f"Job submission error: {e.stderr}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

# Example usage:
# 1. First generate the script
# generate_slurm_script(runtime="0-01:00:00", num_tasks=4, num_cores=40,
#                      mem_per_cpu="8G", output_file="my_job.sh")
#
# 2. Then submit it
# job_id = submit_slurm_job("my_job.sh")
#
# 3. To chain jobs (run after previous one completes)
# next_job_id = submit_slurm_job("another_job.sh", dependency=job_id)

def write_artn_in(push_ids=955, filename='artn.in'):
    """
    Writes ARTn parameters to a specified file (default: artn.in)
    with customizable push_ids parameter.

    Args:
        push_ids (int or str): Atom ID(s) to push (default: 955)
        filename (str): Output filename (default: 'artn.in')
    """
    content = f"""&ARTN_PARAMETERS
  !! Units definition::(eV,Ang,ps)
  engine_units     ='lammps/metal'
  verbose          = 1
  zseed            = 42

  !! ARTn mode
  ninit            = 0
  lpush_final      = .true.
  nsmooth          = 3
  nnewchance       = 30
  forc_thr         = 0.01
  nperp_limitation = 4, 10, 15, 20, 25, 30, 35, -1
  restart_freq     = 0

  !! parameters for the push
  push_step_size   = 0.40
  push_mode        = 'rad'
  push_dist_thr    = 3.5
  push_ids         = {push_ids}

  !! lanczos parameters
  lanczos_disp     = 1.0D-2
  lanczos_min_size = 3
  lanczos_max_size = 50

  !! eigenpush parms
  eigen_step_size  = 0.1
  push_over        = 6.0
/"""

    with open(filename, 'w') as f:
        f.write(content)

# Example usage:
# write_artn_in()  # Uses default push_ids=955
# write_artn_in(push_ids=1234)  # Custom push_ids
# write_artn_in(push_ids="955, 956")  # Multiple atoms

def MTP_lammps_input(data_file, output_name, input_filename="lammps.in"):
    """
    Generate a LAMMPS input file for energy minimization and cohesive energy calculation.

    Parameters:
    -----------
    data_file : str
        Name of the LAMMPS data file to read (e.g., "1000.lmp")
    output_name : str
        Base name for output files (without extension, e.g., "FinalS")
    input_filename : str, optional
        Name of the generated LAMMPS input file (default: "lammps.in")

    Returns:
    --------
    None
        Creates a LAMMPS input file with the specified parameters
    """

    # LAMMPS input file content template
    lammps_content = f"""clear
units            metal
dimension        3
boundary         p p p
# read data
atom_style       atomic
read_data        {data_file}
mass             1 28.0855
pair_style  mlip mlip.ini
pair_coeff  **
timestep         0.001
neighbor 2.0 bin
neigh_modify every 1 delay 5 check yes
# ---------- Define Settings ---------------------
compute eng all pe/atom
compute eatoms all reduce sum c_eng
thermo                         10
thermo_style                   custom step pe  press pxx pyy pzz density
fix                            1 all box/relax iso 0.0 vmax 0.001
min_style                      cg
minimize                       1e-25 1e-25 5000 10000
unfix                          1
variable natoms equal "count(all)"
variable teng equal "c_eatoms"
variable length equal "lx"
variable ecoh equal "v_teng/v_natoms"
print "Total energy (eV) = ${{teng}};"
print "Number of atoms = ${{natoms}};"
print "Lattice constant (Angstoms) = ${{length}};"
print "Cohesive energy (eV) = ${{ecoh}};"
write_data                   {output_name}.data
write_restart                {output_name}.restart
print "All done!"
"""

    # Write the LAMMPS input file
    try:
        with open(input_filename, 'w') as file:
            file.write(lammps_content)
        print(f"LAMMPS input file '{input_filename}' has been created successfully!")
        print(f"Data file: {data_file}")
        print(f"Output files: {output_name}.data and {output_name}.restart")

    except IOError as e:
        print(f"Error writing file: {e}")


# Example usage
    # Generate LAMMPS input file with custom parameters
    # MTP_lammps_input("1000.lmp", "FinalS")
