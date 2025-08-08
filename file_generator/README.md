# File Generator Module

A Python module containing utility functions for generating SLURM job scripts, LAMMPS input files, and managing computational workflows in high-performance computing environments. This module is designed to streamline the setup and execution of molecular dynamics simulations using LAMMPS with machine learning interatomic potentials (MLIP) and ARTn methods.

## Overview

The `file_generator.py` module provides five main functions:

1. **`generate_job_sh()`** - Creates SLURM job submission scripts
2. **`generate_lammps_input()`** - Generates LAMMPS input files for ARTn calculations
3. **`submit_slurm_job()`** - Submits jobs to SLURM scheduler
4. **`write_artn_in()`** - Creates ARTn parameter files
5. **`MTP_lammps_input()`** - Generates LAMMPS input for energy minimization with MTP

## Requirements

- Python 3.6+
- SLURM workload manager
- LAMMPS with MLIP support
- ARTn plugin for LAMMPS (optional, for transition state calculations)

## Functions Documentation

### 1. generate_job_sh()

Creates SLURM job submission scripts with customizable resource requirements.

```python
def generate_job_sh(time, num_task, num_core, mem_per_cpu, file_name="script_job.sh")
```

**Parameters:**
- `time` (str): Job duration in format "days-hours:minutes:seconds" (e.g., "0-00:15:00")
- `num_task` (int): Number of SLURM tasks (`--ntasks`)
- `num_core` (int): Number of cores for MPI execution
- `mem_per_cpu` (str): Memory per CPU (e.g., "4G")
- `file_name` (str): Output filename (default: "script_job.sh")

**Example:**
```python
generate_job_sh(
    time="0-01:30:00",
    num_task=4,
    num_core=40,
    mem_per_cpu="8G",
    file_name="my_job.sh"
)
```

**Generated SLURM script features:**
- Loads required modules (StdEnv/2020, intel, openmpi)
- Sets up LAMMPS-MLIP environment
- Executes LAMMPS with ARTn support
- Includes timing and error reporting

### 2. generate_lammps_input()

Generates LAMMPS input files for ARTn transition state calculations.

```python
def generate_lammps_input(input_data_file, output_file="lammps.in")
```

**Parameters:**
- `input_data_file` (str): Name of LAMMPS data file to read
- `output_file` (str): Output filename (default: "lammps.in")

**Example:**
```python
generate_lammps_input(
    input_data_file="./mol_vac.lmp",
    output_file="lammps.in"
)
```

**Generated LAMMPS input features:**
- Metal units and periodic boundary conditions
- MLIP pair style with custom potential
- ARTn plugin integration
- Energy minimization with FIRE algorithm
- Comprehensive output (energies, forces, coordinates)

### 3. submit_slurm_job()

Submits job scripts to SLURM scheduler with optional job dependencies.

```python
def submit_slurm_job(script_path, dependency=None)
```

**Parameters:**
- `script_path` (str): Path to the job script
- `dependency` (str, optional): Previous job ID for chaining jobs

**Returns:**
- `str`: Submitted job ID or `None` if error occurred

**Examples:**
```python
# Simple job submission
job_id = submit_slurm_job("script_job.sh")

# Chain jobs (run after previous completes)
next_job_id = submit_slurm_job("next_script.sh", dependency=job_id)
```

**Features:**
- Automatic script permission setting
- Job dependency support
- Error handling and reporting
- Job ID extraction and return

### 4. write_artn_in()

Creates ARTn parameter files for transition state calculations.

```python
def write_artn_in(push_ids=955, filename='artn.in')
```

**Parameters:**
- `push_ids` (int/str): Atom ID(s) to push during ARTn search (default: 955)
- `filename` (str): Output filename (default: 'artn.in')

**Examples:**
```python
# Default parameters
write_artn_in()

# Custom atom to push
write_artn_in(push_ids=1234)

# Multiple atoms
write_artn_in(push_ids="955, 956")

# Custom filename
write_artn_in(push_ids=100, filename="custom_artn.in")
```

**ARTn parameters included:**
- Engine units (LAMMPS/metal)
- Push parameters (step size, mode, distance threshold)
- Lanczos parameters for eigenvector calculations
- Convergence criteria and iteration limits

### 5. MTP_lammps_input()

Generates LAMMPS input files specifically for energy minimization and cohesive energy calculations.

