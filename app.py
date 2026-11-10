import datetime as dt
import oracledb
import pandas as pd
import streamlit as st

# Configuración inicial de la página
st.set_page_config(page_title="Yoga & Fitness Studio", page_icon="🧘", layout="wide")

# Estilos personalizados (Banner y tarjetas)
st.markdown(
    """
    <style>
    .banner {background: linear-gradient(90deg, #2E7D32, #1B5E20 60%, #004D40); color:#fff;
             padding:1.2rem 1.8rem; border-radius:12px; margin-bottom:1.5rem;}
    .banner h1 {margin:0; font-size:2.2rem; color:#fff;}
    .banner p {margin:0; opacity:.9; font-size:1.1rem;}
    div[data-testid="stMetric"] {background:#f8f9fa; border:1px solid #C8E6C9; border-left:5px solid #2E7D32;
                                 padding:.6rem .9rem; border-radius:8px;}
    </style>
    <div class="banner">
        <h1>🧘 Bienvenid@ a Yoga & Fitness Studio</h1>
        <p>Conoce nuestras clases, elige tu plan de membresía e inscríbete o reserva tu cupo en línea.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

ESQUEMA = "ADMIN"

# ---------------- 1. Conexión a Oracle (Compatible con Local y Streamlit Cloud) ----------------

@st.cache_resource
def conectar():
    """Obtiene la conexión a Oracle leyendo secrets.toml de forma segura."""
    s = st.secrets["oracle"]
    
    if "lib_dir" in s:
        oracledb.init_oracle_client(lib_dir=s["lib_dir"], config_dir=s.get("config_dir"))
        return oracledb.connect(user=s["user"], password=s["password"], dsn=s["dsn"])
    
    kwargs = {}
    if s.get("config_dir") and not str(s.get("config_dir")).startswith("/app"):
        kwargs["config_dir"] = s.get("config_dir")
        kwargs["wallet_location"] = s.get("wallet_location", s.get("config_dir"))
    if s.get("wallet_password"):
        kwargs["wallet_password"] = s.get("wallet_password")
        
    return oracledb.connect(
        user=s["user"],
        password=s["password"],
        dsn=s["dsn"],
        **kwargs
    )

try:
    conn = conectar()
except Exception as err:
    st.error(f"❌ Error conectando a la base de datos Oracle: {err}")
    st.info("Revisa la configuración de Secrets en Streamlit Cloud.")
    st.stop()


# ---------------- 2. Funciones de Consulta y Modificación ----------------

def consultar(sql, params=None):
    df = pd.read_sql(sql, conn, params=params)
    df.columns = [c.lower() for c in df.columns]
    return df

def modificar(sql, params=None):
    cur = conn.cursor()
    try:
        cur.execute(sql, params or {})
        conn.commit()
        return cur.rowcount
    except Exception as e:
        conn.rollback()
        raise e

def insertar_con_id(sql, col_id, params):
    cur = conn.cursor()
    try:
        var_id = cur.var(int)
        cur.execute(f"{sql} RETURNING {col_id} INTO :new_id", {**params, "new_id": var_id})
        conn.commit()
        return int(var_id.getvalue()[0])
    except Exception as e:
        conn.rollback()
        raise e


# ---------------- 3. Menú Principal de Navegación ----------------

opcion_menu = st.sidebar.radio(
    "Navegación Studio",
    ["🏷️ Ver Planes y Precios", "🧘 Clases y Horarios", "👨‍🏫 Instructores", "📝 Inscribirse (Nuevo Cliente)", "📅 Agendar Reserva", "📋 Ver mis Reservas"]
)

# -----------------------------------------------------------------
# VISTA 1: VER PLANES Y PRECIOS
# -----------------------------------------------------------------
if opcion_menu == "🏷️ Ver Planes y Precios":
    st.header("🏷️ Planes de Membresía Disponibles")
    st.write("Explora las opciones de membresía que tenemos diseñadas para tu bienestar:")

    planes_df = consultar(f"""
        SELECT p_id_plan AS id, p_nombre_plan AS plan, p_tipo_clase AS tipo_clase, 
               p_duracion_plan AS duracion_dias, p_limite_clases AS limite_clases, 
               p_precio AS precio, p_precio_descuento AS precio_promocional, p_estado AS estado
        FROM {ESQUEMA}.plan_membresia
        ORDER BY p_precio ASC
    """)

    if not planes_df.empty:
        planes_df["precio"] = planes_df["precio"].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "$0.00")
        planes_df["precio_promocional"] = planes_df["precio_promocional"].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) and x > 0 else "N/A")
        
        st.dataframe(planes_df, use_container_width=True, hide_index=True)

        st.subheader("💡 Métricas de Planes")
        col1, col2, col3 = st.columns(3)
        col1.metric("Planes Activos", len(planes_df))
        col2.metric("Tipos de Clases Incluidas", len(planes_df["tipo_clase"].unique()))
        col3.metric("Plan Más Popular", planes_df["plan"].iloc[0] if len(planes_df) > 0 else "-")
    else:
        st.info("No hay planes registrados actualmente.")

# -----------------------------------------------------------------
# VISTA 2: CLASES Y HORARIOS
# -----------------------------------------------------------------
elif opcion_menu == "🧘 Clases y Horarios":
    st.header("🧘 Clases Programadas y Horarios")
    st.write("Filtra y conoce los horarios ampliados de nuestras sesiones:")

    tipo_filtro = st.selectbox("Filtrar por Tipo de Clase", ["Todos", "yoga", "pilates", "barre", "multifuncional"])
    
    where_clause = "" if tipo_filtro == "Todos" else f"WHERE c_tipo_clase = '{tipo_filtro}'"
    
    clases_df = consultar(f"""
        SELECT c_id_clase AS id, c_nombre_clase AS nombre_clase, c_tipo_clase AS tipo,
               c_dia AS dia, c_horario AS horario, c_salon_clase AS salon,
               c_cupo_max AS cupo_maximo, c_intensidad AS intensidad, c_modalidad AS modalidad, c_estado AS estado
        FROM {ESQUEMA}.clases
        {where_clause}
        ORDER BY c_id_clase ASC
    """)

    st.dataframe(clases_df, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------
# VISTA 3: INSTRUCTORES
# -----------------------------------------------------------------
elif opcion_menu == "👨‍🏫 Instructores":
    st.header("👨‍🏫 Nuestro Equipo de Instructores")
    st.write("Conoce a los profesionales asignados a cada disciplina:")

    instructores_df = consultar(f"""
        SELECT i_id_instructor AS id, i_nombre_completo AS nombre, i_especialidad AS especialidad,
               i_tipo_contrato AS contrato, i_cantidad_certificaciones AS certificaciones,
               i_tipo_certificacion AS detalle_certificacion, i_estado AS estado
        FROM {ESQUEMA}.instructor
        WHERE i_estado = 'activo'
        ORDER BY i_especialidad ASC, i_nombre_completo ASC
    """)

    st.dataframe(instructores_df, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------
# VISTA 4: INSCRIBIRSE (NUEVO CLIENTE)
# -----------------------------------------------------------------
elif opcion_menu == "📝 Inscribirse (Nuevo Cliente)":
    st.header("📝 Formulario de Inscripción de Clientes")
    st.write("Completa tus datos y selecciona tu plan inicial para unirte al estudio:")

    planes_opciones = consultar(f"SELECT p_id_plan, p_nombre_plan, p_precio FROM {ESQUEMA}.plan_membresia WHERE p_estado IN ('activo', 'disponible')")

    with st.form("form_inscripcion", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            nombre = st.text_input("Nombre Completo *")
            correo = st.text_input("Correo Electrónico *")
            telefono = st.text_input("Teléfono de Contacto *")
            genero = st.selectbox("Género", ["femenino", "masculino", "otro"])
        with col_b:
            direccion = st.text_input("Dirección de Residencia")
            condicion_medica = st.text_input("Condición Médica / Lesiones", value="Ninguna")
            
            # RANGO EXPANDIDO DE FECHAS (1950 hasta 2010)
            fecha_nac =
