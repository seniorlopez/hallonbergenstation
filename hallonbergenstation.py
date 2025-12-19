import streamlit as st
import requests
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Metro Hallonbergen VIP",
    page_icon="👑",
    layout="centered"
)

# --- TU LLAVE Y CONFIGURACIÓN ---
API_KEY = st.secrets["API_KEY"] if "API_KEY" in st.secrets else "TU_API_KEY_AQUI"
STATION_ID = "740021675" # Hallonbergen T-Bana

# --- FUNCIÓN AUXILIAR: SUMAR MINUTOS ---
def calcular_llegada(hora_salida_str, minutos_a_sumar):
    """
    Recibe la hora tipo "14:30:00" o "14:30", le suma minutos 
    y devuelve la nueva hora limpia "14:53".
    """
    try:
        # ResRobot a veces manda segundos, a veces no. Limpiamos.
        # Nos quedamos solo con HH:MM
        hora_corta = hora_salida_str[:5] 
        formato = "%H:%M"
        
        # Convertimos texto a objeto de tiempo
        dt_obj = datetime.strptime(hora_corta, formato)
        
        # Sumamos los minutos
        nueva_hora = dt_obj + timedelta(minutes=minutos_a_sumar)
        
        # Regresamos texto bonito
        return nueva_hora.strftime("%H:%M")
    except Exception:
        return "??"

# --- FUNCIÓN PARA TRAER DATOS ---
@st.cache_data(ttl=30)
def obtener_datos(hora_consulta): # <--- 1. AHORA RECIBE LA HORA
    # 2. AÑADIMOS &time={hora_consulta} Y AUMENTAMOS duration A 120
    url = f"https://api.resrobot.se/v2.1/departureBoard?id={STATION_ID}&format=json&accessId={API_KEY}&duration=120&time={hora_consulta}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

# ================= INTERFAZ GRÁFICA =================

# 1. HORA ACTUAL CENTRADA (Gigante)
hora_sistema = datetime.now().strftime("%H:%M")
st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{hora_sistema}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: gray;'>Hora actual en tu dispositivo</p>", unsafe_allow_html=True)

st.divider()

if st.button('🔄 Refrescar Tablero', use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# Usamos la misma hora que mostramos en pantalla para que coincida perfectamente
data = obtener_datos(hora_sistema)

if not data or 'Departure' not in data:
    st.error("❌ No pude conectar con la central. Checa tu internet.")
else:
    salidas = data['Departure']
    if isinstance(salidas, dict): salidas = [salidas]

    hacia_ciudad = [] 
    hacia_norte = []  

    for tren in salidas:
        # Filtro de Línea 11
        producto = tren.get('Product')
        linea = "?"
        if isinstance(producto, list): linea = producto[0].get('num', '?')
        elif isinstance(producto, dict): linea = producto.get('num', '?')
        
        if str(linea).strip() != "11":
            continue 

        # Datos base
        destino = tren.get('direction', '').replace(" T-bana", "").replace(" (Stockholm kn)", "")
        hora_prog = tren.get('time', '')[:5] # Cortamos segundos
        hora_real = tren.get('rtTime', hora_prog)[:5]
        
        # Estado
        if hora_prog == hora_real:
            color = "green"
            display_hora = hora_prog
        else:
            color = "red"
            display_hora = f"{hora_real}" # Mostramos la hora real si hay retraso

        # Calculamos llegadas estimadas (Solo para usarlas si va al centro)
        llegada_central = calcular_llegada(hora_real, 23)
        llegada_soder = calcular_llegada(hora_real, 36)

        info_tren = {
            "Hora": display_hora,
            "Destino": destino,
            "Color": color,
            "LlegadaTC": llegada_central,
            "LlegadaSoder": llegada_soder,
            "Original": hora_prog # Guardamos la original por si queremos comparar
        }

        # Clasificación
        if "Kungsträdgården" in destino or "T-Centralen" in destino:
            hacia_ciudad.append(info_tren)
        else:
            hacia_norte.append(info_tren)

    # --- 2. LA GUILLOTINA (Solo los primeros 3) ---
    hacia_ciudad = hacia_ciudad[:3]
    hacia_norte = hacia_norte[:3]

    # --- MOSTRAR COLUMNAS ---
    col1, col2 = st.columns(2)

    # COLUMNA 1: AL CENTRO (Con cálculos)
    with col1:
        st.subheader("⬇️ Al Centro")
        if not hacia_ciudad:
            st.info("Sin trenes.")
        
        for t in hacia_ciudad:
            with st.container(border=True):
                # Encabezado Grande: HORA y DESTINO
                st.markdown(f"### :{t['Color']}[{t['Hora']}]  → {t['Destino']}")
                
                # 3. CALCULADORA DEL FUTURO
                st.markdown(f"""
                <div style="font-size: 14px; color: #bbb; margin-top: -10px;">
                🏁 T-Centralen: <b>{t['LlegadaTC']}</b><br>
                🍻 Söder: <b>{t['LlegadaSoder']}</b>
                </div>
                """, unsafe_allow_html=True)

    # COLUMNA 2: AL NORTE (Normalita)
    with col2:
        st.subheader("⬆️ Hacia Akalla")
        if not hacia_norte:
            st.info("Sin trenes.")
        
        for t in hacia_norte:
            with st.container(border=True):
                st.markdown(f"### :{t['Color']}[{t['Hora']}] → {t['Destino']}")
                st.caption("Dirección Kista / Akalla")