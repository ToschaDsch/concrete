def get_ei_from_eo_eu_z_h(eo: float, eu: float, h: float, z: float) -> float:
    return (eu - eo) * (h + z) / h + eo
