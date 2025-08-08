# Formation Energy Calculator for Point Defects in Silicon

This Python script calculates vacancy and self-interstitial formation energies in silicon structures, following the methodology described in Cleveland & Demkowicz (Phys. Rev. Materials 6, 013611, 2022).

## Background

Formation energy is a fundamental thermodynamic property that determines whether point defects (vacancies and self-interstitials) will form spontaneously in a material. The formation energy depends critically on the choice of reference energy, which represents the reservoir from which atoms are removed or added.

### Theoretical Foundation

**Vacancy Formation Energy:**
```
E_f^v = (E_{N-1} + E_r) - E_N
```

**Self-Interstitial Formation Energy:**
```
E_f^i = (E_{N+1} - E_r) - E_N
```

Where:
- `E_N` = total energy of the perfect system with N atoms
- `E_{N-1}` = total energy after removing one atom (vacancy)
- `E_{N+1}` = total energy after adding one atom (self-interstitial)
- `E_r` = reference energy per atom (reservoir energy)

## Script Functionality

This script processes computational results from atomistic simulations and calculates formation energies using two different reservoir choices:

### 1. Crystal Reservoir (E_r = E_coh^{c-Si})
Uses the cohesive energy of perfect crystalline silicon as the reference. This represents the scenario where atoms are exchanged with a perfect crystal reservoir.

### 2. Amorphous Reservoir (E_r = E_coh^{a-Si})
Uses the cohesive energy of the amorphous structure itself as the reference. This represents a more realistic scenario for defect formation within the amorphous material.

## Input/Output

### Input Files Required:
- `out.run` files in subdirectories containing:
  - Total energy (eV) values
  - Cohesive energy (eV) values
- `../out.run` - parent directory energy (E_N)
- `../crystal/out.run` - crystalline reference cohesive energy

### Output:
- `e_summary.txt` - Tab-separated file containing:
  - Folder name
  - Total energy (eV)
  - Cohesive energy (eV)
  - ΔE = (E_{n-1} + ΔE_c) - E_n (eV)
  - Formation energy (eV)

## Physical Interpretation

### Formation Energy Signs:
- **Positive formation energy (E_f > 0)**: Defect formation is energetically unfavorable
- **Negative formation energy (E_f < 0)**: Defect formation is energetically favorable, indicating the structure is not at a local enthalpy minimum

### Research Significance:
As demonstrated by Cleveland & Demkowicz, amorphous silicon consistently exhibits negative vacancy and self-interstitial formation energies, regardless of the reservoir choice. This indicates that:

1. Amorphous silicon is not at or near a local enthalpy minimum
2. The material can undergo spontaneous, exothermic evolution to lower enthalpy states
3. Successive defect insertion drives the structure further from equilibrium

## Usage

### 1. Energy Extraction and Calculation
```bash
python summary.py
```

The script will:
1. Search for `out.run` files in all subdirectories
2. Extract total and cohesive energies using regex patterns
3. Calculate formation energies using both reservoir choices
4. Generate a summary report (`e_summary.txt`)

### 2. Statistical Analysis and Visualization
```bash
python ef_histogram.py
```

This companion script provides statistical analysis and visualization of the formation energy results:

**Features:**
- **Data parsing**: Reads the `e_summary.txt` output from `summary.py`
- **Statistical summary**: Reports ranges and counts for both energy types
- **Comparative visualization**: Creates normalized histograms comparing:
  - ΔE with amorphous Si reservoir (ΔE_r = ΔE_coh^{a-Si}) - Red line with circles
  - Formation Energy with crystalline Si reservoir (ΔE_r = ΔE_coh^{c-Si}) - Black line with squares

**Output:**
- Console statistics showing energy ranges and data counts
- Matplotlib figure comparing formation energy distributions for both reservoir choices
- Normalized density plots allowing direct comparison of distribution shapes

## Key Features

- **Robust parsing**: Uses regular expressions to extract energies from simulation output files
- **Dual reservoir calculation**: Computes formation energies for both crystalline and amorphous reservoirs
- **Error handling**: Gracefully handles missing files and parsing errors
- **Comprehensive output**: Provides detailed energy analysis and summary statistics

## Reference

This implementation is based on the methodology described in:

> Cleveland, M. W. & Demkowicz, M. J. "Persistence of negative vacancy and self-interstitial formation energies in atomistic models of amorphous silicon." *Physical Review Materials* **6**, 013611 (2022).

The choice of reference energy significantly impacts the interpretation of defect thermodynamics in amorphous materials, making this dual-reservoir approach essential for comprehensive analysis.
