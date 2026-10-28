
import streamlit as st
from PIL import Image
from pathlib import Path
from io import BytesIO
from datetime import datetime
import sqlite3
import json
import os
import hmac
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as PDFImage, KeepTogether

# ---------------- CONFIGURACIÓN ----------------
st.set_page_config(
    page_title="NOV ENERGY MEXICO S. de RL de CV. | Evaluación de barrenas",
    page_icon="LOGO_NOV.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).parent
RUTA_LOGO = BASE_DIR / "logo_reedhycalog.png"
RUTA_LOGO_2 = BASE_DIR / "logo_reedhycalog_blanco.png"
RUTA_LOGO_3 = BASE_DIR / "reed.png"
RUTA_BD = BASE_DIR / "historial_barrenas.db"
RUTA_VIDEO = BASE_DIR / "fondo_pozo.mp4"


import base64
from pathlib import Path
import streamlit as st

def mostrar_video_login():
    ruta_video = Path(__file__).resolve().parent / "fondo_pozo.mp4"

    if not ruta_video.exists():
        st.error(f"No se encontró el video: {ruta_video}")
        return

    with open(ruta_video, "rb") as archivo:
        video_base64 = base64.b64encode(archivo.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: transparent;
        }}

        .video-fondo {{
            position: fixed;
            inset: 0;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            z-index: 0;
            pointer-events: none;
        }}

        .video-fondo video {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}

        .video-fondo::after {{
            content: "";
            position: absolute;
            inset: 0;
            background: rgba(0, 0, 0, 0.55);
        }}

        .stMainBlockContainer {{
            position: relative;
            z-index: 1;
        }}
        </style>

        <div class="video-fondo">
            <video autoplay muted loop playsinline>
                <source src="data:video/mp4;base64,{video_base64}"
                        type="video/mp4">
            </video>
        </div>
        """,
        unsafe_allow_html=True,
    )

if not st.session_state.get("autenticado", False):
    mostrar_video_login()


# ---------------- ACCESO PRIVADO ----------------
def obtener_credenciales():
   
    usuario = os.environ.get("APP_USERNAME", "ReedHycalogPR")
    contraseña = os.environ.get("APP_PASSWORD", "NOVENERGY2026")
    try:
        usuario = st.secrets.get("APP_USERNAME", usuario)
        contrasena = st.secrets.get("APP_PASSWORD", contraseña)
    except Exception:
        
        pass
    return str(usuario), str(contraseña)


USUARIO_CONFIGURADO, CONTRASENA_CONFIGURADA = obtener_credenciales()

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] { background: #FFFFFF; }
        [data-testid="stHeader"] { background: #B82025; }
        div[data-testid="stTextInput"] label p {color: #FFFFFF !important; font-size:1.0rem}
        .login-titulo { color: #FFFFFF; font-size: 1.8rem; font-weight: 700; text-align:center; }
        .login-subtitulo { color: FFFFFF; font-size: 1rem; text-align:center; }
        div[data-testid="stFormSubmitButton"] button {
            background: #B82025 !important; color: white !important;
            border: 1px; solid #B82025 !important; font-weight: 700 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    _, columna_login, _ = st.columns([1, 1.2, 1])
    with columna_login:
        if RUTA_LOGO_2.exists():
            st.image(str(RUTA_LOGO_2), use_container_width=True)
        st.markdown('<div class="login-titulo">Acceso al sistema</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitulo">Sistema de evaluación de desgaste de barrenas IADC</div>', unsafe_allow_html=True)
        st.write("")

        if not USUARIO_CONFIGURADO or not CONTRASENA_CONFIGURADA:
            st.error("Falta configurar el usuario y la contraseña del sistema.")
            
            
          
        else:
            with st.form("formulario_login"):
                usuario_ingresado = st.text_input("Usuario", autocomplete="username")
                contrasena_ingresada = st.text_input(
                    "Contraseña", type="password", autocomplete="current-password"
                )
                enviar = st.form_submit_button("Iniciar sesión", use_container_width=True)

            if enviar:
                usuario_valido = hmac.compare_digest(usuario_ingresado, USUARIO_CONFIGURADO)
                contrasena_valida = hmac.compare_digest(contrasena_ingresada, CONTRASENA_CONFIGURADA)
                if usuario_valido and contrasena_valida:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")
    st.stop()



def inicializar_historial():
    """Crea la base de datos local para conservar las evaluaciones."""
    with sqlite3.connect(RUTA_BD) as conexion:
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS evaluaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_registro TEXT NOT NULL,
                cliente TEXT,
                pozo TEXT,
                numero_serie TEXT,
                tipo_barrena TEXT,
                datos TEXT NOT NULL,
                pdf BLOB
            )
        """)
        # Si la base de datos ya existía, agrega la columna del PDF sin borrar el historial.
        columnas = [fila[1] for fila in conexion.execute("PRAGMA table_info(evaluaciones)").fetchall()]
        if "pdf" not in columnas:
            conexion.execute("ALTER TABLE evaluaciones ADD COLUMN pdf BLOB")


