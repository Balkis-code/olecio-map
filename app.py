import pandas as pd
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential
from io import BytesIO
import os

import dash
from dash import dcc, html, Output, Input
import dash_leaflet as dl

# --- CONFIG SHAREPOINT ---
site_url = "https://olicio.sharepoint.com/sites/Plateforme"
file_relative_url = "/sites/Plateforme/Fichier contacts.xlsx"

username = "balkis.mansour@olecio.fr"
password = "Beki-2002"

# --- Fonction pour lire Excel depuis SharePoint ---
def get_excel_from_sharepoint():
    ctx = ClientContext(site_url).with_credentials(UserCredential(username, password))
    response = ctx.web.get_file_by_server_relative_url(file_relative_url).download().execute_query()
    bytes_file_obj = BytesIO()
    bytes_file_obj.write(response.content)
    bytes_file_obj.seek(0)
    df = pd.read_excel(bytes_file_obj)
    return df

# --- Initialisation Dash ---
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Carte dynamique avec données SharePoint"),
    dcc.Interval(id="interval", interval=60*1000, n_intervals=0),  # mise à jour chaque 60 sec
    dl.Map(id="map", center=[48.8566, 2.3522], zoom=6, style={'width': '100%', 'height': '600px'}),
])

# --- Callback pour mettre à jour la carte ---
@app.callback(
    Output("map", "children"),
    Input("interval", "n_intervals")
)
def update_map(n):
    try:
        df = get_excel_from_sharepoint()
        # Supposons que ton Excel a des colonnes 'Latitude', 'Longitude', 'Nom' pour placer les marqueurs
        markers = []
        for _, row in df.iterrows():
            marker = dl.Marker(position=[row['Latitude'], row['Longitude']], children=dl.Tooltip(row['Nom']))
            markers.append(marker)
        return [dl.TileLayer()] + markers
    except Exception as e:
        print(f"Erreur: {e}")
        return [dl.TileLayer()]  # carte vide si erreur

if __name__ == "__main__":
    app.run(debug=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port, debug=True)







