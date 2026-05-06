import streamlit as st
import ee
from google.oauth2 import service_account

st.set_page_config(page_title="Teste GEE", layout="centered")

@st.cache_resource
def init_gee():
    info = dict(st.secrets["earthengine"])

    credentials = service_account.Credentials.from_service_account_info(
        info,
        scopes=[
            "https://www.googleapis.com/auth/earthengine",
            "https://www.googleapis.com/auth/cloud-platform",
        ],
    )

    ee.Initialize(credentials, project=info["project_id"])
    return ee

st.title("Teste de conexão com Google Earth Engine")

try:
    ee = init_gee()
    st.success("Google Earth Engine inicializado com sucesso.")

    ponto = ee.Geometry.Point([-45.45, -22.42])
    imagem = ee.Image("CGIAR/SRTM90_V4")

    resultado = imagem.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=ponto.buffer(1000),
        scale=90,
        maxPixels=1e9
    ).getInfo()

    st.write("Resultado do teste:")
    st.json(resultado)

except Exception as e:
    st.error(f"Erro ao inicializar o GEE: {e}")