inicializar_historial()

# ---------------- ESTILO INDUSTRIAL OSCURO ----------------

st.markdown("""
<style>
    /* Fondo general */
    .stApp {
        background-color: #FFFFFF;
        color: #FFFFFF;
    }

    /* Barra lateral color */        
    [data-testid="stSidebar"] {
        background-color: #F1F1F1;
        border-right: 1px solid #D6D6D6;
    }

    st.sidebar.button{
        color: #FFFFFF !important;
        
    
    }
/*COLOR LETRA BARRA LATERAL*/
    [data-testid="stSidebar"] * {
        color: #666666;
    }

    /* Títulos */
    h1, h2, h3 {
        color: #B82025 !important;
    }
    


    /* Texto general */
    p, label, .stMarkdown {
        color: #666666;
    }

    /* Botón Generar reporte PDF: estilo exclusivo */
    .st-key-generar_pdf button,
    .st-key-generar_pdf button p {
        background: #B82025 !important;
        background-color: #B82025 !important;
        color: #FFFFFF !important;
        border: 2px solid #B82025 !important;
        font-weight: 700 !important;
        opacity: 1 !important;
        transition: background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    

    /* Hover: rojo más oscuro y sombra visible */
    .st-key-generar_pdf button:hover,
    .st-key-generar_pdf button:hover p {
        background: #7F1419 !important;
        background-color: #7F1419 !important;
        color: #FFFFFF !important;
        border-color: #7F1419 !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.22) !important;
    }

    .st-key-generar_pdf button:active,
    .st-key-generar_pdf button:active p {
        background: #681015 !important;
        background-color: #681015 !important;
        color: #FFFFFF !important;
        border-color: #681015 !important;
    }
    

    

    /* Botón Descargar reporte PDF: rojo con texto blanco */
    .st-key-descargar_reporte_generado button,
    .st-key-descargar_reporte_generado button p {
        background: #B82025 !important;
        background-color: #B82025 !important;
        color: #FFFFFF !important;
        border: 2px solid #B82025 !important;
        font-weight: 700 !important;
    }

    .st-key-descargar_reporte_generado button:hover,
    .st-key-descargar_reporte_generado button:hover p {
        background: #7F1419 !important;
        background-color: #7F1419 !important;
        color: #FFFFFF !important;
        border-color: #7F1419 !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.22) !important;
    }

    /* Botones Descargar PDF dentro del historial */
    [class*="st-key-descargar_pdf_"] button,
    [class*="st-key-descargar_pdf_"] button p {
        background-color: #B82025 !important;
        color: #FFFFFF !important;
        border: 2px solid #B82025 !important;
        font-weight: 700 !important;
        opacity: 1 !important;
        transition: background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease !important;
    }

    [class*="st-key-descargar_pdf_"] button:hover,
    [class*="st-key-descargar_pdf_"] button:hover p {
        background-color: #7F1419 !important;
        color: #FFFFFF !important;
        border-color: #7F1419 !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.22) !important;
    }

    /* Botón Eliminar del historial */
    [class*="st-key-eliminar_eval_"] button,
    [class*="st-key-eliminar_eval_"] button p {
        background-color: #B82025 !important;
        color: #FFFFFF !important;
        border: 2px solid #B82025 !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }

    [class*="st-key-eliminar_eval_"] button:hover,
    [class*="st-key-eliminar_eval_"] button:hover p {
        background-color: #7F1419 !important;
        color: #FFFFFF !important;
        border-color: #7F1419 !important;
    }

    /* Encabezados de los registros del historial */
    [data-testid="stExpander"] summary {
        background-color: #B82025 !important;
        color: #FFFFFF !important;
    }

    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary svg {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }

    /* Campos de texto y selectores */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    div[data-baseweb="textarea"] {
        background-color: #FFFFFF;
        border: 1px solid #C9C9C9;
        border-radius: 5px;
    }

    /* Secciones y contenedores */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #F5F5F5;
        border-radius: 8px;
    }

    /* Botones */
    .stButton > button {
        background-color: #B82025;
        color: #FFFFFF;
        border: none;
        border-radius: 5px;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #94191E;
        color: #FFFFFF;
        border: none;
    }

    /* Área de carga de imágenes */
    [data-testid="stFileUploader"] {
        background-color: #F5F5F5;
        border: 2px dashed #B82025;
        border-radius: 8px;
        padding: 10px;
        min-height: 120px;
        display: absolute; 
       
    }

    /* Separadores */
    hr {
        border-color: #D6D6D6;
    }

    /* Encabezado corporativo */
    .encabezado-empresa {
        background-color: #B82025;
        padding: 22px;
        border-radius: 8px;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .encabezado-empresa h1 {
        color: #FFFFFF !important;
        margin: 0;
        padding: 0;
        font-size: 28px;
        line-height: 1.3;
    }

    .encabezado-empresa p {
        color: #FFFFFF !important;
        margin: 8px 0 0 0;
        font-size: 16px;
    }
    
        
</style>
""", unsafe_allow_html=True)

