# utils/colours.py
import plotly.express as px

def get_crime_colour_map():
    """
    Defines a consistent colour map for different crime types.
    """
    colours = px.colors.qualitative.Plotly
    crime_types = [
        "Anti-social behaviour", "Violence and sexual offences", "Criminal damage and arson",
        "Shoplifting", "Other theft", "Public order", "Vehicle crime", "Burglary",
        "Bicycle theft", "Drugs", "Theft from the person", "Robbery", "Possession of weapons",
        "Other crime"
    ]
    plotly_colour_map = {crime: colours[i % len(colours)] for i, crime in enumerate(crime_types)}

    # Renamed parameter to hex_colour
    def hex_to_rgba(hex_colour, alpha=200):
        hex_colour = hex_colour.lstrip('#')
        rgb = tuple(int(hex_colour[i:i+2], 16) for i in (0, 2, 4))
        return list(rgb) + [alpha]

    # Renamed internal variable to 'colour'
    pydeck_colour_map = {crime: hex_to_rgba(colour) for crime, colour in plotly_colour_map.items()}
    return plotly_colour_map, pydeck_colour_map
