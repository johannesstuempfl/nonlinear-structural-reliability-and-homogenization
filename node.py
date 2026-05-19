# Freiheitsgrade pro Knotentyp
import numpy as np

DOF_LABELS = {
    "frame": ["u", "w", "phi"],   # Rahmen: x-Verschiebung, z-Verschiebung, Verdrehung
    "truss": ["u", "w"],          # Fachwerk: nur Verschiebungen, keine Verdrehung
}

class Node:
    """
    Repräsentiert einen Knoten im ebenen Stabwerk.

    Parameters
    ----------
    id      : eindeutige Knotennummer (0-basiert empfohlen)
    x, z    : Koordinaten im globalen KOS [m]
    kind    : 'frame' (3 DOF) oder 'truss' (2 DOF)
    support : Wörterbuch der gesperrten DOFs, z.B.
              {'u': True, 'w': True, 'phi': False}  → Gelenklager
              {'u': True, 'w': True, 'phi': True}   → Einspannung
              None                                  → freier Knoten
    """
    def __init__(self, id: int, x: float, z: float, kind: str = "frame", support: dict = None):
        
        if support is not None:
            valid = set(DOF_LABELS[kind])
            unknown = set(support) - valid
            if unknown:
                raise ValueError(f"Unbekannte DOF-Bezeichnung(en): {unknown}")

        self.id = id
        self.x = x
        self.z = z
        self.kind = kind
        self.support = support
        # Globale DOF Indizes -> Wird später von Structure.assemble() gesetzt
        self.dof_indices = []
        
    # ------------------------------------------------------------------ #
    #  Properties                                                          #
    # ------------------------------------------------------------------ #
    @property
    def coords(self) -> np.ndarray:
        return np.array([self.x, self.z])
    
    @property
    def n_dof(self) -> int:
        return len(DOF_LABELS[self.kind])
    
    @property
    def dof_labels(self) -> list:
        return DOF_LABELS[self.kind]
    
    # ------------------------------------------------------------------ #
    #  Lagerungs-Abfragen                                                  #
    # ------------------------------------------------------------------ #
    
    def is_fixed(self, dof_label: str) -> bool:
        if self.support is None:
            return False
        return self.support.get(dof_label, False)
    
    # wird erst verwendet, wenn Structure das dof_indices[] füllt
    @property
    def free_dof_indices(self) -> list:
        return [
            self.dof_indices[i]
            for i, label in enumerate(self.dof_labels)
            if not self.is_fixed(label)
        ]
        
    # wird erst verwendet, wenn Structure das dof_indices[] füllt
    @property
    def fixed_dof_indices(self) -> list:
        return [
            self.dof_indices[i]
            for i, label in enumerate(self.dof_labels)
            if self.is_fixed(label)
        ]
        
    # ------------------------------------------------------------------ #
    #  Darstellung                                                         #
    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:
        sup = self.support or "frei"
        return (f"Node(id={self.id}, x={self.x}, z={self.z}, "
                f"kind='{self.kind}', support={sup}, "
                f"dofs={self.dof_indices})")


# # Verwendung
# n1 = Node(id=0, x=0.0, z=0.0, support={"u": True, "w": True, "phi": True})
# n2 = Node(id=1, x=5.0, z=0.0)  # freier Knoten
# n3 = Node(id=2, x=10.0, z=0.0, support={"u": False, "w": True, "phi": False})

