import numpy as np
from skyfield.api import load, utc
from shapely.geometry import Point, Polygon

# Загрузка границ из файла
def parse_boundaries(filename):
    boundaries = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) < 4:
                continue
            ra = float(parts[0])
            dec = float(parts[1])
            const = parts[2]
            if const not in boundaries:
                boundaries[const] = []
            boundaries[const].append((ra, dec))
    return boundaries

boundaries_j2000 = parse_boundaries('boundaries.txt')

# Проверка принадлежности точки созвездию
def point_in_constellation(ra_deg, dec_deg, polygon_points):
    ra0 = np.radians(ra_deg)
    dec0 = np.radians(dec_deg)
    points_rad = [(np.radians(ra), np.radians(dec)) for ra, dec in polygon_points]
    x0 = np.cos(dec0) * np.cos(ra0)
    y0 = np.cos(dec0) * np.sin(ra0)
    z0 = np.sin(dec0)
    east = np.array([-np.sin(ra0), np.cos(ra0), 0])
    north = np.array([-np.sin(dec0)*np.cos(ra0), -np.sin(dec0)*np.sin(ra0), np.cos(dec0)])
    proj = []
    for ra, dec in points_rad:
        x = np.cos(dec) * np.cos(ra)
        y = np.cos(dec) * np.sin(ra)
        z = np.sin(dec)
        e = (x - x0) * east[0] + (y - y0) * east[1] + (z - z0) * east[2]
        n = (x - x0) * north[0] + (y - y0) * north[1] + (z - z0) * north[2]
        proj.append((e, n))
    polygon = Polygon(proj)
    point = Point(0.0, 0.0)
    return polygon.contains(point)

def get_constellation(ra_deg, dec_deg):
    for const, points in boundaries_j2000.items():
        if point_in_constellation(ra_deg, dec_deg, points):
            return const
    return None

# Эфемериды
ts = load.timescale()
eph = load('de440.bsp')
sun = eph['sun']
earth = eph['earth']

def sun_position(dt_utc):
    t = ts.from_datetime(dt_utc)
    astrometric = earth.at(t).observe(sun)
    ra, dec, _ = astrometric.radec()
    return ra._degrees, dec.degrees

# Архетипы
archetypes = {
    'ARI': 'Пробуждающийся Воин',
    'TAU': 'Хранитель Ресурсов',
    'GEM': 'Связующий',
    'CNC': 'Чуткий Страж',
    'LEO': 'Сердце Системы',
    'VIR': 'Мастер Анализа и Целительства',
    'LIB': 'Стратег Мгновенного Выбора',
    'SCO': 'Алхимик Кризиса',
    'OPH': 'Целитель / Мудрец',
    'SGR': 'Искатель Смыслов',
    'CAP': 'Архитектор Реальности',
    'AQR': 'Проводник Будущего',
    'PSC': 'Творец Снов',
}

def sun_constellation(dt_utc):
    ra, dec = sun_position(dt_utc)
    code = get_constellation(ra, dec)
    arch = archetypes.get(code, 'Неизвестный архетип')
    return code, arch
