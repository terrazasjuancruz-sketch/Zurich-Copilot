import os
from fpdf import FPDF

class PDFReport(FPDF):
    def header(self):
        # Logo placeholder (can be text if we don't have image paths)
        self.set_font("helvetica", "B", 18)
        self.set_text_color(0, 51, 160) # Zurich Blue ish
        self.cell(0, 10, "Zurich Copilot - Análisis Financiero", border=0, ln=1, align="C")
        self.ln(5)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

def generate_report(clean_data, fin_data, output_path):
    pdf = PDFReport()
    pdf.add_page()
    
    # Extraer Datos
    nombre = clean_data["Cliente"]["Nombre"]
    edad = clean_data["Cliente"]["Edad"]
    producto = clean_data["Producto"]["Nombre"]
    prima = clean_data["Inversion"]["Prima_Regular"]
    incremento = clean_data["Inversion"]["Incremento_Automatico"]
    tc_ref = clean_data["Inversion"]["Tipo_Cambio_Referencia"]
    
    resumen = fin_data["Resumen"]
    tir = resumen["TIR_Final_Porcentaje"]
    break_even = resumen["Anio_Break_Even"]
    capital_final = fin_data["Resultados_Anuales"][-1]["Valor_Rescate_Optimista"]
    
    # Titulo Principal
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 10, f"Resumen Ejecutivo para {nombre}", ln=1)
    
    # Ficha Técnica
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(45, 8, "Producto", border=1, fill=True)
    pdf.cell(45, 8, "Edad Proyectada", border=1, fill=True)
    pdf.cell(50, 8, "Plan Incremento", border=1, fill=True)
    pdf.cell(50, 8, "V.R.U$S Inicial", border=1, fill=True, ln=1)
    
    pdf.set_font("helvetica", "", 10)
    pdf.cell(45, 8, str(producto), border=1)
    pdf.cell(45, 8, f"{edad} años", border=1)
    pdf.cell(50, 8, str(incremento), border=1)
    pdf.cell(50, 8, str(tc_ref), border=1, ln=1)
    
    pdf.ln(10)
    
    # KPIs
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(0, 31, 63) # Navy blue
    pdf.cell(0, 10, "Métricas Clave del Proyecto", ln=1)
    
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"- Tasa Interna de Retorno (TIR) Anualizada: {tir}%", ln=1)
    pdf.cell(0, 8, f"- Año de Recuperación (Break-Even): Año {break_even}", ln=1)
    pdf.cell(0, 8, f"- Capital Final Proyectado (Año 16): VRU$S {capital_final:,.2f}", ln=1)
    
    pdf.ln(10)
    
    # El Valor Refugio
    pdf.set_fill_color(230, 245, 255) # Soft Blue
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, "Importancia del VRU$S como Valor Refugio", ln=1, fill=True)
    pdf.set_font("helvetica", "", 10)
    txt_vrus = "El VRU$S es un componente estructural diseñado para proteger los aportes frente a la devaluación. Resguarda de manera sólida el poder adquisitivo en el largo plazo, permitiendo proyectar con certidumbre sin el riesgo sistémico de las monedas puramente fíat."
    pdf.multi_cell(0, 6, txt_vrus, border=1)
    
    # We could theoretically include the chart image here by saving it to disk first, 
    # but for a quick automated PDF, text summary works identically and robustly.

    pdf.output(output_path)
    return output_path
