# Amorphous Silicon Models from ARTn-MTP Study

This folder contains the atomic structure models of amorphous silicon (a-Si) generated in the study:

**"Amorphous silicon structures generated using a moment tensor potential and the activation relaxation technique nouveau"**  
*Karim Zongo et al., Physical Review B 111, 214209 (2025)*  
DOI: [10.1103/w12r-gwzb](https://doi.org/10.1103/w12r-gwzb)

## Overview
The models were created by coupling the **Activation Relaxation Technique nouveau (ARTn)** with a **Moment Tensor Potential (MTP)**. These high-quality a-Si structures range in size from 216 to 4096 atoms and exhibit:
- Low coordination defects (≤3% in most cases).
- Excellent agreement with experimental structural data (RDF, bond angles, etc.).
- Mechanical properties (bulk modulus, elastic constants) consistent with literature values.

## Available Models
| Model Name   | Atoms | Density (g/cm³) | 4-fold Coord. (%) | Crystallinity (%) | Notes                          |
|--------------|-------|-----------------|-------------------|-------------------|--------------------------------|
| `216-R1`     | 216   | 2.20            | 99.07             | 0.00              | Low defects, no crystallinity  |
| `216-R2`     | 216   | 2.28            | 100.00            | 14.40             | **Fully 4-fold coordinated**   |
| `512-R1`     | 512   | 2.20            | 98.04             | 0.00              |                                |
| `512-R2`     | 512   | 2.28            | 98.04             | 0.00              |                                |
| `1000-R`     | 1000  | 2.28            | 97.00             | 13.30             |                                |
| `4096-R-MD`  | 4096  | 2.28            | 97.56             | 11.70             | Prerelaxed with MD             |

## Key Features
- **Structural Accuracy**: Models match experimental radial distribution functions (RDFs) and bond-angle distributions.
- **Defect Analysis**: Coordination defects (3-/5-fold) are minimized (<2% in most cases).
- **Mechanical Properties**: Bulk moduli (~75–80 GPa) align with DFT benchmarks.
- **Crystallinity**: Some models (e.g., `216-R2`) contain local crystalline environments, while others (e.g., `216-R1`) are purely amorphous.

