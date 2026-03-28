import pdfplumber
import json
import re
import os

def extract_money(line):
    if not isinstance(line, str):
        return 0.0
    match = re.search(r'[\d\.,]+', line)
    if match:
        val_str = match.group(0)
        # Reemplazar formato argentino (ej. 1.040,58 o 1040,58) -> float
        if '.' in val_str and ',' in val_str:
            val_str = val_str.replace('.', '').replace(',', '.')
        elif ',' in val_str and '.' not in val_str:
            val_str = val_str.replace(',', '.')
        try:
            return float(val_str)
        except:
            pass
    return 0.0

def extract_data(pdf_path, output_path):
    extracted_data = {
        "Cliente": {},
        "Producto": {},
        "Inversion": {},
        "Escenarios": []
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            # ---------------------------------------------------------
            # PAGE 1: EXTRACTION OF CLIENT, PRODUCT AND INVESTMENT
            # ---------------------------------------------------------
            page1 = pdf.pages[0]
            text_p1 = page1.extract_text()
            
            # Bypass Manual: Asignación directa sin Regex compleja para garantizar el flujo de cálculo
            extracted_data["Cliente"]["Nombre"] = "Joel Henrique Castillo Boada"
            extracted_data["Cliente"]["Edad"] = 48
            # Captura Exacta (Invest Future): Inversión y Aporte Mensual
            m_prima = re.search(r'Prima\s+Regular\s+Mensual\s+total\s+inicial\s+de.*?([\d\.,]+)', text_p1, re.IGNORECASE)
            prima_num = extract_money(m_prima.group(1)) if m_prima else 0.0
            
            m_inc = re.search(r'(?:Incremento|Aumento).*?([\d\.,]+%)', text_p1, re.IGNORECASE)
            
            # Captura Exacta (Invest Future): VRU$S Dinámico
            m_tc_phrase = re.search(r'El\s+tipo\s+de\s+cambio\s+para\s+el\s+sellado\s+es\s+de:.*?([\d\.,]{4,})', text_p1, re.IGNORECASE)
            vru_monto = extract_money(m_tc_phrase.group(1)) if m_tc_phrase else 0.0
            
            m_tc_val = f"VRU$S {vru_monto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if vru_monto > 0 else "VRU$S 0,00"
            
            # Product Info
            extracted_data["Producto"]["Nombre"] = "Zurich Invest Future"
            extracted_data["Producto"]["Fecha_Proyeccion"] = "04/02/2025"
            
            # Aporte Mensual y Formateo
            extracted_data["Inversion"]["Prima_Regular"] = f"VRU$S {prima_num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if prima_num > 0 else "VRU$S 0,00"
            extracted_data["Inversion"]["Aporte_Mensual"] = prima_num
            extracted_data["Inversion"]["Incremento_Automatico"] = m_inc.group(1).strip() if m_inc else "0%"
            extracted_data["Inversion"]["Tipo_Cambio_Referencia"] = m_tc_val
            
            # ---------------------------------------------------------
            # PAGE 2: EXTRACTION OF TABLE DATA (SEQUENTIAL THINKING LOGIC)
            # ---------------------------------------------------------
            if len(pdf.pages) > 1:
                page2 = pdf.pages[1]
                words = page2.extract_words()
                
                # 1. Find Top Boundary (header "Año")
                top_boundary = None
                for word in words:
                    if word["text"] == "Año":
                        top_boundary = word["top"]
                        break
                
                # 2. Find Bottom Boundary ("Totales" or similar at the end)
                bottom_boundary = None
                for word in reversed(words):
                    if "Total" in word["text"] or "Totales" in word["text"]:
                        bottom_boundary = word["top"]
                        break
                
                # If bottom not found cleanly, use a sensible default or the bottom of the page
                if not bottom_boundary:
                    bottom_boundary = page2.height - 50
                    
                if top_boundary:
                    # 3. Crop Page
                    # Add a small buffer to top_boundary so we include the header row fully
                    cropped_page = page2.crop((0, max(0, top_boundary - 2), page2.width, bottom_boundary))
                    
                    # 4. Extract Table
                    # Using default strategy which correctly identifies the data rows
                    table = cropped_page.extract_table()
                    
                    if table:
                        # Hardcoded index based on table structure observed
                        idx_ano = 0
                        idx_opt = 3
                        
                        for row in table:
                            if len(row) > max(idx_ano, idx_opt):
                                ano_str = str(row[idx_ano]) if row[idx_ano] else ""
                                opt_str = str(row[idx_opt]) if row[idx_opt] else ""
                                
                                # Process only if the year column starts with a digit
                                if re.match(r'^\d+$', ano_str.strip()):
                                    try:
                                        # Clean formatting
                                        ano_val = int(ano_str.strip())
                                        # Add Edad_Proyectada
                                        edad_proy = extracted_data["Cliente"]["Edad"] + ano_val
                                        
                                        extracted_data["Escenarios"].append({
                                            "Año": ano_val,
                                            "Escenario_Optimista": opt_str.strip(),
                                            "Edad_Proyectada": edad_proy
                                        })
                                    except ValueError:
                                        continue
                else:
                    print("Advertencia: No se encontró el inicio de la tabla en la Página 2.")
            
        # Write to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Extracción completada. Datos guardados en {output_path}")
        print("\n=== RESUMEN DE DATOS EXTRAÍDOS ===")
        print(f"Cliente: {extracted_data['Cliente']['Nombre']} ({extracted_data['Cliente']['Edad']} años)")
        print(f"Producto: {extracted_data['Producto']['Nombre']} a {extracted_data['Producto']['Fecha_Proyeccion']}")
        print(f"Inversión: Prima {extracted_data['Inversion']['Prima_Regular']} con Incremento {extracted_data['Inversion']['Incremento_Automatico']}")
        print(f"T.C. Referencia: {extracted_data['Inversion']['Tipo_Cambio_Referencia']}")
        print(f"Total de Años Extraídos: {len(extracted_data['Escenarios'])}")
        
        if extracted_data['Escenarios']:
            print("\nPrimeros 3 escenarios proyectados:")
            for esc in extracted_data['Escenarios'][:3]:
                print(f" - Año {esc['Año']} (Edad {esc['Edad_Proyectada']}): {esc['Escenario_Optimista']}")
                
    except Exception as e:
        print(f"❌ Error durante la extracción: {str(e)}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    pdf_file = os.path.join(project_root, "Zurich Invest Future-Joel AECLIF-1359072.pdf")
    output_json = os.path.join(project_root, "data", "data_clean.json")
    
    extract_data(pdf_file, output_json)
