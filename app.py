import requests
import pandas as pd
import matplotlib as plt
import streamlit as st
import datetime 
from datetime import timedelta

url = "https://api.argentinadatos.com"

def obtener_data(url, param_busqueda = ""):
    try:
        response = requests.get(f"{url}{param_busqueda}")
        data = response.json()
    except:
        data = None
        print("Error al obtener los datos")
    finally:
        return data

def exploracion_data_nula(data):
    df_data = pd.DataFrame(data)
    df_data["casa"] = df_data["casa"].fillna("Sin nombre")
    df_data["compra"] = df_data["compra"].fillna(0)
    df_data["venta"] = df_data["venta"].fillna(0)
    df_data["fecha"] = df_data["fecha"].fillna("Sin fecha")
    return df_data

def data_a_csv(data):
    data.to_csv("cotizacion_dolar_argentina", index=False)
    return print("Archivo generado correctamente")

def restringir_df(fecha, data_analisis, df_base):
    fecha_fin = fecha + timedelta(days = 20)
    df_para_grafico = df_base[df_base["fecha"] >= str(fecha)]
    df_para_grafico = df_para_grafico[df_para_grafico["fecha"] <= str(fecha_fin)]
    df_para_grafico = df_para_grafico[df_para_grafico["casa"].isin(data_analisis)]
    return df_para_grafico

def hacer_grafico_compra(df_restringido):
    df_restringido["dia"] = df_restringido["fecha"].str.split('-').str[2]
    df_restringido.sort_values(by = "fecha", inplace = True)
    fig, ax = plt.subplots(figsize = (12, 8))
    for casa in df_restringido['casa'].unique():
        df_casa = df_restringido[df_restringido['casa'] == casa]
        ax.plot(df_casa['dia'], df_casa['compra'], label=casa)
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Precio (En pesos Argentinos)')
    ax.set_title('Valor de la compra del Dolar en Argentina')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

def hacer_grafico_venta(df_restringido):
    df_restringido["dia"] = df_restringido["fecha"].str.split('-').str[2]
    df_restringido.sort_values(by = "fecha", inplace = True)
    fig, ax = plt.subplots(figsize = (12, 8))
    for casa in df_restringido['casa'].unique():
        df_casa = df_restringido[df_restringido['casa'] == casa]
        ax.plot(df_casa['dia'], df_casa['venta'], label=casa)
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Precio (En pesos Argentinos)')
    ax.set_title('Valor de la venta del Dolar en Argentina')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

def precios_actuales(df_base):
    fecha_inicio = datetime.date.today() - timedelta(days = 21)
    data_a_analizar = ["oficial", "blue", "mayorista", "contadoconliqui", "tarjeta", "solidario", "bolsa"]
    df_restringido = restringir_df(fecha_inicio, data_a_analizar, df_base)
    st.write("Estadisticas varias de los precios en los ultimos 20 dias")
    st.write(df_restringido.describe())
    st.subheader("Precios de Compra y Venta del Dolar en Argentina en los ultimos 20 dias")
    hacer_grafico_compra(df_restringido)
    hacer_grafico_venta(df_restringido)

def main():
    st.set_page_config(page_title = "Analisis dolar en Argentina", page_icon = ":dollar:", layout = "centered")
    cotizacion_dolar = obtener_data(url, "/v1/cotizaciones/dolares")
    df_base = exploracion_data_nula(cotizacion_dolar)
    data_a_csv(df_base)
    st.sidebar.title("Menu Principal")
    opcion =st.sidebar.selectbox("Selecciona la opcion deseada", ["Pagina Principal", "Precios Actuales"])

    if opcion == "Pagina Principal":
        st.title("Analisis dolar en Argentina")
        st.subheader("Data desde el año 2011 a la Actualidad")
        st.write("Rellene los parametros para revisar sus graficos")
        data_a_analizar = st.multiselect("Selecciona la casa o las casas a analizar", ["oficial", "blue", "mayorista", "contadoconliqui", "tarjeta", "solidario", "bolsa"])
        fecha_inicio = st.date_input("Selecciona la fecha de inicio del grafico", min_value = datetime.date(2011, 1, 1), max_value = datetime.date.today())

        if st.button("Generar Graficos"):
            df_restringido = restringir_df(fecha_inicio, data_a_analizar, df_base)
            hacer_grafico_compra(df_restringido)
            hacer_grafico_venta(df_restringido)
            df_restringido = df_restringido.sort_values(by = "fecha")
            for casa in df_restringido['casa'].unique():
                df_casa = df_restringido[df_restringido['casa'] == casa]
                st.table(df_casa)
    
    elif opcion == "Precios Actuales":
        st.title("Precios Actuales")
        fecha_ultima_actualizacion = df_base["fecha"].max()
        df_ultima_data = df_base[df_base["fecha"] == fecha_ultima_actualizacion]
        df_ultima_actualizacion = df_ultima_data["fecha"].max()
        st.table(df_ultima_data)
        st.write(f"Ultima actualizacion: {df_ultima_actualizacion}")
        precios_actuales(df_base)
main() 
