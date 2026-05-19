import numpy as np
from structure import Structure
from results import Results


class Solver1stOrder:
    """
    Löser für Theorie 1. Ordnung.

    Löst das lineare Gleichungssystem:
        K_red · u_free = f_red

    durch Reduktion auf die freien DOFs (Streichen der
    gesperrten Zeilen und Spalten).
    """

    def solve(self, structure: Structure) -> Results:

        # 1) Gesamtsteifigkeitsmatrix und Lastvektor assemblieren
        K = structure.assemble_K()
        f = structure.assemble_f()

        # 2) Freie und gesperrte DOFs ermitteln
        free  = structure.get_free_dofs()
        fixed = structure.get_fixed_dofs()

        if len(free) == 0:
            raise RuntimeError("Keine freien DOFs – ist das System vollständig eingespannt?")

        # 3) Reduziertes Gleichungssystem aufstellen
        K_red = K[np.ix_(free, free)]
        f_red = f[free]
        
        # 4) Gleichungssystem lösen
        try:
            u_free = np.linalg.solve(K_red, f_red)
        except np.linalg.LinAlgError:
            raise RuntimeError("K_red ist singulär – ist das System kinematisch?")

        # 5) Globalen Verschiebungsvektor zusammensetzen
        u = np.zeros(structure._n_dof)
        for i, dof in enumerate(free):
            u[dof] = u_free[i]

        return Results(u=u, structure=structure)