```python
def MTP_lammps_input(data_file, output_name, input_filename="lammps.in")
```

**Parameters:**
- `data_file` (str): LAMMPS data file to read (e.g., "structure.lmp")
- `output_name` (str): Base name for output files (without extension)
- `input_filename` (str): Generated input filename (default: "lammps.in")

**Example:**
```python
MTP_lammps_input(
    data_file="crystal.lmp",
    output_name="optimized",
    input_filename="minimize.in"
)
```

**Generated input features:**
- Box relaxation with isotropic pressure control
- Conjugate gradient minimization
- Energy and structural analysis
- Comprehensive property output (energy, lattice parameters, etc.)

## Usage Examples

### Complete Workflow Example

```python
from file_generator import *

# 1. Generate SLURM job script
generate_job_sh(
    time="0-02:00:00",
    num_task=4,
    num_core=20,
    mem_per_cpu="4G",
    file_name="calculation.sh"
)

# 2. Generate LAMMPS input for ARTn calculation
generate_lammps_input(
    input_data_file="./system.lmp",
    output_file="artn_calculation.in"
)

# 3. Create ARTn parameters
write_artn_in(
    push_ids=500,
    filename="artn_params.in"
)

# 4. Submit job to cluster
job_id = submit_slurm_job("calculation.sh")
print(f"Job submitted with ID: {job_id}")
```

### Energy Minimization Workflow

```python
# Generate input for simple energy minimization
MTP_lammps_input(
    data_file="initial_structure.lmp",
    output_name="minimized_structure"
)

# Create corresponding job script
generate_job_sh(
    time="0-00:30:00",
    num_task=2,
    num_core=8,
    mem_per_cpu="2G",
    file_name="minimize_job.sh"
)

# Submit minimization job
job_id = submit_slurm_job("minimize_job.sh")
```

### Job Chaining Example

```python
# Submit multiple dependent jobs
job_ids = []

for i in range(5):
    script_name = f"job_{i}.sh"
    
    # Generate job script
    generate_job_sh(
        time="0-01:00:00",
        num_task=2,
        num_core=4,
        mem_per_cpu="4G",
        file_name=script_name
    )
    
    # Submit with dependency on previous job
    if job_ids:
        job_id = submit_slurm_job(script_name, dependency=job_ids[-1])
    else:
        job_id = submit_slurm_job(script_name)
    
    job_ids.append(job_id)
    print(f"Submitted job {i+1}: {job_id}")
```

## Configuration

### SLURM Account Configuration

The generated SLURM scripts use account `def-belandl1`. To modify for your cluster:

```python
# Edit the account line in generate_job_sh() function
#SBATCH --account=your-account-name
```

### Module Loading

Scripts automatically load:
- `StdEnv/2020`
- `intel/2020.1.217` 
- `openmpi/4.0.3`

Modify these in the `generate_job_sh()` function as needed for your cluster.

### LAMMPS Executable Paths

Default paths used:
- LAMMPS-MLIP: `/home/oupc/mlip_2/interface-lammps-mlip-2/lmp_mpi`
- ARTn plugin: `/home/oupc/artn-plugin/Files_LAMMPS/libartn-lmp.so`

Update these paths in the respective functions for your installation.

## File Outputs

### Generated Files Structure

Each function creates specific files:

```
calculation_directory/
├── script_job.sh          # SLURM job script
├── lammps.in             # LAMMPS input file
├── artn.in               # ARTn parameters
├── config.dmp            # LAMMPS trajectory dump
├── FinalS.data           # Final structure data
├── FinalS.restart        # LAMMPS restart file
└── out.run              # Simulation output log
```

## Error Handling

All functions include comprehensive error handling:

- **File validation**: Checks for existing files and permissions
- **Parameter validation**: Ensures correct input formats
- **Execution monitoring**: Reports success/failure status
- **Graceful failures**: Returns meaningful error messages

## Limitations

- Designed specifically for LAMMPS with MLIP and ARTn
- SLURM-specific job submission (not portable to other schedulers)
- Hardcoded paths require modification for different installations
- ARTn functionality requires specific LAMMPS plugin

## Contributing

To extend functionality:
1. Follow existing function naming conventions
2. Include comprehensive docstrings
3. Add error handling and validation
4. Provide usage examples
5. Update this documentation