# ---------------- ENCABEZADO ----------------

col_logo, col_titulo = st.columns(
    [1, 3],
    vertical_alignment="center"
)

with col_logo:
    if RUTA_LOGO.exists():
        st.image(str(RUTA_LOGO), width=1200)
    else:
        st.warning(
            "No se encontró el logotipo. "
            "Coloca logo_reedhycalog.png junto a app.py."
        )

with col_titulo:
    st.markdown("""
        <div class="encabezado-empresa">
            <h1>NOV ENERGY MEXICO S. de RL de CV.</h1>
            <p> Sistema de evaluación de desgaste de barrenas IADC </p>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# ---------------- MENÚ LATERAL ----------------
st.sidebar.title("MENÚ")
pagina = st.sidebar.radio(
    "Navegación",
    ["Inicio", "Nueva evaluación", "Historial", "Configuración"]
)
if st.sidebar.button("Cerrar sesión", use_container_width=True):
    st.session_state.autenticado = False
    st.rerun()

# ---------------- PÁGINAS ----------------
if pagina == "Inicio":
    st.header("Panel principal")
    st.write(
        "Plataforma de apoyo para el registro y evaluación "
        "visual del desgaste de herramientas de perforación."
    )

    st.info(
        "Prototipo en desarrollo. El análisis automático "
        "de imágenes aún no está implementado."
    )

elif pagina == "Nueva evaluación":
    st.header("Nueva evaluación")
    st.markdown(
        '<p class="subtitulo">'
        'Registra los datos de la herramienta y carga sus fotografías.'
        '</p>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        cliente = st.text_input("Cliente*")
        pozo = st.text_input("Nombre o Identificador del Pozo*")
        equipo = st.text_input("Equipo de Perforación*")
        campo = st.text_input("Campo*")
        fecha = st.text_input("Fecha*")
        operador = st.text_input("Operador*")
        comentarios = st.text_input("Comentarios")

    with col2:
        tipo = st.selectbox(
            "Tipo de Barrena",
            ["PDC", "Tricónica"]
        )

        n_aletas = st.selectbox(
            "No. de Aletas",
            ["3","4","5","6","7","8","9","10","11","12"]
        )

        bna_no  = st.selectbox(
            "Barrena No.",
            ["1","2","3","4","5"]
        )
        diametro = st.text_input("Diámetro*")
        tipo_bna = st.text_input("Tipo*")
        no_serie =st.text_input("No. serie*")
        toberas = st.text_input("Toberas*")
        iadc = st.text_input("Código IADC*")
        

    with col3:
        profundidad_inicial = st.text_input("Profundidad Inicial*")
        profundidad_final = st.text_input("Profundidad Final*")
        m_perforados = st.text_input("Metros Perforados*")
        horas = st.text_input("Horas*")
        rop = st.text_input("R.O.P*")
        tfa = st.text_input("T.F.A*")
        formacion = st.text_input("Formación*")
        
    st.markdown(
            '<p class="subtitulo">'
            'Carga tus fotografías dependiendo el número de aletas que tenga la barrena utilizada.'
            '</p>',
            unsafe_allow_html=True
        )
        

        
    col1, col2, col3 = st.columns(3)
   
    with col1:        

         fotografias = st.file_uploader(
        "Fotografía Aleta 1",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )
    
         fotografias = st.file_uploader(
            "Fotografía Aleta 2",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True
        )
    
         fotografias = st.file_uploader(
            "Fotografía Aleta 3",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True
        )
    
         fotografias = st.file_uploader(
            "Fotografía Aleta 4",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True
        )
         
         fotografias = st.file_uploader(
             "Fotografía Vista aérea",
             type=["jpg", "jpeg", "png"],
             accept_multiple_files=True
             )
    
    with col2:  
    
         fotografias = st.file_uploader(
            "Fotografía Aleta 5",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True
        )
    
         fotografias = st.file_uploader(
                "Fotografía Aleta 6",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True
            )
    
         fotografias = st.file_uploader(
                "Fotografía Aleta 7",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True
            )
    
         fotografias = st.file_uploader(
                "Fotografía Aleta 8",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True
            )
         fotografias = st.file_uploader(
                         "Fotografía Frontal",
                         type=["jpg", "jpeg", "png"],
                         accept_multiple_files=True
                     )
    
    with col3:  
    
         fotografias = st.file_uploader(
                "Fotografía Aleta 9",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True
            )
    
         fotografias = st.file_uploader(
                "Fotografía Aleta 10",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True
            )
    
         fotografias = st.file_uploader(
                "Fotografía Aleta 11",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True
            )
    
         fotografias = st.file_uploader(
                "Fotografía Aleta 12",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True
            )
         
         fotografias = st.file_uploader(
             "Fotografía No. de Serie",
             type=["jpg", "jpeg", "png"],
             accept_multiple_files=True
             )
    
    
    

    if fotografias:
        st.subheader("Fotografías seleccionadas")
        st.write(f"Total de fotografías: {len(fotografias)}")

        columnas = st.columns(3)

        for i, archivo in enumerate(fotografias):
            try:
                imagen = Image.open(archivo)

                with columnas[i % 3]:
                    st.image(
                        imagen,
                        caption=archivo.name,
                        use_container_width=True
                    )
            except Exception:
                st.error(f"No se pudo abrir: {archivo.name}")

    st.caption(
        "Las imágenes se muestran para revisión. "
        "El análisis automático de desgaste aún no está implementado; la evaluación IADC se captura manualmente."
    )

    st.subheader("Evaluación de desgaste IADC")
    st.write("Completa manualmente las observaciones de desgaste que correspondan a la barrena.")
    desgaste_cols = st.columns(4)
    with desgaste_cols[0]:
        desgaste_interior = st.text_input("Hilera interior*", placeholder="Indique desgaste")
        desgaste_exterior = st.text_input("Hilera exterior*",placeholder="Indique desgaste")
    with desgaste_cols[1]:
        caracteristicas = st.text_input("Característica Desgaste*", placeholder="Código/Observación") 
        ubicacion = st.text_input("Ubicación*", placeholder="Indique ubicación")
    with desgaste_cols[2]:
        cojinetes_sello = st.text_input("Cojinetes/sello*", placeholder="Aplica/No Aplica")
        calibre_desgaste = st.text_input("Gauge/Calibre*", placeholder="Observación")
    with desgaste_cols[3]:
        otras_caracteristicas = st.text_input("Otras características*", placeholder="Observación")
        razon_dull = st.text_input("Código de razón de salida*", placeholder="Código / Observación")

        
    if st.button("Generar reporte PDF", type="primary", key="generar_pdf"):
        campos_obligatorios = {
            "Cliente": cliente,
            "Nombre o Identificador del Pozo": pozo,
            "Equipo de Perforación": equipo,
            "Campo": campo,
            "Fecha": fecha,
            "Operador": operador,
            "Diámetro": diametro,
            "Tipo": tipo_bna,
            "No. serie": no_serie,
            "Toberas": toberas,
            "Código IADC": iadc,
            "Profundidad Inicial": profundidad_inicial,
            "Profundidad Final": profundidad_final,
            "Metros Perforados": m_perforados,
            "Horas": horas,
            "R.O.P": rop,
            "T.F.A": tfa,
            "Formación": formacion,
            "Hilera interior": desgaste_interior,
            "Hilera exterior": desgaste_exterior,
            "Característica Desgaste": caracteristicas,
            "Ubicación": ubicacion,
            "Cojinetes/sello": cojinetes_sello,
            "Gauge/Calibre": calibre_desgaste,
            "Otras características": otras_caracteristicas,
            "Código de razón de salida": razon_dull,
        }
        campos_vacios = [nombre for nombre, valor in campos_obligatorios.items() if not str(valor).strip()]
        if campos_vacios:
            st.error("Es obligatorio llenar todos los campos")
        else:
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=letter,
                rightMargin=0.35 * inch,
                leftMargin=0.35 * inch,
                topMargin=0.3 * inch,
                bottomMargin=0.3 * inch,
            )

            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(
                name="ReportTitle",
                parent=styles["Title"],
                textColor=colors.HexColor("#000000"),
                fontSize=12,
                leading=16,
                alignment=1,
                spaceAfter=5,
            ))
            styles.add(ParagraphStyle(
                name="SectionHeading",
                parent=styles["Heading2"],
                textColor=colors.HexColor("#B82025"),
                fontSize=13,
                leading=14,
                spaceBefore=8,
                spaceAfter=5,
            ))
            styles.add(ParagraphStyle(
                name="SmallText",
                parent=styles["BodyText"],
                fontSize=8,
                leading=10,
            ))
            styles.add(ParagraphStyle(
                name="TituloEncabezadoPDF",
                parent=styles["Title"],
                fontName="Helvetica-Bold",
                fontSize=15,
                leading=16,
                textColor=colors.white,
                alignment=1,
                spaceAfter=4,
            ))
            styles.add(ParagraphStyle(
                name="SubtituloEncabezadoPDF",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=11,
                leading=10,
                textColor=colors.white,
                alignment=1,
            ))

            story = []

            # Preparar el logo para el encabezado.
            logo_encabezado = ""
            if RUTA_LOGO_2.exists():
                try:
                    logo_encabezado = PDFImage(
                        str(RUTA_LOGO_2),
                        width=2.35 * inch,
                        height=1.75 * inch,
                        kind="proportional",
                    )
                except Exception:
                    logo_encabezado = ""

            texto_encabezado = [
                Paragraph(
                    "NOV ENERGY MEXICO S. de RL de CV.",
                    styles["TituloEncabezadoPDF"],
                ),
                Paragraph(
                    "EVALUACIÓN DE DESGASTE",
                    styles["SubtituloEncabezadoPDF"],
                ),
            ]

            tabla_encabezado = Table(
                [[logo_encabezado, texto_encabezado]],
                colWidths=[2.65 * inch, 4.75 * inch],
                rowHeights=[0.95 * inch],
                hAlign="LEFT",
            )
            tabla_encabezado.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#B82025")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, 0), "LEFT"),
                ("ALIGN", (1, 0), (1, 0), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            story.append(tabla_encabezado)
            story.append(Spacer(1, 8))
            story.append(Paragraph(
                f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                styles["SmallText"],
            ))
            story.append(Spacer(1, 5))

            def safe(value):
                value = "" if value is None else str(value)
                return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") or "—"

            # Estilos compactos para organizar la información debajo del encabezado existente.
            estilo_etiqueta = ParagraphStyle(
                name="EtiquetaCompacta",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=6.5,
                leading=7,
                textColor=colors.black,
                alignment=0,
            )
            estilo_valor = ParagraphStyle(
                name="ValorCompacto",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=7,
                leading=8,
                textColor=colors.HexColor("#B82025"),
                alignment=1,
            )
            estilo_titulo_rojo = ParagraphStyle(
                name="TituloFranjaRoja",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=7,
                leading=8,
                textColor=colors.white,
                alignment=1,
            )
            estilo_celda = ParagraphStyle(
                name="CeldaCompacta",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=6.5,
                leading=7,
                textColor=colors.black,
                alignment=1,
            )
            estilo_celda_negrita = ParagraphStyle(
                name="CeldaCompactaNegrita",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=6.2,
                leading=7,
                textColor=colors.black,
                alignment=1,
            )

            def franja_titulo(texto, ancho):
                tabla = Table(
                    [[Paragraph(safe(texto), estilo_titulo_rojo)]],
                    colWidths=[ancho],
                    hAlign="LEFT",
                )
                tabla.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#B82025")),
                    ("BOX", (0, 0), (-1, -1), 0.7, colors.black),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]))
                story.append(tabla)

            ancho_util = 7.4 * inch

            # 1. Datos generales en tres bloques compactos.
            story.append(Spacer(1, 2))
            datos_generales = [
                [("Cliente:", cliente), ("Barrena No.:", bna_no), ("Prof. inicial:", profundidad_inicial)],
                [("Pozo:", pozo), ("Diámetro:", diametro), ("Prof. final:", profundidad_final)],
                [("Equipo:", equipo), ("Tipo:", tipo_bna), ("Metros perforados:", m_perforados)],
                [("Campo:", campo), ("No. de serie:", no_serie), ("Horas:", horas)],
                [("Fecha:", fecha), ("Toberas:", toberas), ("R.O.P.:", rop)],
                [("Operador:", operador), ("IADC:", iadc), ("T.F.A.:", tfa)],
            ]
            datos_tabla = []
            for fila in datos_generales:
                fila_pdf = []
                for etiqueta, valor in fila:
                    fila_pdf.append([
                        Paragraph(safe(etiqueta), estilo_etiqueta),
                        Paragraph(safe(valor), estilo_valor),
                    ])
                datos_tabla.append(fila_pdf)

            tabla_general = Table(
                datos_tabla,
                colWidths=[ancho_util / 3] * 3,
                hAlign="LEFT",
            )
            tabla_general.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.45, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))
            story.append(tabla_general)
            story.append(Spacer(1, 3))

            # 2. Registro de barrena en una sola tabla horizontal.
            franja_titulo("RECORD DE BARRENA", ancho_util)
            encabezados_record = [
                "DIÁM.", "TIPO", "No. SERIE", "TOBERAS", "PROF. ENTRADA",
                "PROF. SALIDA", "METROS", "HORAS", "ROP", "FORMACIÓN"
            ]
            valores_record = [
                diametro, tipo_bna, no_serie, toberas, profundidad_inicial,
                profundidad_final, m_perforados, horas, rop, formacion
            ]
            tabla_record_datos = [
                [Paragraph(safe(x), estilo_celda_negrita) for x in encabezados_record],
                [Paragraph(safe(x), estilo_valor) for x in valores_record],
            ]
            anchos_record = [0.55, 0.55, 0.85, 0.65, 0.75, 0.75, 0.55, 0.45, 0.45, 2.25]
            factor = ancho_util / sum(anchos_record)
            tabla_record = Table(
                tabla_record_datos,
                colWidths=[ancho_util /10] * 10,
                hAlign="LEFT",
            )
            tabla_record.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E6E6E6")),
                ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(tabla_record)
            story.append(Spacer(1, 3))
            
        
            
          
            # 3. Tabla de evaluación IADC compacta.
            franja_titulo("ESTRUCTURA DE CORTE, COJINETE, CALIBRE Y OBSERVACIONES", ancho_util)
            encabezados_iadc = [
                "HILERA INTERIOR", "HILERA EXTERIOR", "CARACT. DESGASTE",
                "UBICACIÓN", "COJINETE / SELLO", "GAUGE / CALIBRE",
                "OTRAS CARACT.", "RAZÓN DE SALIDA"
            ]
            valores_iadc = [
                desgaste_interior, desgaste_exterior, caracteristicas,
                ubicacion, cojinetes_sello, calibre_desgaste,
                otras_caracteristicas, razon_dull
            ]
            tabla_iadc = Table(
                [
                    [Paragraph(safe(x), estilo_celda_negrita) for x in encabezados_iadc],
                    [Paragraph(safe(x), estilo_valor) for x in valores_iadc],
                ],
                colWidths=[ancho_util / 8] * 8,
                hAlign="LEFT",
            )
            tabla_iadc.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E6E6E6")),
                ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(tabla_iadc)
            story.append(Spacer(1, 5))

            # 4. Fotografías en una cuadrícula de tres columnas.
            franja_titulo("FOTOGRAFÍAS DE EVIDENCIA", ancho_util)
            if fotografias:
                celdas_fotos = []
                fila_fotos = []
                for idx, archivo in enumerate(fotografias, start=1):
                    try:
                        archivo.seek(0)
                        img_bytes = BytesIO(archivo.getvalue())
                        imagen_pdf = PDFImage(img_bytes, width=2.45 * inch, height=1.65 * inch, kind="proportional")
                        fila_fotos.append([
                            imagen_pdf
                           
                        ])
                    except Exception:
                        fila_fotos.append(Paragraph(
                            f"No fue posible incorporar la fotografía: {safe(archivo.name)}",
                            styles["SmallText"]
                        ))
                    if len(fila_fotos) == 3:
                        celdas_fotos.append(fila_fotos)
                        fila_fotos = []
                if fila_fotos:
                    while len(fila_fotos) < 3:
                        fila_fotos.append("")
                    celdas_fotos.append(fila_fotos)

                tabla_fotos = Table(
                    celdas_fotos,
                    colWidths=[ancho_util / 3] * 3,
                    hAlign="LEFT",
                )
                tabla_fotos.setStyle(TableStyle([
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BBBBBB")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]))
                story.append(tabla_fotos)
            else:
                story.append(Paragraph("No se adjuntaron fotografías.", styles["SmallText"]))

            story.append(Spacer(1, 12))

            # Tabla de CÓDIGOS: listas largas dentro de cada celda.
            encabezados_tabla = [
                Paragraph("DESGASTE CORTADORES", estilo_titulo_rojo),
                Paragraph("CARACTERÍSTICAS DEL DESGASTE", estilo_titulo_rojo),
                Paragraph("RAZÓN POR LA CUAL SE SACÓ LA BARRENA", estilo_titulo_rojo),
            ]

            # Columna izquierda: códigos de desgaste y ubicación.
            celda_ubicacion = Table(
                [
                    [Paragraph("0 - SIN DESGASTE", estilo_celda)],
                    [Paragraph("1 - ", estilo_celda)],
                    [Paragraph("2 - ", estilo_celda)],
                    [Paragraph("3 - ", estilo_celda)],
                    [Paragraph("4 - 50% ESTRUCTURA DE CORTE", estilo_celda)],
                    [Paragraph("5 - ", estilo_celda)],
                    [Paragraph("6 - ", estilo_celda)],
                    [Paragraph("7 - ", estilo_celda)],
                    [Paragraph("8 - SIN ESTRUCTURA DE CORTE", estilo_celda)],
                    [Paragraph("UBICACIÓN", estilo_titulo_rojo)],
                    [Paragraph("PDC", estilo_celda_negrita)],
                    [Paragraph("C - CONO/CENTRO", estilo_celda)],
                    [Paragraph("N - NARIZ (HILERA)", estilo_celda)],
                    [Paragraph("T - FLANCO (TAPER)", estilo_celda)],
                    [Paragraph("S - HOMBRO", estilo_celda)],
                    [Paragraph("G - CALIBRE (HILERA)", estilo_celda)],
                    [Paragraph("A - TODAS LAS HILERAS", estilo_celda)],
                    [Paragraph("TRICÓNICAS", estilo_celda_negrita)],
                    [Paragraph("N - NARIZ (HILERA)", estilo_celda)],
                    [Paragraph("M - HILERA INTERMEDIAS", estilo_celda)],
                    [Paragraph("H - HILERAS DEL CALIBRE", estilo_celda)],
                    [Paragraph("G - CALIBRE", estilo_celda)],
                    [Paragraph("A - TODAS LAS HILERAS", estilo_celda)],
                ],
                colWidths=[1.7 * inch],
            )
            celda_ubicacion.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
                ("BACKGROUND", (0, 9), (0, 9), colors.HexColor("#B82025")),
                ("TEXTCOLOR", (0, 9), (0, 9), colors.white),
                ("BACKGROUND", (0, 10), (0, 10), colors.HexColor("#B7B7B7")),
                ("BACKGROUND", (0, 17), (0, 17), colors.HexColor("#B7B7B7")),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]))

            # Cada código se mantiene en una línea dentro de su celda.
            texto_caracteristicas = Paragraph(
                "BC - CONO ROTO<br/>"
                "BF - FALLA DE PEGA<br/>"
                "BT - DIENTES/CORTADORES ROTOS<br/>"
                "BU - EMBOLAMIENTO<br/>"
                "CC - CONO AGRIETADO*<br/>"
                "CD - CONO ARRASTRADO*<br/>"
                "CI - INTERFERENCIA DE CONO*<br/>"
                "CR - CORONADO<br/>"
                "CT - DIENTES/CORTADORES ASTILLADOS<br/>"
                "ER - EROSIÓN<br/>"
                "FC - DESGASTE PLANO DE LA CRESTA*<br/>"
                "HC - SOBRECALENTAMIENTO<br/>"
                "JD - DAÑO POR CHATARRA<br/>"
                "LC - PÉRDIDA DE CONO<br/>"
                "LN - PÉRDIDA DE TOBERA<br/>"
                "LT - PÉRDIDA DE DIENTES/CORTADORES<br/>"
                "NO - NINGUNA OTRA CARACTERÍSTICA<br/>"
                "OC - DESGASTE EXCÉNTRICO<br/>"
                "PB - BARRENA PINCHADA<br/>"
                "PN - TAPONAMIENTO TOBERA<br/>"
                "RG - CALIBRE REDONDEADO*<br/>"
                "RO - ANILLAMIENTO<br/>"
                "SD - DAÑO DEL FALDÓN*<br/>"
                "SS - DESGASTE DE CORT. AUTOAFILABLES<br/>"
                "TR - RASTRILLEO*<br/>"
                "WO - LAVADO DE BARRENA<br/>"
                "WT - DIENTES/CORTADORES DESGASTADOS",
                estilo_celda,
            )

            texto_razon_salida = Paragraph(
                "BHA - CAMBIO CONJUNTO DE FONDO<br/>"
                "DMF - FALLA MOTOR FONDO<br/>"
                "DSF - FALLA SARTA PERFORACIÓN<br/>"
                "DST - FALLA SISTEMA REGISTRO PERFORACIÓN<br/>"
                "DTF - FALLA HERRAMIENTA POZO ABAJO<br/>"
                "LOG - REGISTROS ELÉCTRICOS<br/>"
                "CM - CONDICIONES LODO<br/>"
                "RIG - REPARACIONES EN EL EQUIPO<br/>"
                "TD - PROFUNDIDAD TOTAL ÚLTIMO CASING<br/>"
                "CP - EXTRACCIÓN DE NÚCLEO<br/>"
                "DP - TAPÓN SARTA PERFORACIÓN<br/>"
                "FM - CAMBIO FORMACIÓN<br/>"
                "HP - PROBLEMAS EN EL AGUJERO<br/>"
                "HR - HORAS DE VIDA DE LA MECHA<br/>"
                "PP - PRESIÓN DE BOMBEO<br/>"
                "PR - RITMO PENETRACIÓN<br/>"
                "TW - TORSIÓN<br/>"
                "WC - CONDICIONES CLIMÁTICAS<br/>"
                "WO - LAVADO DE LA SARTA DE PERFORACIÓN",
                estilo_celda,
            )

            tabla = Table(
                [
                    encabezados_tabla,
                    [celda_ubicacion, texto_caracteristicas, texto_razon_salida],
                ],
                colWidths=[1.7 * inch, 3.4 * inch, 2.3 * inch],
                hAlign="LEFT",
                splitByRow=1,
            )
            tabla.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#B82025")),
                ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(tabla)
            story.append(Spacer(1, 8))
            story.append(Paragraph(
                "No realiza todavía una clasificación automática del desgaste.",
                styles["SmallText"],
            ))
            doc.build(story)
            pdf_buffer.seek(0)

            # Guardar los datos de esta evaluación en el historial local.
            datos_evaluacion = {
                "Cliente": cliente,
                "Pozo": pozo,
                "Equipo de perforación": equipo,
                "Campo": campo,
                "Fecha": fecha,
                "Operador": operador,
                "Tipo de barrena": tipo,
                "Barrena No.": bna_no,
                "Diámetro": diametro,
                "Tipo": tipo_bna,
                "No. de serie": no_serie,
                "Toberas": toberas,
                "Código IADC": iadc,
                "Profundidad inicial": profundidad_inicial,
                "Profundidad final": profundidad_final,
                "Metros perforados": m_perforados,
                "Horas": horas,
                "R.O.P.": rop,
                "T.F.A.": tfa,
                "Hilera interior": desgaste_interior,
                "Hilera exterior": desgaste_exterior,
                "Característica de desgaste": caracteristicas,
                "Ubicación": ubicacion,
                "Cojinetes/Sello": cojinetes_sello,
                "Gauge/Calibre": calibre_desgaste,
                "Otras características": otras_caracteristicas,
                "Código de razón de salida": razon_dull,
                "Fotografías": [archivo.name for archivo in fotografias] if fotografias else [],
            }
            with sqlite3.connect(RUTA_BD) as conexion:
                conexion.execute(
                    """INSERT INTO evaluaciones
                       (fecha_registro, cliente, pozo, numero_serie, tipo_barrena, datos, pdf)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        cliente, pozo, no_serie, tipo,
                        json.dumps(datos_evaluacion, ensure_ascii=False),
                        pdf_buffer.getvalue(),
                    ),
                )

            nombre_pozo = "_".join((pozo.strip() or "pozo").split())
            nombre_serie = "_".join((no_serie.strip() or "sin_serie").split())
            st.success("Reporte PDF generado.")
            st.download_button(
                label="Descargar reporte PDF",
                data=pdf_buffer.getvalue(),
                file_name=f"Reporte_IADC_{nombre_pozo}_{nombre_serie}.pdf",
                mime="application/pdf",
                key="descargar_reporte_generado"
            )

