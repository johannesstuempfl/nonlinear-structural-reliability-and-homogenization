from structure import Structure
from solver_1st import Solver1stOrder
import numpy as np

class BucklingAnalysis:
    """
    Lineare Stabilitätsanalyse (Eigenwertproblem).

    Bestimmt den kleinsten Lastmultiplikator λ für den die
    Tangentensteifigkeit singulaer wird:

        (K + λ · Kg) · u = 0
    →   K · u = -λ · Kg · u
    →   generalisiertes Eigenwertproblem

    Vorgehensweise:
        1. Th.1-Lösung für die angesetzten Lasten
        2. Kg aus den resultierenden Normalkräften aufbauen
        3. Eigenwertproblem auf den freien DOFs lösen
        4. Kleinsten positiven Eigenwert λ_krit ausgeben

    Parameters
    ----------
    n_modes : Anzahl der auszugebenden Eigenformen
    """

    def __init__(self, n_modes: int = 3):
        self.n_modes = n_modes

    def solve(self, structure: Structure) -> dict:
        res_th1 = Solver1stOrder().solve(structure)

        K  = structure.assemble_K()
        Kg = structure.assemble_Kg(res_th1)

        free   = structure.get_free_dofs()
        K_red  = K[np.ix_(free, free)]
        Kg_red = Kg[np.ix_(free, free)]

        # Generalisiertes Eigenwertproblem:
        # K · u = λ · (-Kg) · u
        # umgeformt: K_red_inv · (-Kg_red) · u = (1/λ) · u
        # → standard Eigenwertproblem mit numpy.eig
        from numpy.linalg import solve as lin_solve, eig

        # A = K_red^(-1) · (-Kg_red)
        A = lin_solve(K_red, -Kg_red)

        eigenvalues_raw, eigenvectors_raw = eig(A)

        # Eigenwerte sind 1/λ → umkehren
        # Nur reelle, positive Werte sind physikalisch relevant
        eigenvalues_raw = eigenvalues_raw.real
        eigenvectors_raw = eigenvectors_raw.real

        # λ = 1 / Eigenwert, nur positive λ behalten
        valid_mask = np.abs(eigenvalues_raw) > 1e-10
        ev_valid   = eigenvalues_raw[valid_mask]
        vec_valid  = eigenvectors_raw[:, valid_mask]

        lambdas_all = 1.0 / ev_valid

        pos_mask    = lambdas_all > 1e-6
        if not np.any(pos_mask):
            raise RuntimeError(
                "Keine positiven Eigenwerte gefunden – "
                "prüfe ob Drucklasten vorhanden sind."
            )

        lambdas_pos  = lambdas_all[pos_mask]
        vectors_pos  = vec_valid[:, pos_mask]

        # Aufsteigend sortieren
        sort_idx     = np.argsort(lambdas_pos)
        lambdas_pos  = lambdas_pos[sort_idx]
        vectors_pos  = vectors_pos[:, sort_idx]

        # Kleinste n_modes Eigenwerte
        n       = min(self.n_modes, len(lambdas_pos))
        lambdas = lambdas_pos[:n]
        modes   = vectors_pos[:, :n]

        # Eigenformen in globale Vektoren einbetten
        mode_vectors = []
        for i in range(n):
            u_mode = np.zeros(structure._n_dof)
            for j, dof in enumerate(free):
                u_mode[dof] = modes[j, i]
            mode_vectors.append(u_mode)

        return {
            "lambda":      lambdas,
            "modes":       mode_vectors,
            "results_th1": res_th1,
        }

    def print_summary(self, buckling_result: dict,
                      structure: Structure) -> None:

        lambdas = buckling_result["lambda"]

        print("=" * 55)
        print("  STABILITÄTSANALYSE – KRITISCHE LASTMULTIPLIKATOREN")
        print("=" * 55)
        for i, lam in enumerate(lambdas):
            print(f"  Mode {i+1}: λ = {lam:.4f}  "
                  f"→  F_krit = {lam:.4f} · F_angesetzt")
        print()
        print(f"  Hinweis: Die angesetzten Lasten dürfen nur mit")
        print(f"  λ = {lambdas[0]:.4f} multipliziert werden,")
        print(f"  bevor Versagen eintritt.")
        print("=" * 55)