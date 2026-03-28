import os
import json
import plotly.graph_objects as go

# ==========================================
# Explicación de Pensamiento Secuencial
# ==========================================
print("\n[Pensamiento Secuencial] Configuración de UI/UX interactiva:")
print("1. Eje X con saltos de 1 año: Utilizaremos 'tickmode=\"linear\"' y 'dtick=1' en 'fig.update_xaxes()'. Esto fuerza a Plotly a no agrupar las edades (ej: mostrar 49, 50, 51 explícitamente sin decimales ni saltos de a 2).")
print("2. Responsividad Absoluta: Al exportar de gráfica a HTML, no hardcodearemos width/height absolutos en layout, y dejaremos que Plotly genere el archivo con ancho 100%, de forma nativa. Esto permite que el HTML se adapte a cualquier pantalla móvil o de escritorio.\n")

def create_visualization(clean_data_path, financial_data_path, output_html_path):
    print("-> Leyendo datos financieros...")
    with open(clean_data_path, 'r', encoding='utf-8') as f:
        clean_data = json.load(f)
        
    with open(financial_data_path, 'r', encoding='utf-8') as f:
        fin_data = json.load(f)
        
    cliente_nombre = clean_data["Cliente"]["Nombre"]
    resultados = fin_data["Resultados_Anuales"]
    resumen = fin_data["Resumen"]
    
    # Extraer datos para el eje X y ejes Y
    edades = [r["Edad"] for r in resultados]
    anios = [r["Año"] for r in resultados]
    rescates = [r["Valor_Rescate_Optimista"] for r in resultados]
    invertido = [r["Acumulado_Invertido"] for r in resultados]
    
    # Crear la figura (Plotly)
    fig = go.Figure()
    
    # 1. Área de Capital Proyectado (Valor Rescate)
    fig.add_trace(go.Scatter(
        x=edades, 
        y=rescates,
        fill='tozeroy',
        fillcolor='rgba(0, 102, 204, 0.1)', # Soft fill
        mode='lines',
        name='Capital Proyectado',
        line=dict(color='#0066CC', width=4), # Apple Blue
        hovertemplate="<b>%{y:,.0f} VRU$S</b> a los %{x} años<extra></extra>"
    ))
    
    # 2. Línea de Inversión Acumulada
    fig.add_trace(go.Scatter(
        x=edades,
        y=invertido,
        mode='lines',
        name='Acumulado Invertido',
        line=dict(color='#86868B', width=2.5, dash='dash'), # Apple Silver/Gray
        hovertemplate="%{y:,.0f} VRU$S invertidos (Edad %{x})<extra></extra>"
    ))
    
    # Buscar punto de Break-Even
    anio_break = resumen.get("Anio_Break_Even")
    if anio_break:
        # Encontrar edad correspondiente al break-even
        idx = next((i for i, r in enumerate(resultados) if r["Año"] == anio_break), None)
        if idx is not None:
            edad_be = edades[idx]
            rescate_be = rescates[idx]
            
            # Apple-style Break-Even Annotation
            fig.add_trace(go.Scatter(
                x=[edad_be],
                y=[rescate_be],
                mode='markers',
                name='Punto de Equilibrio',
                marker=dict(
                    size=14,
                    color='#0066CC',
                    line=dict(color='white', width=3),
                    symbol='circle'
                ),
                hoverinfo='skip',
                showlegend=False
            ))
            
            # Floating Annotation Box
            fig.add_annotation(
                x=edad_be,
                y=rescate_be,
                text=f"<b>Punto de Equilibrio</b><br>~{edad_be} años",
                showarrow=False,
                yshift=35,
                bgcolor="rgba(255, 255, 255, 0.95)",
                bordercolor="#E5E5EA",
                borderwidth=1,
                borderpad=8,
                font=dict(family="Inter, sans-serif", size=12, color="#1D1D1F")
            )
            
    # Configurar Ejes y Estética (Apple)
    fig.update_layout(
        title=dict(text=""), # Title handled in Streamlit / Snapshot sin bug undefined
        xaxis_title="Edad",
        yaxis_title="",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(245, 245, 247, 0.8)",
            bordercolor="#E5E5EA",
            borderwidth=1,
            font=dict(family="Inter, sans-serif", size=12, color="#515154")
        ),
        template="none",
        plot_bgcolor="#F5F5F7",
        paper_bgcolor="#F5F5F7",
        margin=dict(l=40, r=40, t=40, b=80),
        hovermode="x unified",
        font=dict(family="Inter, sans-serif", color="#1D1D1F")
    )
    
    fig.update_xaxes(
        tickmode='linear',
        dtick=5, # Saltos de 5 años
        showgrid=False,
        zeroline=False,
        showline=False,
        tickfont=dict(color="#86868B")
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridcolor='#E5E5EA',
        zeroline=False,
        showline=False,
        tickformat="$.0s", # Formato $25k
        tickfont=dict(color="#86868B")
    )
    
    # 4. Exportar a HTML responsivo (Sequential Thinking)
    # responsive=True no es un flag en write_html, el div interno ocupa 100% de la ventana si no hay size hardcodeado.
    fig.write_html(
        output_html_path,
        include_plotlyjs="cdn", # Pesa menos, lo carga de CDN web
        full_html=True,
        default_width="100%",
        default_height="100%"
    )
    
    print(f"✅ Visualización generada exitosamente.")
    print(f"-> Archivo guardado en: {output_html_path}")
    
    return fig

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    clean_data_file = os.path.join(project_root, "data", "data_clean.json")
    fin_data_file = os.path.join(project_root, "data", "financial_results.json")
    output_html = os.path.join(current_dir, "visualizacion_interactiva.html")
    
    create_visualization(clean_data_file, fin_data_file, output_html)
