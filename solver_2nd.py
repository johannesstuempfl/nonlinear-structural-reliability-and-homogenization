import numpy as np
from structure import Structure
from results import Results
from solver_1st import Solver1stOrder

class Solver2ndOrder:
    """
    Löser für Theorie 2. Ordnung.

    Iteratives Verfahren:
        1. Th1-Lösung als Startwert
        2. Kg aus Normalkräften aufbauen
        3. (K + Kg)_red · u_free = f_red lösen
        4. Wiederholen bis ||u_neu - u_alt|| < tol
    """

    def __init__(self, tol: float = 1e-6, max_iter: int = 50):
        self.tol      = tol
        self.max_iter = max_iter

    def solve(self, structure: Structure) -> Results:

        # --- Schritt 1: Th1-Startwert ---
        solver_th1 = Solver1stOrder()
        results    = solver_th1.solve(structure)

        K     = structure.assemble_K()
        f     = structure.assemble_f()
        free  = structure.get_free_dofs()

        f_red = f[free]

        # --- Iterationsschleife ---
        for iteration in range(self.max_iter):

            u_alt = results.u.copy()

            # Kg aus aktuellen Normalkräften aufbauen
            Kg    = structure.assemble_Kg(results)
            KT    = K + Kg                              # Tangentensteifigkeit

            # Reduziertes System
            KT_red = KT[np.ix_(free, free)]

            try:
                u_free = np.linalg.solve(KT_red, f_red)
            except np.linalg.LinAlgError:
                raise RuntimeError(
                    f"System singulaer in Iteration {iteration+1} – "
                    "Knicklast überschritten?"
                )

            # Globalen Verschiebungsvektor zusammensetzen
            u = np.zeros(structure._n_dof)
            for i, dof in enumerate(free):
                u[dof] = u_free[i]

            results = Results(u=u, structure=structure)

            # Konvergenzprüfung
            delta = np.linalg.norm(u - u_alt)
            print(f"  Iteration {iteration+1:2d}: ||Δu|| = {delta:.2e}")
            
            if delta < self.tol:
                print(f"  Konvergiert nach {iteration+1} Iterationen.")
                return results

        raise RuntimeError(
            f"Keine Konvergenz nach {self.max_iter} Iterationen. "
            "Knicklast überschritten oder tol zu streng?"
        )

# class Solver2ndOrder:
#     """
#     Löser für Theorie 2. Ordnung.
#     """
#     def __init__(self):
#         self.N_dict = {}
#         self.results_list = []
    
#     def solve1st(self, structure: Structure):
#         # Berechnung nach Th.I.O. für Iteration 0 -> Funktion analog zu Solver1stOrder
#         # 1) Gesamtsteifigkeitsmatrix und Lastvektor assemblieren
#         K = structure.assemble_K()
#         f = structure.assemble_f()

#         # 2) Freie und gesperrte DOFs ermitteln
#         free  = structure.get_free_dofs()
#         fixed = structure.get_fixed_dofs()

#         if len(free) == 0:
#             raise RuntimeError("Keine freien DOFs – ist das System vollständig eingespannt?")

#         # 3) Reduziertes Gleichungssystem aufstellen
#         K_red = K[np.ix_(free, free)]
#         f_red = f[free]

#         # 4) Gleichungssystem lösen
#         try:
#             u_free = np.linalg.solve(K_red, f_red)
#         except np.linalg.LinAlgError:
#             raise RuntimeError("K_red ist singulär – ist das System kinematisch?")

#         # 5) Globalen Verschiebungsvektor zusammensetzen
#         u = np.zeros(structure._n_dof)
#         for i, dof in enumerate(free):
#             u[dof] = u_free[i]

#         return Results(u=u, structure=structure)


#     def solve(self, structure: Structure, n_iterations: int, N_tolerance : float) -> Results:
        
#         iteration = 0
#         print("="*50)
#         print(f"Iteration: {iteration}")
        
#         # 1. Lösung nach Th.I.O.
#         results_TH1 = self.solve1st(structure)
#         self.results_list.append(results_TH1)
        
#         # 2. Rückrechnen der Normalkräfte für jedes Element
#         for element in structure.elements:
#             internal_forces = results_TH1.internal_forces(element)
            
#             # Normalkräfte immer konstant -> Wert von Stabanfang verwendet
#             N = internal_forces["N_i"]
#             # Update
#             element.N = N
            
#             # Save N to N_dict
#             self.N_dict[f"element_{element.id}"] = []
#             self.N_dict[f"element_{element.id}"].append(N)
            
#             print(f"N: {N}")
            
#         iteration += 1
        
#         while iteration < n_iterations:
#             print("="*50)
#             print(f"Iteration: {iteration}")
            
#             # Berechnung nach Th.II.O. für Iteration i 
#             # 1) Gesamtsteifigkeitsmatrix und Lastvektor assemblieren
#             K = structure.assemble_K_TH2()
#             f = structure.assemble_f()

#             # 2) Freie und gesperrte DOFs ermitteln
#             free  = structure.get_free_dofs()
#             fixed = structure.get_fixed_dofs()

#             # 3) Reduziertes Gleichungssystem aufstellen
#             K_red = K[np.ix_(free, free)]
#             f_red = f[free]

#             # 4) Gleichungssystem lösen
#             try:
#                 u_free = np.linalg.solve(K_red, f_red)
#             except np.linalg.LinAlgError:
#                 raise RuntimeError("K_red ist singulär – ist das System kinematisch?")

#             # 5) Globalen Verschiebungsvektor zusammensetzen
#             u = np.zeros(structure._n_dof)
#             for i, dof in enumerate(free):
#                 u[dof] = u_free[i]
            
#             results_TH2 = Results(u=u, structure=structure)
#             self.results_list.append(results_TH2)
            
#             # Rückrechnen der Normalkräfte für jedes Element
#             for element in structure.elements:
#                 internal_forces = results_TH2.internal_forces(element)
                
#                 # Normalkräfte immer konstant -> Wert von Stabanfang verwendet
#                 N = internal_forces["N_i"]
#                 # Update
#                 element.N = N
                
#                 self.N_dict[f"element_{element.id}"].append(N)
#                 print(f"N: {N}")
            
#             iteration += 1
        
#         return self.results_list[-1]