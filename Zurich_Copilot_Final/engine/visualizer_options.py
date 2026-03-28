import json
import plotly.graph_objects as go
import os

def create_options_visualization(json_data_path, output_html_path=None):
    with open(json_data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    cliente_nombre = data["Cliente"]["Nombre"]
    proyecciones = data["Proyeccion"]
    
    edades = [p["Edad"] for p in proyecciones]
    seguros = [p["Seguro_Vida"] for p in proyecciones]
    cuentas = [p["Cuenta_Individual"] for p in proyecciones]
    
    fig = go.Figure()
    
    # Serie B: Cuenta Individual (Valor Cuenta) - Sólida con Gradient Fill
    fig.add_trace(go.Scatter(
        x=edades,
        y=cuentas,
        fill='tozeroy',
        fillcolor='rgba(0, 102, 204, 0.1)', # Gradient simulado
        mode='lines',
        name='Cuenta Individual',
        line=dict(color='#0066CC', width=4), # Apple Blue
        hovertemplate="<b>%{y:,.0f} VRU$S</b> Cuenta Individual<br>Edad %{x}<extra></extra>"
    ))
    
    # Serie A: Seguro de Vida (Línea Punteada Gris Arriba)
    fig.add_trace(go.Scatter(
        x=edades,
        y=seguros,
        mode='lines',
        name='Seguro de Vida (Resguardo)',
        line=dict(color='#86868B', width=2.5, dash='dash'), # Apple Silver/Gray
        hovertemplate="<b>%{y:,.0f} VRU$S</b> Seguro Vida<br>Edad %{x}<extra></extra>"
    ))
    
    # Configurar Ejes y Estética (Apple)
    fig.update_layout(
        title=dict(text=""), 
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
        dtick=5,
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
    
    if output_html_path:
        fig.write_html(
            output_html_path,
            include_plotlyjs="cdn",
            full_html=True,
            default_width="100%",
            default_height="100%"
        )
        
    return fig
