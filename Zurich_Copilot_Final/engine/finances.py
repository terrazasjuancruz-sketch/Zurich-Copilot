import json
import os
import re
import numpy_financial as npf

# ==========================================
# Explicación de Pensamiento Secuencial
# ==========================================
"""
PENSAMIENTO SECUENCIAL - CÁLCULO DE TIR (IRR)
Para calcular una TIR exacta dada la frecuencia dispar entre aportes (mensuales) y el valor
de rescate informado (anual al final del año 16):

1. Array de Flujo de Caja Mensual: Generaremos un array de 192 meses (16 años * 12).
2. Aportes (-): Cada mes insertaremos el flujo negativo mensual (sabiendo que la prima incrementa 5% 
   al inicio de los años 2 al 5, y luego se fija).
3. Rescate (+): En el último mes (mes 192), al flujo negativo de ese mes le sumaremos el
   Valor de Rescate Optimista del año 16.
4. Tasa Mensual vs Anual: Calcularemos la TIR mensual usando numpy-financial.irr(flujo). Luego la 
   anualizaremos con la fórmula de interés compuesto: ((1 + TIR_mensual)**12) - 1.
Esto evita la distorsión de asumir que todas las primas se pagan al final del año.
"""

def process_finances(input_path, output_path):
    print("\n[Pensamiento Secuencial] Iniciando cálculos financieros.")
    print("-> Construyendo flujo mensual para respetar el valor temporal del dinero de aportes mensuales contra el rescate en el año 16.\n")

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Extract initial values
        prima_text = data["Inversion"]["Prima_Regular"]
        # extract numeric from "VRU$S 310,00"
        prima_inicial = float(re.search(r'(\d+[.,]\d+)', prima_text).group(1).replace(',', '.'))
        
        inc_str = data["Inversion"]["Incremento_Automatico"]
        increment_rate = float(inc_str.replace('%', '').replace(',', '.')) / 100.0 if '%' in inc_str else 0.05
        
        escenarios = data["Escenarios"]
        if not escenarios:
            raise ValueError("No hay datos de escenarios proyectados para analizar.")
            
        edad_base = data["Cliente"]["Edad"]
        
        financial_results = []
        acumulado_invertido = 0.0
        
        prima_mensual_actual = prima_inicial
        anio_break_even = None
        tir_final = 0.0
        
        # Flujo de caja para TIR (mes a mes)
        monthly_cash_flow = []
        
        # Nos enfocamos en los años disponibles (ej. 1 al 16)
        for esc in escenarios:
            anio = esc.get("Año", 0)
            edad_proy = esc.get("Edad_Proyectada", 0)
            
            # Buscar la llave correcta para el rescate
            rescate_key = None
            for key in ["Valor de Cuenta", "Cuenta Individual", "Escenario_Optimista", "Cuenta_Individual", "Valor_de_Cuenta"]:
                if key in esc:
                    rescate_key = key
                    break
                    
            if not rescate_key:
                print(f"Advertencia: Columnas encontradas en el JSON: {list(esc.keys())}")
                continue # Skip si no hay llave en vez de abortar
            
            # Limpiar valor de rescate optimista ignorando espacios y monedas
            rescate_str = str(esc.get(rescate_key, ""))
            if not rescate_str or rescate_str.strip() == "":
                continue
                
            clean_str = rescate_str.replace('$', '').replace('.', '').replace(',', '.').strip()
            
            try:
                rescate_val = float(clean_str)
            except ValueError:
                continue
            
            # Determinar Prima Mensual para este año
            if anio > 1 and anio <= 5:
                prima_mensual_actual *= (1 + increment_rate)
            # Año 6 en adelante, prima_mensual_actual se mantiene constante
            
            prima_anual = prima_mensual_actual * 12
            acumulado_invertido += prima_anual
            
            ganancia_neta = rescate_val - acumulado_invertido
            
            # Verificar Break-Even
            if anio_break_even is None and rescate_val >= acumulado_invertido:
                anio_break_even = anio
                
            financial_results.append({
                "Año": anio,
                "Edad": edad_proy,
                "Prima_Anual": round(prima_anual, 2),
                "Acumulado_Invertido": round(acumulado_invertido, 2),
                "Valor_Rescate_Optimista": round(rescate_val, 2),
                "Ganancia_Neta": round(ganancia_neta, 2)
            })
            
            # Construir Cash Flow Mensual para poder calcular TIR al final
            for mes in range(12):
                if anio == len(escenarios) and mes == 11:
                    # Último mes del flujo total: pago la prima y recibo el rescate
                    monthly_cash_flow.append(-prima_mensual_actual + rescate_val)
                else:
                    monthly_cash_flow.append(-prima_mensual_actual)
                    
        # Calcular TIR Final (al finalizar el último escenario disponible, ej. 16)
        try:
            tir_mensual = npf.irr(monthly_cash_flow)
            if not isinstance(tir_mensual, complex) and tir_mensual is not None:
                tir_anual = ((1 + tir_mensual) ** 12) - 1
                tir_final = round(tir_anual * 100, 2)
            else:
                tir_final = None
        except Exception as e:
            tir_final = f"Error: {e}"
            
        final_output = {
            "Resultados_Anuales": financial_results,
            "Resumen": {
                "TIR_Final_Porcentaje": tir_final,
                "Anio_Break_Even": anio_break_even
            }
        }
        
        # Save output
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=4, ensure_ascii=False)
            
        print("✅ Core Matemático Procesado.")
        print("=== REPORTE FINANCIERO: ZURICH COPILOT ===")
        print(f"-> Aportes: Inicial ${prima_inicial} | Incremento 5% primeros 5 años")
        print(f"-> Año Break-Even (Rescate >= Inversión): Año {anio_break_even if anio_break_even else 'No alcanzado en los escenarios previstos.'}")
        print(f"-> Tasa Interna de Retorno (TIR) Anualizada final: {tir_final}%")
        print("\n=== FLUJO RESUMIDO (Primeros 3 Años & Último Año) ===")
        if len(financial_results) > 0:
            for r in financial_results[:3]:
                print(f"Año {r['Año']} (Edad {r['Edad']}): Invertido Acum. ${r['Acumulado_Invertido']:.2f} | Rescate Estimado ${r['Valor_Rescate_Optimista']:.2f} | Neto: ${r['Ganancia_Neta']:.2f}")
            print("...")
            r_fin = financial_results[-1]
            print(f"Año {r_fin['Año']} (Edad {r_fin['Edad']}): Invertido Acum. ${r_fin['Acumulado_Invertido']:.2f} | Rescate Estimado ${r_fin['Valor_Rescate_Optimista']:.2f} | Neto: ${r_fin['Ganancia_Neta']:.2f}")
            
    except Exception as e:
        print(f"❌ Error durante cálculos matemáticos: {str(e)}")
        raise

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    input_json = os.path.join(project_root, "data", "data_clean.json")
    output_json = os.path.join(project_root, "data", "financial_results.json")
    
    process_finances(input_json, output_json)
