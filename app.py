import streamlit as st

st.set_page_config(
    page_title="Aplicação Streamlit com Google Earth Engine",
    page_icon="🌎",
    layout="centered"
)

st.title("Autenticação do Google Earth Engine para Aplicações Streamlit")

st.write(
    "Esta é uma aplicação inicial de teste para verificar se o deploy "
    "no Streamlit Community Cloud foi realizado corretamente."
)

st.info(
    "Se esta página está sendo exibida, significa que o arquivo app.py "
    "foi carregado e executado com sucesso."
)

st.subheader("Status inicial")

st.success("Aplicação Streamlit operacional.")

st.markdown(
    """
    **Próximas etapas:**

    1. conferir se o arquivo `requirements.txt` foi reconhecido;
    2. configurar os secrets no Streamlit Community Cloud;
    3. testar a autenticação com o Google Earth Engine;
    4. substituir ou ampliar este código com as funcionalidades definitivas da aplicação.
    """
)
