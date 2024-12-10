import dash_leaflet as dl
from dash_extensions.javascript import assign
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

from functions import get_color

my_conn = create_engine("mysql+pymysql://root:JHaA6_X~d_@62.171.178.235/ne_database")

# def get_color(rxlev):
#     if rxlev >= -50:
#         return "green"
#     elif -60 <= rxlev < -50:
#         return "yellow"
#     else:
#         return "red"

def get_dt(sets):
    # df_coord = pd.DataFrame(sets, columns=["Latitude", "Longitude"])
    # lats = df_coord['Latitude'].to_list()
    # longs = df_coord['Longitude'].to_list()
    # lat0, lat1 = str(min(lats)), str(max(lats))
    # long0, long1 = str(min(longs)), str(max(longs))
    # query = f"select * from drivetest.dt where (Latitude between {lat0} and {lat1}) and (Longitude between {long0} and {long1})"
    # df = pd.read_sql(query, con=my_conn)
    # df.dropna(inplace=True)
    # df['RxLev'] = df['RxLev'].astype(float)
    # return df
    df_coord = pd.DataFrame(sets, columns=["Latitude", "Longitude"])
    lats=df_coord['Latitude'].to_list()
    longs=df_coord['Longitude'].to_list()

    lat0=str(min(lats))
    lat1=str(max(lats))
    long0=str(min(longs))
    long1=str(max(longs))

    query='select * from drivetest.dt where (Latitude between ' + lat0 + ' and ' +lat1 + ') and (Longitude between ' + long0 + ' and ' + long1 +')'

    # Sample DataFrame
    df=pd.read_sql(query, con = my_conn)
    df['Longitude'] = df['Longitude'].astype(float)
    df['Latitude'] = df['Latitude'].astype(float)
    print(df.info())
    #df.replace(r"^\s*$", np.nan, regex=True, inplace=True)
    df.dropna()
    df=df[df['RxLev']!='']
    df['RxLev']=df['RxLev'].astype(float)
    df=df.loc[df['RxLev'].notna()]
    # print(df.info())
    return df


def generate_geojson(sets):
    df = get_dt(sets)
    features = [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(row["Longitude"]), float(row["Latitude"])]  # Ensure float
            },
            "properties": {
                "RxLev": row["RxLev"],
                "Cluster": row["Cluster"],
                "hidden": False,  # Initially, all features are visible
                "color": get_color(row["RxLev"])
            }
        }
        for _, row in df.iterrows()
    ]
    geojson_data =  {"type": "FeatureCollection", "features": features}
    # print("Generated GeoJSON:", geojson_data)  # Debug print
    return {"type": "FeatureCollection", "features": features}