import pandas as pd
import dash
from dash import dcc, html, Input, Output
import dash_leaflet as dl
df = pd.read_excel(r"C:\Users\Balkis Mansour\OLECIO\Plateforme - Olecio.fr\Fichier contacts.xlsx")
print(df.head())
region_coords = {
    "Auvergne-Rhône-Alpes": [45.5, 4.8],
    "Bourgogne-Franche-Comté": [47.0, 5.0],
    "Bretagne": [48.1, -2.7],
    "Centre-Val de Loire": [47.6, 1.9],
    "Corse": [42.0, 9.0],
    "Grand Est": [48.6, 6.0],
    "Hauts-de-France": [50.3, 3.0],
    "Ile-de-France": [48.8, 2.3],
    "Normandie": [49.0, 0.2],
    "Nouvelle-Aquitaine": [45.7, 0.2],
    "Occitanie": [43.6, 2.5],
    "Pays de la Loire": [47.5, -0.5],
    "Provence-Alpes-Côte d'Azur": [43.8, 6.2],
    "DROM-COM": [15.0, -61.0]  # exemple pour Guadeloupe/Martinique
}
# Liste des colonnes territoires à vérifier dans ton fichier
territoires = list(region_coords.keys())
import dash
from dash import html, dcc
import dash_leaflet as dl
import pandas as pd
import math
from dash.dependencies import Input, Output, State
# 📌 Génération des marqueurs avec placement circulaire
def generate_markers(data):
    markers = []
    base_radius = 0.08
    step_radius = 0.03
    markers_per_ring = 8

    region_counters = {region: 0 for region in territoires}

    for i, row in data.iterrows():
        for territoire in territoires:
            val = row.get(territoire)
            if isinstance(val, str) and val.strip().upper() == "X":
                base_lat, base_lon = region_coords[territoire]
                count = region_counters[territoire]
                angle_deg = (count * (360 / markers_per_ring)) % 360
                ring = count // markers_per_ring
                angle_rad = math.radians(angle_deg)
                radius = base_radius + step_radius * ring

                lat_offset = radius * math.cos(angle_rad)
                lon_offset = radius * math.sin(angle_rad)
                coord = [base_lat + lat_offset, base_lon + lon_offset]

                tooltip_text = f"{row['Organisation']} - {territoire}"
                markers.append(
                    dl.Marker(
                        position=coord,
                        children=dl.Tooltip(tooltip_text),
                        id={'type': 'marker', 'index': f"{i}_{territoire}"}
                    )
                )

                region_counters[territoire] += 1
    return markers

# 🚀 App Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Cartographie des partenaires Olecio"),

    html.Div([
        dcc.Input(id="recherche", type="text", placeholder="Recherche par nom", style={"width": "30%", "marginRight": "20px"}),

        dcc.Dropdown(
            id="filtre-region",
            options=[{"label": r, "value": r} for r in territoires],
            placeholder="Filtrer par région",
            style={"width": "30%", "marginRight": "20px"}
        ),

        html.Button("🔄 Mettre à jour", id="maj-button", n_clicks=0),
    ], style={"margin": "20px", "display": "flex", "flexWrap": "wrap", "gap": "10px"}),

    dl.Map([
        dl.TileLayer(),
        dl.LayerGroup(id="markers")
    ], id="map", center=[46.5, 2.5], zoom=5, style={'width': '100%', 'height': '70vh'})
])

# 🎯 Callback pour mise à jour des marqueurs et zoom sur la région
@app.callback(
    Output("markers", "children"),
    Output("map", "center"),
    Output("map", "zoom"),
    Input("maj-button", "n_clicks"),
    State("recherche", "value"),
    State("filtre-region", "value")
)
def update_markers(n_clicks, search_val, region_val):
    df = pd.read_excel(r"C:\Users\Balkis Mansour\OLECIO\Plateforme - Olecio.fr\Fichier contacts.xlsx")
    df.columns.values[0] = "Organisation"

    # Recherche par nom
    if search_val:
        df = df[df["Organisation"].str.contains(search_val, case=False, na=False)]

    # Filtrage par région
    if region_val:
        df = df[df[region_val].apply(lambda x: str(x).strip().upper() == 'X')]

    # Filtrer les lignes avec au moins un "X"
    df_filtered = df[df[territoires].applymap(lambda x: str(x).strip().upper() == 'X').any(axis=1)]

    # Générer les marqueurs
    markers = generate_markers(df_filtered)

    # Définir le centre de la carte
    if region_val and region_val in region_coords:
        center = region_coords[region_val]
        zoom = 7
    else:
        center = [46.5, 2.5]
        zoom = 5

    return markers, center, zoom

# ▶️ Lancement de l'app
if __name__ == '__main__':
    app.run(debug=True)
