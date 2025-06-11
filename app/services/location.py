# app/services/location.py
import math
from typing import Tuple, List, Dict
from dataclasses import dataclass


@dataclass
class Location:
    latitude: float
    longitude: float
    address: str = ""


def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula a distância entre dois pontos geográficos usando a fórmula de Haversine
    Retorna a distância em quilômetros
    """
    R = 6371  # Raio da Terra em km

    # Converte graus para radianos
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Diferenças
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Fórmula de Haversine
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return round(distance, 2)


def is_within_radius(
        center_lat: float,
        center_lon: float,
        point_lat: float,
        point_lon: float,
        radius_km: float
) -> bool:
    """Verifica se um ponto está dentro de um raio específico"""
    distance = calculate_distance_km(center_lat, center_lon, point_lat, point_lon)
    return distance <= radius_km


def get_bounding_box(
        center_lat: float,
        center_lon: float,
        radius_km: float
) -> Tuple[float, float, float, float]:
    """
    Calcula o bounding box (retângulo) que contém um círculo
    Retorna: (min_lat, max_lat, min_lon, max_lon)
    Útil para otimizar consultas no banco de dados
    """
    # Aproximação simples: 1 grau ≈ 111 km
    lat_delta = radius_km / 111.0
    lon_delta = radius_km / (111.0 * math.cos(math.radians(center_lat)))

    min_lat = center_lat - lat_delta
    max_lat = center_lat + lat_delta
    min_lon = center_lon - lon_delta
    max_lon = center_lon + lon_delta

    return min_lat, max_lat, min_lon, max_lon


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula o bearing (direção) entre dois pontos
    Retorna o ângulo em graus (0-360)
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlon_rad = math.radians(lon2 - lon1)

    y = math.sin(dlon_rad) * math.cos(lat2_rad)
    x = (math.cos(lat1_rad) * math.sin(lat2_rad) -
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad))

    bearing = math.atan2(y, x)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360  # Normaliza para 0-360

    return round(bearing, 2)


def get_cardinal_direction(bearing: float) -> str:
    """Converte bearing em direção cardinal (N, NE, E, SE, S, SW, W, NW)"""
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = round(bearing / 45) % 8
    return directions[index]


def format_distance(distance_km: float) -> str:
    """Formata distância para exibição amigável"""
    if distance_km < 1:
        return f"{int(distance_km * 1000)}m"
    elif distance_km < 10:
        return f"{distance_km:.1f}km"
    else:
        return f"{int(distance_km)}km"


def sort_by_distance(
        center_lat: float,
        center_lon: float,
        locations: List[Dict]
) -> List[Dict]:
    """
    Ordena uma lista de localizações por distância
    Cada localização deve ter 'latitude' e 'longitude'
    Adiciona o campo 'distance_km' a cada item
    """
    for location in locations:
        distance = calculate_distance_km(
            center_lat, center_lon,
            location['latitude'], location['longitude']
        )
        location['distance_km'] = distance
        location['distance_formatted'] = format_distance(distance)

    return sorted(locations, key=lambda x: x['distance_km'])


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Valida se as coordenadas são válidas"""
    return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)


# Constantes úteis para o Brasil
BRAZIL_BOUNDS = {
    'min_lat': -33.75,  # Ponto mais ao sul
    'max_lat': 5.27,  # Ponto mais ao norte
    'min_lon': -73.99,  # Ponto mais a oeste
    'max_lon': -28.84  # Ponto mais a leste
}


def is_in_brazil(latitude: float, longitude: float) -> bool:
    """Verifica se as coordenadas estão dentro do território brasileiro"""
    return (
            BRAZIL_BOUNDS['min_lat'] <= latitude <= BRAZIL_BOUNDS['max_lat'] and
            BRAZIL_BOUNDS['min_lon'] <= longitude <= BRAZIL_BOUNDS['max_lon']
    )


# Coordenadas das principais cidades brasileiras (para referência/testes)
MAJOR_CITIES = {
    'brasilia': (-15.7801, -47.9292),
    'sao_paulo': (-23.5558, -46.6396),
    'rio_de_janeiro': (-22.9068, -43.1729),
    'belo_horizonte': (-19.9191, -43.9378),
    'salvador': (-12.9714, -38.5014),
    'fortaleza': (-3.7319, -38.5267),
    'recife': (-8.0476, -34.8770),
    'curitiba': (-25.4284, -49.2733),
    'porto_alegre': (-30.0346, -51.2177),
    'manaus': (-3.1190, -60.0217)
}