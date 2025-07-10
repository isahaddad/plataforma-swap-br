import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image, ImageOps, ImageEnhance
import re
import math

st.set_page_config(layout="wide", page_title="Comparador de SWAPs", page_icon="🏦")
# Logo da BR Partners
st.image("br_logo.png", width=180)

st.markdown("""
    <style>
    /* Fundo geral */
    .stApp {
        background-color: #f9f9f9;
    }

    /* Fonte geral e cor de texto */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        color: #1e1e1e;
    }

    /* Títulos principais */
    h1, h2, h3, h4, h5, h6 {
        color: #002F6C !important;
        font-weight: 600;
    }

    /* Cabeçalho do selectbox e uploader */
    label {
        color: #002F6C !important;
        font-weight: 500;
    }

    /* Tabelas do st.dataframe */
    div[data-testid="stDataFrame"] {
        border: 1px solid #d3d3d3;
        border-radius: 8px;
        overflow: auto;
    }

    div[data-testid="stDataFrame"] thead {
        background-color: #f2f2f2;
        color: #1e1e1e;
        font-weight: bold;
    }

    div[data-testid="stDataFrame"] td {
        background-color: white;
        color: #1e1e1e;
        font-size: 14px;
    }

    /* Expanders e blocos */
    .streamlit-expanderHeader {
        color: #002F6C !important;
        font-weight: bold;
    }

    /* Botões, selects, uploaders */
    .stSelectbox, .stFileUploader, .stButton > button {
        margin-top: 10px;
        margin-bottom: 15px;
    }

    .block-container {
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Logo fixo no canto superior direito */
    .logo-container {
        position: absolute;
        top: 15px;
        right: 25px;
        z-index: 100;
    }
    </style>

    <div class="logo-container">
        <img src="br_logo.png" style="width: 180px;">
    </div>
""", unsafe_allow_html=True)

st.title('Comparador de SWAPs: Tesouraria BR Partners 🏦')

# Seleção do tipo de batimento
tipo_batimento = st.selectbox("🔀 Selecione o tipo de batimento:", ["Swap - Vencimento", "Accrual - Último dia útil"])

# ======================
# ACCRUAL - NOVO BLOCO
# ======================
if tipo_batimento == "Accrual - Último dia útil":
    st.subheader("📊 Batimento de Accrual")
    
    tes_file = st.file_uploader("📥 Upload Planilha da Tesouraria (aba mestre)", type="xlsx", key="tes")
    back_file = st.file_uploader("📥 Upload Planilha do BackOffice", type="xlsx", key="back")

    if tes_file and back_file:
        try:
            df_tes = pd.read_excel(tes_file, sheet_name=0)  # carrega a primeira aba, qualquer que seja o nome
            df_back = pd.read_excel(back_file, skiprows=3)

        # Limpeza
            df_tes.columns = df_tes.columns.str.strip()
            df_back.columns = df_back.columns.str.strip()
            df_tes["Contrato Extraído"] = df_tes["Contrato"].astype(str).str.extract(r'\((.*?)\)')

        # Padronização de datas
            df_tes["Data de vencimento"] = pd.to_datetime(df_tes["Data de vencimento"], errors="coerce").dt.date
            df_back["Data de Vencimento"] = pd.to_datetime(df_back["Data de Vencimento"], errors="coerce").dt.date

        # Funções auxiliares
            def parse_number(val):
                try:
                    val_str = str(val).replace("R$", "").replace(" ", "").strip()
                    if "," in val_str:
                        val_str = val_str.replace(".", "").replace(",", ".")
                    return float(val_str)
                except:
                  return None

            def format_currency(val):
                try:
                    return f"R$ {float(val):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                except:
                   return val

            resultados_dada = []
            resultados_tomada = []

            for _, back_row in df_back.iterrows():
                contrato = str(back_row.get("Contrato CETIP")).strip()
                tes_matches = df_tes[df_tes["Contrato Extraído"] == contrato]
                
                if tes_matches.empty:
                    continue

                tes_row = tes_matches.iloc[0]  # Considera o primeiro que bate a data

            # Comparar Ponta Dada
                val_back_dada = parse_number(back_row.get("Valor da Curva Over (252) Ponta Dada"))
                val_tes_dada = parse_number(tes_row.get("Valor da Curva Over (252) Ponta Dada"))
                status_dada = "✅ Batido" if val_back_dada and val_tes_dada and abs(val_back_dada - val_tes_dada) < 200 else "❌ Divergente"
                resultados_dada.append({
                    "Contrato": contrato,
                    "Cliente": back_row.get("Cliente"),
                    "Data Vencimento": back_row.get("Data de Vencimento"),
                    "Tesouraria": format_currency(val_tes_dada),
                    "BackOffice": format_currency(val_back_dada),
                    "Status": status_dada
                })

            # Comparar Ponta Tomada
                val_back_tomada = parse_number(back_row.get("Valor da Curva Over (252) Ponta Tomada"))
                val_tes_tomada = parse_number(tes_row.get("Valor da Curva Over (252) Ponta Tomada"))
                status_tomada = "✅ Batido" if val_back_tomada and val_tes_tomada and abs(val_back_tomada - val_tes_tomada) < 200 else "❌ Divergente"
                resultados_tomada.append({
                    "Contrato": contrato,
                    "Cliente": back_row.get("Cliente"),
                    "Data Vencimento": back_row.get("Data de Vencimento"),
                    "Tesouraria": format_currency(val_tes_tomada),
                    "BackOffice": format_currency(val_back_tomada),
                    "Status": status_tomada
                })

            st.subheader("📊 Comparação - Ponta Dada")
            st.dataframe(pd.DataFrame(resultados_dada),
                     use_container_width=True)


            st.subheader("📊 Comparação - Ponta Tomada")
            st.dataframe(pd.DataFrame(resultados_tomada),
                     use_container_width=True)


        except Exception as e:
            st.error(f"Erro ao processar os arquivos: {e}")

