"""Calculo de regiones para layouts (split horizontal/vertical)."""
from ncurses_ui.kernel.renderer import Region


def _parse(spec):
    if isinstance(spec, int):
        return spec, None
    if isinstance(spec, dict):
        if "size" in spec:
            return int(spec["size"]), None
        return 0, float(spec.get("weight", 1))
    if spec == "fill":
        return 0, 1.0
    return 0, 1.0


def split(region, specs, horizontal=False, gap=0):
    """Divide `region` en sub-regiones segun `specs`.

    Cada spec es un tamano fijo (`int` o `{"size": n}`) o flexible
    (`"fill"`, `{"weight": w}`). Los flexibles se reparten el espacio
    restante; el sobrante de redondeo va al ultimo flexible.
    """
    total = region.width if horizontal else region.height
    count = len(specs)
    if count == 0:
        return []
    parsed = [_parse(spec) for spec in specs]
    fixed = sum(size for size, _ in parsed)
    remaining = max(0, total - fixed - gap * (count - 1))
    weights = [weight for _, weight in parsed]
    total_weight = sum(weight for weight in weights if weight is not None)
    sizes = []
    flexible = []
    for i, (size, weight) in enumerate(parsed):
        if weight is None:
            sizes.append(size)
        else:
            flexible.append(i)
            sizes.append(int(remaining * weight / total_weight) if total_weight else 0)
    leftover = remaining - sum(sizes[i] for i in flexible)
    if leftover and flexible:
        sizes[flexible[-1]] += leftover
    regions = []
    cursor = region.y if not horizontal else region.x
    for size in sizes:
        if horizontal:
            regions.append(Region(region.y, cursor, region.height, max(0, size)))
        else:
            regions.append(Region(cursor, region.x, max(0, size), region.width))
        cursor += size + gap
    return regions
