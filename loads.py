import numpy as np
from node import Node
from element import Element


class Load:
    """Abstrakte Basisklasse für alle Lasttypen."""

    def assemble_into(self, f: np.ndarray) -> None:
        raise NotImplementedError


class NodeLoad(Load):
    """
    Knotenlast: Einzelkraft und/oder Moment direkt an einem Knoten.

    Parameter
    ----------
    node : Zielknoten
    Fx   : Kraft in globaler x-Richtung [kN]
    Fz   : Kraft in globaler z-Richtung [kN]  (z nach unten positiv)
    M    : Moment [kNm]  (gegen Uhrzeigersinn positiv)
    """

    def __init__(self, node: Node, Fx: float = 0.0, Fz: float = 0.0, M: float = 0.0):
        self.node = node
        self.Fx   = Fx
        self.Fz   = Fz
        self.M    = M

    def assemble_into(self, f: np.ndarray) -> None:
        idx = self.node.dof_indices   # z.B. [0, 1, 2]
        f[idx[0]] += self.Fx
        f[idx[1]] += self.Fz
        if len(idx) == 3:             # Rahmenknoten hat phi-DOF
            f[idx[2]] += self.M

    def __repr__(self) -> str:
        return (f"NodeLoad(node={self.node.id}, "
                f"Fx={self.Fx}, Fz={self.Fz}, M={self.M})")

class DistLoad(Load):
    """
    Gleichstreckenlast auf einem Element.

    Parameters
    ----------
    element : belastetes Element
    qx      : Streckenlast in lokaler x'-Richtung [kN/m]  (Normalkraft)
    qz      : Streckenlast in lokaler z'-Richtung [kN/m]  (Querkraft)
    local   : True  → qx/qz im lokalen KOS des Stabs
              False → qx/qz im globalen KOS
    """
    def __init__(self, element: Element, qx: float = 0.0, qz: float = 0.0, local: bool = True):
        self.element = element
        self.qx      = qx
        self.qz      = qz
        self.local   = local
        
    def _fixed_end_forces_local(self) -> np.ndarray:
        """
        Festeinspannkräfte im lokalen KOS.
        Reihenfolge: [Fx_i, Fz_i, M_i, Fx_j, Fz_j, M_j]

        Vorzeichen-Konvention: Festeinspannkräfte wirken dem
        Lastvektor entgegen → werden mit negativem Vorzeichen
        in f eingetragen (d.h. hier positiv berechnet, Minus beim Eintragen).
        """
        L  = self.element.L
        qx = self.qx
        qz = self.qz
        
        # Falls Last im globalen KOS angegeben: erst transformieren (Global -> Lokal)
        if not self.local:
            c  = np.cos(self.element.angle)
            s  = np.sin(self.element.angle)
            qx_loc =  c * qx + s * qz
            qz_loc = -s * qx + c * qz
            qx, qz = qx_loc, qz_loc
            
        # Volleinspannschnittgrößen lokal
        Fx_i = qx * L / 2
        Fz_i = qz * L / 2
        M_i  = -qz * L**2 / 12
        Fx_j = qx * L / 2
        Fz_j = qz * L / 2
        M_j  = qz * L**2 / 12
        
        # auf Element kopieren
        self.element.f_cl += np.array([Fx_i, Fz_i, M_i, Fx_j, Fz_j, M_j])
        
        return np.array([Fx_i, Fz_i, M_i, Fx_j, Fz_j, M_j])
    
    
    def assemble_into(self, f: np.ndarray) -> None:
        """
        Trägt die äquivalenten Knotenlasten in den globalen Lastvektor ein.
        Die Festeinspannkräfte werden transformiert und mit negativem
        Vorzeichen addiert (Umlagerung auf Knoten).
        """
        f_lok = self._fixed_end_forces_local()

        # Lokale Festeinspannkräfte → globales KOS
        T     = self.element.T
        f_glo = T.T @ f_lok

        # In f eintragen
        idx = self.element.dof_indices
        for i_local, i_global in enumerate(idx):
            f[i_global] += f_glo[i_local]

    def __repr__(self) -> str:
        sys = "lokal" if self.local else "global"
        return (f"DistLoad(elem={self.element.id}, "
                f"qx={self.qx}, qz={self.qz}, {sys})")