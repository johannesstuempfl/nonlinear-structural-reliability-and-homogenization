import numpy as np
from structure import Structure

# Übersetzung: interner DOF-Name → lesbarer Ausgabename
DOF_DISPLAY_NAMES = {
    "u":   "H",
    "w":   "V",
    "phi": "M",
}

class Results:
    """
    Ergebnisbehälter nach dem Lösen.

    Enthält den globalen Verschiebungsvektor u und berechnet
    daraus auf Anfrage Schnittgrößen und Auflagerkräfte.

    Parameters
    ----------
    u         : globaler Verschiebungsvektor (n_dof,)
    structure : Referenz auf die gelöste Struktur
    """

    def __init__(self, u: np.ndarray, structure: Structure):
        self.u          = u
        self._structure = structure

    # ------------------------------------------------------------------ #
    #  Knotenverschiebungen                                                #
    # ------------------------------------------------------------------ #

    def displacements(self, node) -> dict:
        """
        Verschiebungen und Verdrehung eines Knotens.
        Gibt ein Dict zurück, z.B. {'u': 0.002, 'w': -0.005, 'phi': 0.001}
        """
        idx    = node.dof_indices
        labels = node.dof_labels
        return {label: self.u[idx[i]] for i, label in enumerate(labels)}

    # ------------------------------------------------------------------ #
    #  Schnittgrößen                                                       #
    # ------------------------------------------------------------------ #

    def internal_forces(self, element) -> dict:
        """
        Schnittgrößen am Element im lokalen KOS.

        Reihenfolge: [N_i, Q_i, M_i, N_j, Q_j, M_j]

        Berechnung:
            s_lok = k_local · T · u_element
        """
        idx       = element.dof_indices
        f_cl      = element.f_cl
        u_element = self.u[idx]                     # globale Verschiebungen eines Elements
        u_local   = element.T @ u_element           # ins lokale KOS transformieren
        s_local   = element.k_local @ u_local - f_cl   # Schnittgrößen lokal (Volleinspannschnittgrößen werden abgezogen)

        return {
            "N_i":   -s_local[0], # negatives Schnittufer hat entgegengesetzte Vorzeichenkonvention
            "Q_i":   -s_local[1], # negatives Schnittufer hat entgegengesetzte Vorzeichenkonvention
            "M_i":   -s_local[2], # negatives Schnittufer hat entgegengesetzte Vorzeichenkonvention
            "N_j":  s_local[3],   
            "Q_j":  s_local[4],
            "M_j":   s_local[5],
        }

    # ------------------------------------------------------------------ #
    #  Auflagerkräfte                                                      #
    # ------------------------------------------------------------------ #

    def reactions(self) -> dict:
        """
        Auflagerkräfte an allen gelagerten Knoten.

        Berechnung:
            f_react = K · u  (vollständig, nicht reduziert)
        dann nur die gesperrten DOFs ablesen.
        """
        K       = self._structure.assemble_K()
        f_react = K @ self.u

        result = {}
        for node in self._structure.nodes:
            if node.support is None:
                continue
            fixed_labels = [l for l in node.dof_labels if node.is_fixed(l)]
            if not fixed_labels:
                continue
            result[node.id] = {
                label: f_react[node.dof_indices[i]]
                for i, label in enumerate(node.dof_labels)
                if node.is_fixed(label)
            }

        return result

    # ------------------------------------------------------------------ #
    #  Darstellung                                                         #
    # ------------------------------------------------------------------ #

    def print_summary(self) -> None:

        print("=" * 50)
        print("  VERSCHIEBUNGEN")
        print("=" * 50)
        for node in self._structure.nodes:
            d = self.displacements(node)
            vals = ", ".join(f"{k}={v:.6f}" for k, v in d.items())
            print(f"  Knoten {node.id + 1}: {vals}")

        print()
        print("=" * 50)
        print("  SCHNITTGRÖSSEN (lokal)")
        print("=" * 50)
        for elem in self._structure.elements:
            s = self.internal_forces(elem)
            print(f"  Element {elem.id + 1}:")
            print(f"    N:  {s['N_i']:10.4f}  →  {s['N_j']:10.4f}")
            print(f"    Q:  {s['Q_i']:10.4f}  →  {s['Q_j']:10.4f}")
            print(f"    M:  {s['M_i']:10.4f}  →  {s['M_j']:10.4f}")

        print()
        print("=" * 50)
        print("  AUFLAGERKRÄFTE")
        print("=" * 50)
        for node_id, forces in self.reactions().items():
            vals = ", ".join(
                f"{DOF_DISPLAY_NAMES.get(k, k)}={v:.4f}"
                for k, v in forces.items()
            )
            print(f"  Knoten {node_id + 1}: {vals}")
        print("=" * 50)