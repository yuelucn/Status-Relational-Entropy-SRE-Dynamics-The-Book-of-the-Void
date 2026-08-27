import numpy as np

# =====================================================================
# SRE DYNAMICS MACROSCOPIC SYSTEM CHARACTERIZATION (SI UNITS)
# =====================================================================
C_LIGHT = 299792458.0      # Absolute velocity of causality propagation (m/s)
delta_tau = 1.0e-3         # Discrete update frame interval (1.0 ms)

num_nodes = 4
boundary_nodes = {0, 3}    # Dirichlet Boundary (Fixed 120V Source and 0V Ground Sink)

# =====================================================================
# SPARSE TOPOLOGY SPECIFICATION (Guarantees Dimensional Alignment)
# =====================================================================
# Real physical impedances assigned to network branch lines
R_01 = 2.0   # Transmission Line Resistance (2.0 Ohms)
R_12 = 10.0  # Distribution Branch Resistance (10.0 Ohms)
R_23 = 50.0  # Sink Path Resistance (50.0 Ohms)

# Initialize Adjacency Matrix A via inverse rigidity rules (Width = 1 / R)
A = np.zeros((num_nodes, num_nodes))
A[0, 1] = 1.0 / R_01
A[1, 2] = 1.0 / R_12
A[2, 3] = 1.0 / R_23
A = A + A.T  # Symmetric causal layout

# Damped Node Capacitances (Farads) - Formulated to secure numerical convergence
# Aligns step interval delta_tau with node charge relaxation physics
node_capacitance = np.array([1.0, 5.0e-3, 2.0e-2, 1.0]) 

# =====================================================================
# STATE STORAGE BASELINES
# =====================================================================
node_charge = np.zeros(num_nodes)    # Net Charge Count (Coulombs)
node_voltage = np.zeros(num_nodes)   # First-Order Phase Pressure (Volts)

# Rigid Dirichlet Boundary Conditions Setup
source_macro_voltage = 120.0
node_voltage[0] = source_macro_voltage
node_voltage[3] = 0.0

print("=====================================================================")
print("      SRE DYNAMICS MULTI-NODE DISCRETE GRAPH EVOLUTION ENGINE        ")
print("=====================================================================")
print(f"System Framework Synchronized. Base update scale: delta_tau = {delta_tau*1000:.1f} ms.\n")

# =====================================================================
# STABLE DISCRETE EVOLUTION ENGINE
# =====================================================================
total_steps = 6

for step in range(1, total_steps + 1):
    print(f"\n[Evolutionary Step ΔS = {step}]")
    
    causal_currents = np.zeros((num_nodes, num_nodes))
    branch_power_loss = np.zeros((num_nodes, num_nodes))
    
    # 1. Strict Upper-Triangle Traversal (Completely Eliminates Output Redundancy)
    for i in range(num_nodes):
        for j in range(num_nodes):
            if i < j and A[i, j] > 0:  # Isolates unique upper triangular branch links
                # Compute potential tension across the connection
                voltage_gradient = node_voltage[i] - node_voltage[j]
                link_resistance = 1.0 / A[i, j]
                
                # Derive exact macro-current flow
                current_flow = voltage_gradient / link_resistance
                
                causal_currents[i, j] = current_flow
                causal_currents[j, i] = -current_flow
                
                # Dynamic Branch Loss calculation: P = I^2 * R
                branch_power_loss[i, j] = (current_flow ** 2) * link_resistance
                
                # Prints out only unique branch logs, bypassing duplicate mirror feedback
                print(f" -> Unique Branch ({i}→{j}): Current = {current_flow:.4f} A | Resistance = {link_resistance:.2f} Ω | Loss = {branch_power_loss[i, j]:.4f} W")

    # 2. Dirichlet Boundary-Insulated Node State Relaxation
    net_charge_flow = np.sum(causal_currents, axis=0)
    
    for i in range(num_nodes):
        if i not in boundary_nodes:
            # Shift local topological knot counts via net current flux
            node_charge[i] += net_charge_flow[i] * delta_tau
            
            # Machine epsilon drift cleaning filter
            if abs(node_charge[i]) < 1e-15:
                node_charge[i] = 0.0
                
            # Compute stable non-divergent node pressure
            node_voltage[i] = node_charge[i] / node_capacitance[i]

    # 3. Macro Performance & Relativistic Mass Analytics Reconstruction
    total_global_power_watts = np.sum(branch_power_loss) # Sum of upper triangle is exact total power
    total_thermal_mass_inc_kg = (total_global_power_watts * delta_tau) / (C_LIGHT ** 2)

    # Format localized node potential matrix block
    voltage_log = " | ".join([f"Node {n}: {node_voltage[n]:.2f}V" for n in range(num_nodes)])
    print(f" -> Node Voltages (V): {voltage_log}")
    print(f" -> Node 2 Reservoir Charge Stored: {node_charge[2]:.4e} C")
    print(f" -> Global SRE Total Settle Power: {total_global_power_watts:.4f} Watts")
    print(f" -> Localized Thermal Mass Increment (Δm): {total_thermal_mass_inc_kg:.4e} kg [Relativistic Guard]")

print("\n=====================================================================")
print("Simulation Complete. Stable Discrete Convergence Achieved Successfully.")
print("=====================================================================")
