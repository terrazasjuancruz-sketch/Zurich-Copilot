import os
import plotly.graph_objects as go
from engine import visualizer, visualizer_options

def generate_snapshot(clean_data_path, financial_data_path, output_png_path, producto_tipo="Invest Future"):
    print(f"-> Generando Snapshot High-Res (PNG) para {producto_tipo}...")
    
    import json
    with open(clean_data_path, 'r', encoding='utf-8') as f:
        datos_cliente = json.load(f)
        
    nombre = datos_cliente["Cliente"].get("Nombre", "Desconocido")
    producto = datos_cliente["Producto"].get("Nombre", producto_tipo)
    
    if producto_tipo == "Invest Future":
        fig = visualizer.create_visualization(clean_data_path, financial_data_path, "/tmp/dummy.html")
        with open(financial_data_path, 'r', encoding='utf-8') as f:
            datos_finanzas = json.load(f)
            
        tir = datos_finanzas["Resumen"]["TIR_Final_Porcentaje"]
        break_even = datos_finanzas["Resumen"]["Anio_Break_Even"]
        
        m1_t = "TIR ANUALIZADA"
        m1_v = f"{tir}%"
        m2_t = "PUNTO DE EQUILIBRIO"
        m2_v = f"Año {break_even}"
    else:
        fig = visualizer_options.create_options_visualization(clean_data_path, "/tmp/dummy.html")
        
        s_total = datos_cliente["Proteccion"]["Suma_Asegurada_Total"]
        riders = datos_cliente["Proteccion"]["Riders"]
        rider_val = riders[0]["Nombre"] if riders else "N/A"
        
        m1_t = "SUMA ASEGURADA TOTAL"
        m1_v = f"${s_total:,.0f}"
        m2_t = "COBERTURA ADICIONAL"
        m2_v = rider_val
    
    # 1. Configurar un Lienzo Vertical (Infografía)
    fig.update_layout(
        title=None, # Desactivamos el título nativo para el infográfico custom
        margin=dict(l=60, r=60, t=320, b=80), # Margen superior enorme para el Header
        width=1000,
        height=1400, # Vertical
        paper_bgcolor="#F5F5F7",
        plot_bgcolor="#F5F5F7"
    )
    
    # 2. Construir el Cuadro del Encabezado (Tarjeta Premium en la Infografía)
    fig.add_shape(
        type="rect",
        xref="paper", yref="paper",
        x0=-0.02, y0=1.1, x1=1.02, y1=1.35, # Caja posicionada sobre el gráfico
        fillcolor="white",
        line=dict(color="#E5E5EA", width=2),
        layer="below"
    )
    
    # Título Principal Infografía
    fig.add_annotation(
        xref="paper", yref="paper", x=0, y=1.32,
        text="<b>Resumen Ejecutivo de Inversión</b>",
        showarrow=False, xanchor="left", yanchor="top",
        font=dict(family="Inter, sans-serif", size=32, color="#1D1D1F")
    )
    
    # Datos de Cliente y Producto
    fig.add_annotation(
        xref="paper", yref="paper", x=0, y=1.24,
        text=f"<span style='color:#86868B; font-size:16px;'>CLIENTE</span><br><b>{nombre}</b>",
        showarrow=False, xanchor="left", yanchor="top",
        font=dict(family="Inter, sans-serif", size=22, color="#1D1D1F")
    )
    
    fig.add_annotation(
        xref="paper", yref="paper", x=0.5, y=1.24,
        text=f"<span style='color:#86868B; font-size:16px;'>PRODUCTO</span><br><b>{producto}</b>",
        showarrow=False, xanchor="left", yanchor="top",
        font=dict(family="Inter, sans-serif", size=22, color="#1D1D1F")
    )
    
    # Métricas Clave (Modificables según producto)
    fig.add_annotation(
        xref="paper", yref="paper", x=0, y=1.15,
        text=f"<span style='color:#0066CC; font-size:16px;'>{m1_t}</span><br><b>{m1_v}</b>",
        showarrow=False, xanchor="left", yanchor="top",
        font=dict(family="Inter, sans-serif", size=26, color="#1D1D1F")
    )
    
    fig.add_annotation(
        xref="paper", yref="paper", x=0.5, y=1.15,
        text=f"<span style='color:#0066CC; font-size:16px;'>{m2_t}</span><br><b>{m2_v}</b>",
        showarrow=False, xanchor="left", yanchor="top",
        font=dict(family="Inter, sans-serif", size=26, color="#1D1D1F")
    )
    
    import re
    # Aseguramos un path corto y absoluto
    final_png_path = os.path.abspath("temp_report.png")
    
    # Escribir imagen usando Kaleido
    try:
        # Metadato de título simple para prevenir [Errno 63] File name too long
        fig.update_layout(title_text='Reporte Financiero')
        fig.write_image(final_png_path, scale=2, engine="kaleido") # Scale 2 = Retina Display 
        print(f"✅ Infografía PNG generada exitosamente en: {final_png_path}")
        return final_png_path
    except ValueError as e:
        print(f"❌ Error Exportando Imagen: {e}")
        return None
