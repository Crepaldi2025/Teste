Autenticação do Google Earth Engine para Aplicações Streamlit

Este repositório contém uma aplicação desenvolvida em **Streamlit** com integração ao **Google Earth Engine**, utilizando autenticação por **conta de serviço** associada a um projeto do **Google Cloud**.

O objetivo principal é disponibilizar uma estrutura básica, segura e reprodutível para implantação de aplicações geoespaciais em ambiente de nuvem, especialmente no **Streamlit Community Cloud**.

---

Objetivo

O projeto tem como finalidade demonstrar e organizar o processo de autenticação entre uma aplicação Streamlit e os serviços do Google Earth Engine, utilizando:

- projeto configurado no Google Cloud;
- Google Earth Engine API ativada;
- projeto registrado para uso no Earth Engine;
- conta de serviço com permissões adequadas;
- chave privada em formato JSON;
- arquivo `secrets.toml` para armazenamento seguro das credenciais no ambiente Streamlit.

---

Estrutura básica do projeto

A estrutura mínima recomendada para o projeto é:

```text
meu_app_gee_streamlit/
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
└── .streamlit/
    └── secrets.toml