# ====================== 
# SWAP - VENCIMENTO 
# =====================
elif tipo_batimento == "Swap - Vencimento":
    st.subheader("📄 Batimento de Swap - Vencimento")

    uploaded_excel = st.file_uploader("📄 Faça upload da Planilha Mestre (.xlsx)", type=["xlsx"])
    uploaded_image = st.file_uploader("🖼️ Faça upload da Imagem do BackOffice (.png, .jpg)", type=["png", "jpg", "jpeg"])

    def preprocess_image(img):
        # Convert to grayscale
        img = ImageOps.grayscale(img)
        # Increase contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        # Optional: Increase sharpness
        enhancer_sharp = ImageEnhance.Sharpness(img)
        img = enhancer_sharp.enhance(1.5)
        # Upscale the image (important for Tesseract accuracy)
        width, height = img.size
        img = img.resize((width * 2, height * 2), Image.LANCZOS)
        return img

    def clean_number_planilha(num_str):
        if pd.isna(num_str) or num_str is None or num_str == '':
            return None

        if isinstance(num_str, (int, float)):
            return num_str

        num_str = str(num_str).strip()
        if not num_str:
            return None

        is_negative = False
        if num_str.startswith('-'):
            is_negative = True
            num_str = num_str[1:]
        elif num_str.startswith('(') and num_str.endswith(')'):
            is_negative = True
            num_str = num_str[1:-1]

        num_str = num_str.replace('R$', '').replace(' ', '').strip()

        if '%' in num_str:
            num_str = num_str.replace('%', '').replace(',', '.').strip()
            try:
                value = float(num_str) / 100.0
                return -value if is_negative else value
            except ValueError:
                return None

        clean_chars = re.sub(r'[^\d\.,]', '', num_str)
        has_comma = ',' in clean_chars
        has_period = '.' in clean_chars

        final_num_str = ""

        if has_comma and has_period:
            last_comma_idx = clean_chars.rfind(',')
            last_period_idx = clean_chars.rfind('.')

            if last_comma_idx > last_period_idx:
                final_num_str = clean_chars.replace('.', '').replace(',', '.')
            else:
                final_num_str = clean_chars.replace(',', '')
        elif has_comma:
            final_num_str = clean_chars.replace(',', '.')
        elif has_period:
            period_count = clean_chars.count('.')
            if period_count == 1:
                final_num_str = clean_chars
            elif period_count > 1 and re.search(r'\.\d{3}(\.|$)', clean_chars):
                final_num_str = clean_chars.replace('.', '')
            else:
                parts = clean_chars.split('.')
                final_num_str = parts[0] + '.' + ''.join(parts[1:])
        else:
            final_num_str = clean_chars

        final_num_str = re.sub(r'[^\d.]', '', final_num_str)

        try:
            value = float(final_num_str)
            return -value if is_negative else value
        except ValueError:
            return None
        except Exception:
            return None
        
    def extrair_valores_ocr(texto_ocr):
        campos = {
            'Ajuste bruto': r'Ajuste Bruto[:\s\-–]{1,2}\s*([-]?[\(]?R?\$?\s*[\d\.,]+[\)]?)',
            'Ajuste líquido': r'Ajuste [Ll][ií]quido[:\s\-–]*-?R?\$?\s*([-]?[\d\.,]+)',
            'Notional': r'Notional[:\s]*R?\$?\s*([-]?[\d\.,]+)',
            'Notional c/ correção': r'Not[i1l]nal\s*c[\/]?\s*corre[çc][aã][aão]*.*?R\$\s*([-]?[\d\.,]+)',
            'Parcela Pré': r'Parcela Pr[ée]?\s*[:\-]?\s*R?\$?\s*([-]?[\d\.,]+)',
            'Taxa Pré': r'Taxa Pr[ée][:\s]*R?\$?\s*([-]?[\d\.,%]+)',
            'Fator Pré': r'Fator Pr[ée]?[\s:]*([-]?[\d\.,]+)',
            'Parcela CDI': r'Parcela(?:s)? CDI[:\s]*R?\$?\s*([-]?[\d\.,]+)', 
            'Juros CDI': r'Juros CDI[:\s]*R?\$?\s*([-]?[\d\.,]+)',
            'Fator CDI': r'Fator CDI[:\s]*([-]?[\d\.,]+)',
            'Fator carrego': r'Fator carrego[:\s]*([-]?[\d\.,]+)',
            'IPCA Início': r'IPCA In[ií]cio[:\s]*R?\$?\s*([-]?[\d\.,]+)',
            'IPCA Fluxo': r'IPCA Fluxo[:\s]*R?\$?\s*([-]?[\d\.,]+)',
            'Parcela IPCA': r'Parcela IPCA[:\s]*R?\$?\s*([-]?[\d\.,]+)',
            'Juros IPCA': r'Juros IPCA[:\s]*R?\$?\s*([-]?[\d\.,]+)',
            'DU': r'DU[:\s]*([\d]+)',
            'Data de início': r'Data[ \-]?in[ií]cio[:\s]*(\d{1,2}[-/.\s][A-Za-z]{3,9}[-/.\s]\d{2,4}|\d{1,2}[/.]\d{1,2}[/.]\d{2,4})',
            'Data final': r'Data[ \-]?final[:\s]*(\d{1,2}[-/.\s][A-Za-z]{3,9}[-/.\s]\d{2,4}|\d{1,2}[/.]\d{1,2}[/.]\d{2,4})',
        }

        resultados = {}

        for campo, regex in campos.items():
            match = re.search(regex, texto_ocr, re.IGNORECASE)
            if match:
                valor_str = match.group(1).strip()

                if campo in ['Data de início', 'Data final']:
                    try:
                        valor_formatado = None
                        date_formats = [
                            '%d-%b-%y', '%d %b %y', 
                            '%d/%m/%Y', '%d/%m/%y', 
                            '%d.%m.%Y', '%d.%m.%y'  
                        ]
                        for fmt in date_formats:
                            try:
                                valor_formatado = pd.to_datetime(valor_str, format=fmt, errors='coerce')
                                if pd.notnull(valor_formatado):
                                    break
                            except ValueError:
                                continue
                        if pd.isna(valor_formatado):
                            valor_formatado = pd.to_datetime(valor_str, dayfirst=True, errors='coerce')

                        resultados[campo] = valor_formatado if pd.notnull(valor_formatado) else None
                    except Exception:
                        resultados[campo] = None
                elif campo == 'DU':
                    try:
                        cleaned_val = clean_number_planilha(valor_str)
                        if cleaned_val is not None:
                            resultados[campo] = int(cleaned_val)
                        else:
                            resultados[campo] = None
                    except ValueError:
                        resultados[campo] = None
                else:
                    resultados[campo] = clean_number_planilha(valor_str)
            else:
                resultados[campo] = None

        return resultados
    
    def formatar_linha_cliente(linha):
        campos_moeda = [
            "Notional", "Notional + inflação", "Parcela CDI", "Parcela Pré",
            "Juros CDI", "Juros Pré", "Juros IPCA", "Ajuste bruto", "Ajuste líquido", "Notional c/ correção"
        ]
        campos_percentual = ["Taxa Pré"]
        campos_fator = [
            "Fator carrego", "Fator CDI", "Fator Pré",
            "Fator carrego 2", "Fator CDI 2"
        ]
        campos_data = ["Data de início", "Data final"]
        campos_no_currency_prefix = ["IPCA Início", "IPCA Fluxo", "DU"]

        formatado = {}
        for campo_original, valor in linha.items():
            display_campo = campo_original.strip() 

            normalized_display_campo = normalizar_nome(display_campo)

            if "data inicio" in normalized_display_campo: display_campo = "Data de início"
            elif "data final" in normalized_display_campo: display_campo = "Data final"
            elif "notional c/ correcao" in normalized_display_campo: display_campo = "Notional c/ correção"
            elif "parcelacdi" == normalized_display_campo: display_campo = "Parcela CDI"
            elif "juroscdi" == normalized_display_campo: display_campo = "Juros CDI"
            elif "notional" == normalized_display_campo: display_campo = "Notional"
            elif "ajustebruto" == normalized_display_campo: display_campo = "Ajuste bruto"
            elif "ajusteliquido" == normalized_display_campo: display_campo = "Ajuste líquido"
            elif "du" == normalized_display_campo: display_campo = "DU"
            elif "ipcainicio" == normalized_display_campo: display_campo = "IPCA Início"
            elif "ipcafluxo" == normalized_display_campo: display_campo = "IPCA Fluxo"
            elif "jurosipca" == normalized_display_campo: display_campo = "Juros IPCA"
            elif "parcelaipca" == normalized_display_campo: display_campo = "Parcela IPCA"
            elif "fatorcdi" == normalized_display_campo: display_campo = "Fator CDI"
            elif "fatorcarrego" == normalized_display_campo: display_campo = "Fator carrego"
            elif "taxapre" == normalized_display_campo: display_campo = "Taxa Pré"
            elif "parcelapre" == normalized_display_campo: display_campo = "Parcela Pré"

            if pd.isna(valor):
                formatado[display_campo] = "–"
            elif display_campo in campos_moeda:
                processed_valor = clean_number_planilha(valor)
                if processed_valor is not None:
                    if processed_valor < 0:
                        formatado[display_campo] = f"R$ ({abs(processed_valor):,.2f})".replace(",", "X").replace(".", ",").replace("X", ".")
                    else:
                        formatado[display_campo] = f"R$ {processed_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                else:
                    formatado[display_campo] = str(valor)
            elif display_campo in campos_percentual:
                processed_valor = clean_number_planilha(valor) 
                if processed_valor is not None:
                    formatado[display_campo] = f"{processed_valor*100:.4f}%".replace(".", ",") 
                else:
                    formatado[display_campo] = str(valor)
            elif display_campo in campos_fator:
                processed_valor = clean_number_planilha(valor)
                if processed_valor is not None:
                    formatado[display_campo] = f"{processed_valor:.8f}".replace(".", ",")
                else:
                    formatado[display_campo] = str(valor)
            elif display_campo in campos_data:
                try:
                    date_val = pd.to_datetime(valor, dayfirst=True, errors='coerce')
                    if pd.notnull(date_val):
                        formatado[display_campo] = date_val.strftime('%d/%m/%Y')
                    else:
                        formatado[display_campo] = "–"
                except:
                    formatado[display_campo] = "–"
            elif display_campo in campos_no_currency_prefix:
                processed_valor = clean_number_planilha(valor)
                if processed_valor is not None:
                    if display_campo == "DU":
                        formatado[display_campo] = f"{int(processed_valor)}"
                    else:
                        formatado[display_campo] = f"{processed_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                else:
                    formatado[display_campo] = str(valor)
            else:
                formatado[display_campo] = str(valor)

        return pd.DataFrame.from_dict(formatado, orient="index", columns=["Valor Formatado"])

    def formatar_valores_extraidos(valores):
        campos_moeda = ['Notional', 'Parcela CDI', 'Parcela IPCA', 'Parcela Pré', 'Juros CDI', 'Juros IPCA', 'Ajuste bruto', 'Ajuste líquido', 'Notional c/ correção']
        campos_fator = ['Fator CDI', 'Fator carrego', 'Fator Pré']
        campos_data = ['Data de início', 'Data final']
        campos_percentual = ['Taxa Pré'] 
        campos_no_currency_prefix = ["IPCA Início", "IPCA Fluxo", "DU"]

        formatado = {}
        all_possible_fields = sorted(list(set(campos_moeda + campos_fator + campos_data + campos_percentual + campos_no_currency_prefix)))

        for campo in all_possible_fields:
            valor = valores.get(campo)

            if campo in campos_moeda and valor is not None:
                if isinstance(valor, (int, float)) and valor < 0:
                    formatado[campo] = f"R$ ({abs(valor):,.2f})".replace(",", "X").replace(".", ",").replace("X", ".")
                else:
                    formatado[campo] = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            elif campo in campos_fator and valor is not None:
                formatado[campo] = f"{valor:.8f}".replace(".", ",")
            elif campo in campos_percentual and valor is not None:
                formatado[campo] = f"{valor*100:.4f}%".replace(".", ",") 
            elif campo in campos_data and isinstance(valor, pd.Timestamp):
                formatado[campo] = valor.strftime('%d/%m/%Y')
            elif campo in campos_no_currency_prefix and valor is not None:
              if campo == "DU":
                formatado[campo] = f"{int(valor)}"
              else:
                formatado[campo] = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            elif valor is None:
               formatado[campo] = "–"
            else:
               formatado[campo] = str(valor)

        return pd.DataFrame.from_dict(formatado, orient="index", columns=["Valor Extraído"])

    def normalizar_nome(nome):
        return str(nome).strip().lower().replace("í", "i").replace("á", "a").replace("ç", "c").replace("ã", "a").replace("â", "a").replace("ê", "e").replace("é", "e").replace(" ", "").replace("-", "").replace("/", "").replace("_", "")
    
    if uploaded_excel and uploaded_image:
        df = pd.read_excel(uploaded_excel)
        clientes = df.iloc[:, 0].dropna().unique().tolist()
        cliente_selecionado = st.selectbox("🔍 Selecione o cliente:", clientes)

    EXCLUDE_FIELDS_FROM_COMPARISON = ["Contrato", "Tipo", "Observações", "Detalhes"]

    if tipo_batimento == "Swap - Vencimento" and 'cliente_selecionado' in locals():
        linha_cliente = df[df.iloc[:, 0] == cliente_selecionado].iloc[0].copy()
        st.write("📄 Dados da planilha para o cliente:", cliente_selecionado)

        linha_cliente_display_dict = {
            k: v for k, v in linha_cliente.items() 
            if normalizar_nome(k) not in [normalizar_nome(f) for f in EXCLUDE_FIELDS_FROM_COMPARISON]
        }
        linha_formatada = formatar_linha_cliente(linha_cliente_display_dict)
        st.dataframe(linha_formatada)

        image = Image.open(uploaded_image)
        processed_image = preprocess_image(image)

        tesseract_config = r'--oem 3 --psm 3'
        extracted_text = pytesseract.image_to_string(processed_image, lang='por', config=tesseract_config)

        st.subheader("📝 Texto extraído da imagem:")
        st.text(extracted_text)

        valores_ocr = extrair_valores_ocr(extracted_text)
        st.subheader("🔎 Valores extraídos da imagem (formatados):")
        st.dataframe(formatar_valores_extraidos(valores_ocr))

        ocr_normalized_fields = {normalizar_nome(k) for k in valores_ocr.keys()}
        excel_normalized_fields = {normalizar_nome(col_name) for col_name in linha_cliente.index}
        
        display_field_order = [
            "Data de início", "Data final", "DU", "Notional", "Notional c/ correção",
            "IPCA Início", "IPCA Fluxo", "Parcela IPCA", "Juros IPCA",
            "Taxa Pré", "Fator Pré", "Parcela Pré",
            "Fator CDI", "Parcela CDI", "Juros CDI",
            "Fator carrego", "Ajuste bruto", "Ajuste líquido"
        ]

        campos_para_comparar_set = set()
        for field in display_field_order:
            normalized_field = normalizar_nome(field)
            if (normalized_field in ocr_normalized_fields or normalized_field in excel_normalized_fields) and \
               normalized_field not in [normalizar_nome(f) for f in EXCLUDE_FIELDS_FROM_COMPARISON]:
                campos_para_comparar_set.add(field)
        
        campos_para_comparar = [field for field in display_field_order if field in campos_para_comparar_set]
        
        resultados = []

        for campo_display in campos_para_comparar:
            valor_imagem_processed = valores_ocr.get(campo_display) # Already processed by extrair_valores_ocr
            
            valor_planilha_raw = None
            normalized_campo_for_lookup = normalizar_nome(campo_display)
            for col_name_df in linha_cliente.index:
                if normalizar_nome(col_name_df) == normalized_campo_for_lookup:
                    valor_planilha_raw = linha_cliente[col_name_df]
                    break

            # Clean/process valor_planilha_raw for comparison
            valor_planilha_processed = None
            if "Data" in campo_display:
                try:
                    valor_planilha_processed = pd.to_datetime(valor_planilha_raw, dayfirst=True, errors='coerce')
                except Exception:
                    valor_planilha_processed = None
            elif campo_display == 'DU':
                cleaned_val = clean_number_planilha(valor_planilha_raw)
                if cleaned_val is not None:
                    valor_planilha_processed = int(cleaned_val)
                else:
                    valor_planilha_processed = None
            else:
                valor_planilha_processed = clean_number_planilha(valor_planilha_raw)

            igual = False # Default to False, will be set to True if conditions match
            val_planilha_fmt = "–"
            val_imagem_fmt = "–"

            if valor_planilha_processed in [None, "-", "–"] and valor_imagem_processed in [None, "-", "–"]:
                igual = True 
                val_planilha_fmt = "–"
                val_imagem_fmt = "–"
                resultados.append({
                    'Campo': campo_display,
                    'Valor Planilha': val_planilha_fmt,
                    'Valor Imagem': val_imagem_fmt,
                    'Status': '✔️'
                })
                continue  

            # Comparison Logic
            if "Data" in campo_display:
                plan_data = valor_planilha_processed
                img_data = valor_imagem_processed

                if pd.notnull(plan_data) and pd.notnull(img_data):
                    igual = plan_data.date() == img_data.date()
                    val_planilha_fmt = plan_data.strftime('%d/%m/%Y')
                    val_imagem_fmt = img_data.strftime('%d/%m/%Y')
                elif pd.isna(plan_data) and pd.isna(img_data):
                    igual = True
                    val_planilha_fmt = "–"
                    val_imagem_fmt = "–"
                else:
                    val_planilha_fmt = "–" if pd.isna(plan_data) else plan_data.strftime('%d/%m/%Y')
                    val_imagem_fmt = "–" if pd.isna(img_data) else img_data.strftime('%d/%m/%Y')
                    igual = False # Explicitly set to false if one is missing and the other is present

            elif isinstance(valor_planilha_processed, (float, int)) and isinstance(valor_imagem_processed, (float, int)):
                if campo_display in ["Ajuste bruto", "Ajuste líquido"]:
                    # Compare absolute values for Ajuste bruto/líquido
                    igual = math.isclose(abs(valor_planilha_processed), abs(valor_imagem_processed), rel_tol=1e-3, abs_tol=0.01)
                elif campo_display == "Taxa Pré":
                    # Compare with sign for Taxa Pré
                    igual = math.isclose(valor_planilha_processed, valor_imagem_processed, rel_tol=1e-5, abs_tol=1e-7)
                elif "Fator" in campo_display:
                    # Compare with sign for Fator fields
                    if campo_display == "Fator carrego":
                         igual = math.isclose(valor_planilha_processed, valor_imagem_processed, rel_tol=1e-8, abs_tol=1e-10)
                    else:
                        igual = math.isclose(valor_planilha_processed, valor_imagem_processed, rel_tol=1e-9, abs_tol=1e-10)
                else:
                    # Default for other numeric fields (compare with sign)
                    igual = math.isclose(valor_planilha_processed, valor_imagem_processed, rel_tol=1e-3, abs_tol=0.01)

                # Formatting for numeric values
                if campo_display == "Taxa Pré":
                    val_planilha_fmt = f"{valor_planilha_processed * 100:.4f}%".replace(".", ",")
                    val_imagem_fmt = f"{valor_imagem_processed * 100:.4f}%".replace(".", ",")
                elif campo_display in ["IPCA Fluxo", "IPCA Início"]:
                    val_planilha_fmt = f"{valor_planilha_processed:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    val_imagem_fmt = f"{valor_imagem_processed:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                elif campo_display == "DU":
                    val_planilha_fmt = f"{int(valor_planilha_processed)}"
                    val_imagem_fmt = f"{int(valor_imagem_processed)}"
                elif "Fator" in campo_display:
                    val_planilha_fmt = f"{valor_planilha_processed:.8f}".replace(".", ",")
                    val_imagem_fmt = f"{valor_imagem_processed:.8f}".replace(".", ",")
                elif campo_display in [
                    "Ajuste bruto", "Ajuste líquido", "Notional", "Notional c/ correção","Parcela CDI", "Parcela Pré", "Juros CDI", "Juros IPCA"]:
                    val_planilha_fmt = (
                    f"R$ ({abs(valor_planilha_processed):,.2f})"
                    if valor_planilha_processed < 0 else
                    f"R$ {valor_planilha_processed:,.2f}"
                    ).replace(",", "X").replace(".", ",").replace("X", ".")

                    val_imagem_fmt = (
                    f"R$ ({abs(valor_imagem_processed):,.2f})"
                    if valor_imagem_processed < 0 else
                    f"R$ {valor_imagem_processed:,.2f}"
                    ).replace(",", "X").replace(".", ",").replace("X", ".")
                else:
                    val_planilha_fmt = f"R$ {valor_planilha_processed:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    val_imagem_fmt = f"R$ {valor_imagem_processed:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            # Case where one is present and the other is not (or types don't match for comparison)
            else:
                # Format planilha value if present
                if valor_planilha_processed is not None:
                    if campo_display == "Taxa Pré":
                        val_planilha_fmt = f"{valor_planilha_processed * 100:.4f}%".replace(".", ",")
                    elif campo_display in ["IPCA Fluxo", "IPCA Início"]:
                        val_planilha_fmt = f"{valor_planilha_processed:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    elif campo_display == "DU":
                        val_planilha_fmt = f"{int(valor_planilha_processed)}"
                    elif "Fator" in campo_display:
                        val_planilha_fmt = f"{valor_planilha_processed:.8f}".replace(".", ",")
                    elif campo_display in [
                        "Ajuste bruto", "Ajuste líquido", "Notional", "Notional c/ correção","Parcela CDI", "Parcela Pré", "Juros CDI", "Juros IPCA"
                        ] and isinstance(valor_planilha_processed, (float, int)) and valor_planilha_processed < 0:
                        val_planilha_fmt = f"R$ ({abs(valor_planilha_processed):,.2f})".replace(",", "X").replace(".", ",").replace("X", ".")
                    elif isinstance(valor_planilha_processed, (float, int)):
                        val_planilha_fmt = f"R$ {valor_planilha_processed:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    else:
                        val_planilha_fmt = str(valor_planilha_raw) # Fallback for unhandled types
                else:
                    val_planilha_fmt = "–"

                # Format imagem value if present
                if valor_imagem_processed is not None:
                    if campo_display == "Taxa Pré":
                        val_imagem_fmt = f"{valor_imagem_processed * 100:.4f}%".replace(".", ",")
                    elif campo_display in ["IPCA Fluxo", "IPCA Início"]:
                        val_imagem_fmt = f"{valor_imagem_processed:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    elif campo_display == "DU":
                        val_imagem_fmt = f"{int(valor_imagem_processed)}"
                    elif "Fator" in campo_display:
                        val_imagem_fmt = f"{valor_imagem_processed:.8f}".replace(".", ",")
                    elif campo_display in [
                        "Ajuste bruto", "Ajuste líquido", "Notional", "Notional c/ correção",
                        "Parcela CDI", "Parcela Pré", "Juros CDI", "Juros IPCA"
                       ] and isinstance(valor_imagem_processed, (float, int)) and valor_imagem_processed < 0:
                        val_imagem_fmt = f"R$ ({abs(valor_imagem_processed):,.2f})".replace(",", "X").replace(".", ",").replace("X", ".")
                    elif isinstance(valor_imagem_processed, (float, int)):
                        val_imagem_fmt = f"R$ {valor_imagem_processed:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    else:
                        val_imagem_fmt = str(valor_imagem_processed) # Fallback for unhandled types
                else:
                    val_imagem_fmt = "–"
                
                igual = False # If we reach this else, they are not equal (one is missing or types don't match for direct comparison)

            # Adiciona ao resultado final
            resultados.append({
                'Campo': campo_display,
                'Valor Planilha': val_planilha_fmt,
                'Valor Imagem': val_imagem_fmt,
                'Status': '✔️' if igual else '❌'
            })

        st.subheader("📋 Resultado da Comparação Estruturada:")
        st.dataframe(pd.DataFrame(resultados))
 
st.markdown("---")
st.caption("Desenvolvido por Isabela Haddad · Tesouraria BR Partners 2025")



        

        
