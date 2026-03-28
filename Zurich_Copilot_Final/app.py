import os
# Crear directorios obligatorios
os.makedirs("data", exist_ok=True)
os.makedirs("engine", exist_ok=True)

import json
import streamlit as st
import importlib
import pdfplumber

st.cache_data.clear()
st.cache_resource.clear()

# Ensure the app can find the engine modules
from engine import extractor, finances, visualizer, snapshot_generator, extractor_options, visualizer_options

# ==========================================
# Configuración Premium de la Página
# ==========================================
st.set_page_config(
    page_title="Zurich Copilot - Análisis Financiero",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Personalizados para limpiar la interfaz y darle look premium
st.markdown("""
<style>
    /* Zurich Blue: #0033A0 */
    .stApp {
        background-color: #FAFAFA;
    }
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        color: #1D1D1F;
        margin-bottom: 0px;
        letter-spacing: -0.02em;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 400;
        color: #86868B;
        margin-bottom: 30px;
    }
    .metric-card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.02);
        border: 1px solid #E5E5EA;
        text-align: center;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1D1D1F;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #86868B;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .ficha-box {
        background-color: transparent;
        border-radius: 8px;
        padding: 15px 0px;
        margin-bottom: 20px;
        border-left: 3px solid #0066CC;
        padding-left: 15px;
    }
    .ficha-title {
        font-size: 0.8rem;
        color: #86868B;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .ficha-value {
        font-size: 1.2rem;
        color: #1D1D1F;
        font-weight: 600;
    }
    .apple-footnote {
        font-size: 0.85rem;
        color: #86868B;
        text-align: center;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #E5E5EA;
    }
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# Funciones Auxiliares
# ==========================================
def save_uploaded_file(uploaded_file):
    # Crear directorio si no existe
    os.makedirs("data", exist_ok=True)
    temp_path = os.path.join("data", "uploaded_temp.pdf")
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return temp_path

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

@st.cache_data
def detect_product_type(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) > 0:
                text = pdf.pages[0].extract_text()
                if not text:
                    return "Desconocido"
                
                # Búsqueda infalible por huellas digitales de tasas de rendimiento
                if "4.00%" in text or "4,00%" in text:
                    return "Invest Future"
                    
                if "5.15%" in text or "5,15%" in text:
                    return "Options"
                    
                return "Desconocido"
    except Exception as e:
        print(f"Error detectando producto: {e}")
    return "Desconocido"

# ==========================================
# Interfaz de Usuario (Sidebar)
# ==========================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Zurich_Insurance_Group_logo.svg/200px-Zurich_Insurance_Group_logo.svg.png", width=150)
    st.markdown("## ⚙️ Zurich Copilot")
    st.markdown("Sube la proyección PDF de tu cliente para generar el análisis financiero interactivo.")
    
    uploaded_file = st.file_uploader("Arrastra el PDF aquí", type="pdf")
    
    st.markdown("---")
    st.markdown("### 📘 Guía del Asesor")
    st.write("1. Selecciona el archivo PDF de la proyección.")
    st.write("2. Arrástralo a la zona de carga superior.")
    st.write("3. Copilot detectará automáticamente si es Invest Future u Options.")
    st.write("4. Descarga la Infografía Final y envíasela al cliente.")
    
    st.markdown("---")
    modo_seleccion = st.radio(
        "Selección de Producto:",
        options=["Auto-detectar", "Zurich Invest Future", "Zurich Options"],
        index=0
    )
        
    st.markdown("---")
    st.caption("Zurich Copilot v1.0 | Diseñado para Life Planners")

# ==========================================
# Lógica Principal (Main Body)
# ==========================================
if uploaded_file is not None:
    # Limpieza de caché por cambio de archivo
    if "last_uploaded_file" not in st.session_state or st.session_state.last_uploaded_file != uploaded_file.name:
        st.cache_data.clear()
        st.session_state.last_uploaded_file = uploaded_file.name

    # 1. Guardar y Procesar
    with st.spinner("Extrayendo inteligencia matemática y calculando métricas..."):
        # --- LIMPIEZA DE DISCO REAL ---
        import shutil
        if os.path.exists("data"):
            shutil.rmtree("data", ignore_errors=True)
        os.makedirs("data", exist_ok=True)
        
        # Guardar en memoria limpia (restauramos el nombre temporal)
        pdf_path = os.path.join("data", "uploaded_temp.pdf")
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # 2. Detección Inteligente de Producto o Bypass Manual
        if modo_seleccion != "Auto-detectar":
            producto_tipo = "Invest Future" if modo_seleccion == "Zurich Invest Future" else "Options"
        else:
            producto_tipo = detect_product_type(pdf_path)
        
        if producto_tipo == "Desconocido":
            st.warning("Si el sistema no reconoce el archivo, por favor selecciónalo manualmente en la barra lateral.")
            st.stop()
            
        clean_json_path = os.path.join("data", "invest_data.json")
        financial_json_path = os.path.join("data", "invest_financial.json")
        html_out_path = os.path.join("engine", "visualizacion_interactiva.html")
        
        # --- AISLAMIENTO TOTAL DE MOTORES ---
        if producto_tipo == "Invest Future":
            # Aislar motor original de Invest Future que calcula TIR 5.18%
            try:
                extractor.extract_data(pdf_path, clean_json_path)
            except Exception as e:
                st.error(f"Error técnico exacto en extractor.py:\n{str(e)}")
                st.stop()
                
            # Forzar extracción si el archivo está vacío (menos de 50 bytes)
            if not os.path.exists(clean_json_path) or os.path.getsize(clean_json_path) < 50:
                try:
                    extractor.extract_data(pdf_path, clean_json_path)
                except Exception:
                    pass
                    
                if not os.path.exists(clean_json_path) or os.path.getsize(clean_json_path) < 50:
                    st.warning("El archivo de datos está vacío o no se generó. El PDF podría no contener la tabla esperada.")
                    st.stop()
                
            try:
                finances.process_finances(clean_json_path, financial_json_path)
            except Exception as e:
                import traceback
                st.error(f"Error crítico procesando motor financiero:\n{str(e)}")
                st.code(traceback.format_exc())
                st.stop()
                
            if os.path.exists(clean_json_path) and os.path.exists(financial_json_path):
                fig = visualizer.create_visualization(clean_json_path, financial_json_path, html_out_path)
                # Cargar resultados
                datos_cliente = load_json(clean_json_path)
                datos_finanzas = load_json(financial_json_path)
            else:
                st.warning("No se pudo calcular la tabla final. Reintente.")
                st.stop()
            
        elif producto_tipo == "Options":
            try:
                # Aislar motor Options
                options_json_path = os.path.join("data", "options_data.json")
                extractor_options.extract_options_data(pdf_path, options_json_path)
                
                if not os.path.exists(options_json_path):
                    st.warning("Procesando datos del PDF... por favor espera.")
                    st.stop()
                    
                fig = visualizer_options.create_options_visualization(options_json_path, html_out_path)
                
                datos_cliente = load_json(options_json_path)
                datos_finanzas = None
            except Exception as exp:
                st.error(f"Error procesando Seguro: {exp}")
                st.stop()

    if datos_cliente:
        nombre = datos_cliente["Cliente"].get("Nombre", "Desconocido")
        edad = datos_cliente["Cliente"].get("Edad", 0)
        producto = datos_cliente["Producto"]["Nombre"]
        
        # Render Encabezado (Igual para todos)
        st.markdown(f"<div class='main-header'>Su Capital. Su Crecimiento.</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='sub-header'>Trayectoria de inversión y valor acumulado.</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Branch de UI por Producto
        if producto_tipo == "Invest Future" and datos_finanzas:
            incremento = datos_cliente["Inversion"]["Incremento_Automatico"]
            tc_ref = datos_cliente["Inversion"]["Tipo_Cambio_Referencia"]
            
            resumen = datos_finanzas["Resumen"]
            tir = resumen["TIR_Final_Porcentaje"]
            break_even = resumen["Anio_Break_Even"]
            
            ultimo_anio = datos_finanzas["Resultados_Anuales"][-1]
            capital_final = ultimo_anio["Valor_Rescate_Optimista"]
            
            st.markdown("### 📋 Ficha Técnica")
            f1, f2, f3, f4, f5 = st.columns(5)
            with f1:
                st.markdown(f"<div class='ficha-box'><div class='ficha-title'>Producto</div><div class='ficha-value'>{producto}</div></div>", unsafe_allow_html=True)
            with f2:
                aporte_num = datos_cliente["Inversion"].get("Aporte_Mensual", 0)
                if aporte_num is None:
                    aporte_num = 0.0
                aporte_str = f"{aporte_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                st.markdown(f"<div class='ficha-box' style='background-color:#EBF5FF; border:1px solid #0066CC;'><div class='ficha-title' style='color:#0066CC;'><b>Aporte Mensual</b></div><div class='ficha-value'>VRU$S {aporte_str}</div></div>", unsafe_allow_html=True)
            with f3:
                st.markdown(f"<div class='ficha-box'><div class='ficha-title'>Edad Actual</div><div class='ficha-value'>{edad} años</div></div>", unsafe_allow_html=True)
            with f4:
                st.markdown(f"<div class='ficha-box'><div class='ficha-title'>Plan de Incrementos</div><div class='ficha-value'>{incremento} Anual (Primeros 5 años)</div></div>", unsafe_allow_html=True)
            with f5:
                st.markdown(f"<div class='ficha-box'><div class='ficha-title'>V.R.U$S Inicial</div><div class='ficha-value'>{tc_ref}</div></div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>TIR Anualizada (16 años)</div><div class='metric-value'>{tir}%</div></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>Año Break-Even</div><div class='metric-value'>Año {break_even}</div></div>", unsafe_allow_html=True)
            with col3:
                cap_frmt = f"{capital_final:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                st.markdown(f"<div class='metric-card'><div class='metric-label'>Capital Proyectado Final</div><div class='metric-value'>VRU$S {cap_frmt}</div></div>", unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            <div class='apple-footnote'>
                <b>Moneda de Refugio (VRU$S)</b><br>
                El VRU$S es un componente estructural diseñado para proteger estructuralmente el capital contra la devaluación sistémica del dinero fíat, garantizando la preservación del poder adquisitivo en el largo plazo.
            </div>
            """, unsafe_allow_html=True)
            
        elif producto_tipo == "Options":
            # UI branch for Zurich Options
            proteccion = datos_cliente["Proteccion"]
            s_basico = proteccion["Seguro_Basico"]
            s_adic = proteccion["Seguro_Adicional"]
            s_total = proteccion["Suma_Asegurada_Total"]
            riders = proteccion["Riders"]
            
            st.markdown("### 📋 Ficha de Escalera de Protección")
            f1, f2, f3, f4, f5 = st.columns(5)
            with f1:
                st.markdown(f"<div class='ficha-box'><div class='ficha-title'>Producto</div><div class='ficha-value'>{producto}</div></div>", unsafe_allow_html=True)
            with f2:
                aporte_num = datos_cliente.get("Inversion", {}).get("Aporte_Mensual", 0)
                if aporte_num is None:
                    aporte_num = 0.0
                aporte_str = f"{aporte_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                st.markdown(f"<div class='ficha-box' style='background-color:#EBF5FF; border:1px solid #0066CC;'><div class='ficha-title' style='color:#0066CC;'><b>Aporte Mensual</b></div><div class='ficha-value'>$ {aporte_str}</div></div>", unsafe_allow_html=True)
            with f3:
                st.markdown(f"<div class='ficha-box'><div class='ficha-title'>Cliente (Edad)</div><div class='ficha-value'>{nombre} ({edad})</div></div>", unsafe_allow_html=True)
            with f4:
                riders_text = "N/A"
                if riders:
                    riders_text = riders[0]["Nombre"]
                st.markdown(f"<div class='ficha-box'><div class='ficha-title'>Rider Principal</div><div class='ficha-value'>{riders_text}</div></div>", unsafe_allow_html=True)
            with f5:
                tc_ref = datos_cliente.get("Inversion", {}).get("Tipo_Cambio_Referencia", "$0,00")
                st.markdown(f"<div class='ficha-box'><div class='ficha-title'>V.R.U$S Inicial</div><div class='ficha-value'>{tc_ref}</div></div>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                s_basico_str = f"{s_basico:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                st.markdown(f"<div class='metric-card'><div class='metric-label'>Seguro Básico</div><div class='metric-value'>${s_basico_str}</div></div>", unsafe_allow_html=True)
            with col2:
                s_adic_str = f"{s_adic:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                st.markdown(f"<div class='metric-card'><div class='metric-label'>Seguro Adicional</div><div class='metric-value'>${s_adic_str}</div></div>", unsafe_allow_html=True)
            with col3:
                s_total_str = f"{s_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                st.markdown(f"<div class='metric-card' style='border-top: 4px solid #86868B;'><div class='metric-label'>Suma Asegurada Total</div><div class='metric-value'>${s_total_str}</div></div>", unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            <div class='apple-footnote'>
                <b>Fondo Options (VRU$S)</b><br>
                Análisis conceptual de Escalera de Protección frente a la Cuenta Individual garantizando la preservación patrimonial.
            </div>
            """, unsafe_allow_html=True)

        # ==========================================
        # Descargar PNG Snapshot (Universal)
        # ==========================================
        st.markdown("<br><br>", unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
        with col_btn2:
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            base_png_path = os.path.join("engine", "Snapshot_App.png")
            # Inyectamos el producto_tipo para que el generator sepa cual renderizar
            report_png_path = snapshot_generator.generate_snapshot(
                clean_json_path if producto_tipo == "Invest Future" else options_json_path, 
                financial_json_path if producto_tipo == "Invest Future" else None, 
                base_png_path,
                producto_tipo=producto_tipo
            )
            
            if report_png_path and os.path.exists(report_png_path):
                with open(report_png_path, "rb") as png_file:
                    st.download_button(
                        label="📸 Descargar Resumen Ejecutivo (PNG)",
                        data=png_file,
                        file_name=os.path.basename(report_png_path),
                        mime="image/png",
                        type="primary",
                        use_container_width=True
                    )
            st.markdown("</div>", unsafe_allow_html=True)

else:
    # Estado inicial / vacío
    st.markdown("<div class='main-header'>Bienvenido a Zurich Copilot</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Por favor, sube un PDF de proyección desde el panel lateral izquierdo.</div>", unsafe_allow_html=True)
    
    st.info("👈 Esperando archivo...")
