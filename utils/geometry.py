# utils/geometry.py

def is_point_in_polygon(point, polygon):
    """
    Checks if a point is inside a given polygon using the Ray-Casting algorithm.
    """
    lon, lat = point
    vertices = polygon
    n = len(vertices)
    inside = False

    p1_lon, p1_lat = vertices[0]
    for i in range(n + 1):
        p2_lon, p2_lat = vertices[i % n]
        if lat > min(p1_lat, p2_lat):
            if lat <= max(p1_lat, p2_lat):
                if lon <= max(p1_lon, p2_lon):
                    if p1_lat != p2_lat:
                        xinters = (lat - p1_lat) * (p2_lon - p1_lon) / (p2_lat - p1_lat) + p1_lon
                    if p1_lon == p2_lon or lon <= xinters:
                        inside = not inside
        p1_lon, p1_lat = p2_lon, p2_lat

    return inside
