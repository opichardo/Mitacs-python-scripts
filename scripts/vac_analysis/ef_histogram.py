import numpy as np
import matplotlib.pyplot as plt

# Leer el archivo txt
file_path = "e_summary.txt"  # Cambia esto por la ruta de tu archivo

# Extraer ΔE (cuarta columna) y Formation Energy (quinta columna)
delta_E = []
formation_energy = []

with open(file_path, "r") as f:
    lines = f.readlines()
    for line in lines[1:]:  # Saltar la línea de encabezado
        line = line.strip()  # Eliminar espacios en blanco al inicio y final
        if line:  # Asegurar que la línea no esté vacía
            parts = line.split('\t')  # Usar tab como separador
            if len(parts) >= 5:  # Asegurar que hay al menos 5 columnas
                try:
                    # ΔE (cuarta columna, índice 3)
                    if parts[3] != "N/A":
                        delta_E.append(float(parts[3]))
                    
                    # Formation Energy (quinta columna, índice 4)
                    if parts[4] != "N/A":
                        formation_energy.append(float(parts[4]))
                except ValueError as e:
                    print(f"Error al convertir a float en línea: {line}")
                    continue

delta_E = np.array(delta_E)
formation_energy = np.array(formation_energy)

print(f"Se leyeron {len(delta_E)} valores de ΔE")
print(f"Rango de ΔE: {delta_E.min():.3f} a {delta_E.max():.3f} eV")
print(f"Se leyeron {len(formation_energy)} valores de Formation Energy")
print(f"Rango de Formation Energy: {formation_energy.min():.3f} a {formation_energy.max():.3f} eV")

# Configurar bins para que ambos histogramas usen el mismo rango
all_energies = np.concatenate([delta_E, formation_energy])
energy_min = all_energies.min()
energy_max = all_energies.max()
num_bins = 20
bins = np.linspace(energy_min, energy_max, num_bins + 1)

# Calcular histogramas
counts_delta, _ = np.histogram(delta_E, bins=bins, density=False)
counts_formation, _ = np.histogram(formation_energy, bins=bins, density=False)

# Normalizar
counts_delta = counts_delta / counts_delta.sum()
counts_formation = counts_formation / counts_formation.sum()

# Centros de los bins
bin_centers = 0.5 * (bins[1:] + bins[:-1])

# Graficar
plt.figure(figsize=(10, 6))
plt.plot(bin_centers, counts_delta, marker='o', linestyle='-', color="red", 
         linewidth=1.5, markersize=4, label=r'$\Delta E_r$ = $\Delta E_{coh}^{a-Si}$')
plt.plot(bin_centers, counts_formation, marker='s', linestyle='-', color="black", 
         linewidth=1.5, markersize=4, label=r'$\Delta E_r$ = $\Delta E_{coh}^{c-Si}$')

# Etiquetas y estilo
plt.xlabel('Energy (eV)', fontsize=12)
plt.ylabel('Normalized density', fontsize=12)
plt.title('Comparison of Vacancy Formation Energies', fontsize=14)
plt.axvline(x=3, color="gray", linestyle="--", linewidth=1, alpha=0.7)
plt.ylim(0, None)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