elif pagina == "Historial":
    st.header("Historial de evaluaciones")
    st.caption("Abre el PDF que se generó para cada evaluación o elimina registros que ya no necesites.")

    with sqlite3.connect(RUTA_BD) as conexion:
        registros = conexion.execute(
            """SELECT id, fecha_registro, cliente, pozo, numero_serie, tipo_barrena, datos, pdf
               FROM evaluaciones ORDER BY id DESC"""
        ).fetchall()

    if not registros:
        st.info("Todavía no hay evaluaciones guardadas. Genera un reporte desde ‘Nueva evaluación’ para crear el primer registro.")
    else:
        st.write(f"Evaluaciones registradas: **{len(registros)}**")
        filtro = st.text_input("Buscar por cliente, pozo o número de serie", key="buscar_historial")
        if filtro.strip():
            termino = filtro.casefold().strip()
            registros = [r for r in registros if any(termino in str(valor or "").casefold() for valor in r[2:5])]

        if not registros:
            st.warning("No se encontraron evaluaciones con ese criterio.")
        else:
            for registro in registros:
                id_eval, fecha_registro, cliente_reg, pozo_reg, serie_reg, tipo_reg, datos_json, pdf_guardado = registro
                etiqueta = f"#{id_eval} · {pozo_reg or 'Sin pozo'} · {serie_reg or 'Sin serie'} · {fecha_registro}"
                with st.expander(etiqueta):
                    c1, c2, c3 = st.columns(3)
                    c1.write(f"**Cliente:** {cliente_reg or '—'}")
                    c2.write(f"**Tipo de barrena:** {tipo_reg or '—'}")
                    c3.write(f"**No. de serie:** {serie_reg or '—'}")

                    if pdf_guardado:
                        nombre_pozo = "_".join((pozo_reg or "pozo").strip().split())
                        nombre_serie = "_".join((serie_reg or "sin_serie").strip().split())
                        st.download_button(
                            "Descargar reporte PDF",
                            data=bytes(pdf_guardado),
                            file_name=f"Reporte_IADC_{nombre_pozo}_{nombre_serie}.pdf",
                            mime="application/pdf",
                            key=f"descargar_pdf_{id_eval}",
                            use_container_width=True,
                        )
                    else:
                        st.warning("Este registro se creó antes de guardar los PDF. El reporte original no está archivado; puedes eliminar el registro o conservar sus datos, pero no recuperar el PDF exacto desde aquí.")

                    try:
                        datos_guardados = json.loads(datos_json)
                        with st.expander("Ver datos de la evaluación"):
                            for campo, valor in datos_guardados.items():
                                if campo != "Fotografías":
                                    st.write(f"**{campo}:** {valor if valor not in (None, '') else '—'}")
                            fotos = datos_guardados.get("Fotografías", [])
                            if fotos:
                                st.write("**Fotografías registradas por nombre:** " + ", ".join(fotos))
                    except (json.JSONDecodeError, TypeError):
                        st.error("No fue posible leer los datos guardados de esta evaluación.")

                    st.divider()
                    confirmar = st.checkbox(
                        "Confirmo que quiero eliminar este reporte del historial",
                        key=f"confirmar_eliminar_{id_eval}"
                    )
                    if st.button("Eliminar del historial", key=f"eliminar_eval_{id_eval}", disabled=not confirmar):
                        with sqlite3.connect(RUTA_BD) as conexion:
                            conexion.execute("DELETE FROM evaluaciones WHERE id = ?", (id_eval,))
                        
                        st.success(f"Se eliminó la evaluación #{id_eval} del historial.")
                        st.rerun()

elif pagina == "Configuración":
    st.header("Configuración")
    st.write("Sistema: ReedHycalog")
    st.write("Versión: Prototipo inicial")
    st.write("Estado: En desarrollo")

