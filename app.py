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
    """Conecta a Oracle utilizando los secretos guardados en secrets.toml."""
    s = st.secrets["oracle"]
    if "lib_dir" in s:
        oracledb.init_oracle_client(lib_dir=s["lib_dir"], config_dir=s.get("config_dir"))
        return oracledb.connect(user=s["user"], password=s["password"], dsn=s["dsn"])
    
    return oracledb.connect(
        user=s["user"],
        password=s["password"],
        dsn=s["dsn"],
        config_dir=s.get("config_dir"),
        wallet_location=s.get("wallet_location", s.get("config_dir")),
        wallet_password=s.get("wallet_password")
    )

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
    st.write("Filtra y conoce los horarios de nuestras sesiones:")

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
    st.write("Conoce a los profesionales a cargo de tus disciplinas:")

    instructores_df = consultar(f"""
        SELECT i_id_instructor AS id, i_nombre_completo AS nombre, i_especialidad AS especialidad,
               i_tipo_contrato AS contrato, i_cantidad_certificaciones AS certificaciones,
               i_tipo_certificacion AS detalle_certificacion, i_estado AS estado
        FROM {ESQUEMA}.instructor
        WHERE i_estado = 'activo'
        ORDER BY i_nombre_completo ASC
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
            fecha_nac = st.date_input("Fecha de Nacimiento", value=dt.date(1995, 1, 1))
            
            plan_elegido = st.selectbox(
                "Selecciona tu Plan de Membresía *",
                planes_opciones["p_id_plan"].tolist(),
                format_func=lambda x: f"{planes_opciones[planes_opciones['p_id_plan'] == x]['p_nombre_plan'].iloc[0]} (${planes_opciones[planes_opciones['p_id_plan'] == x]['p_precio'].iloc[0]:,.2f})"
            )

        btn_inscribir = st.form_submit_button("✅ Completar Inscripción")

    if btn_inscribir:
        if not nombre.strip() or not correo.strip() or not telefono.strip():
            st.warning("⚠️ Por favor completa los campos obligatorios (*).")
        else:
            try:
                SQL_INS_USUARIO = f"""
                    INSERT INTO {ESQUEMA}.usuario (
                        u_nombre_completo, u_id_plan, u_genero, u_estado,
                        u_direccion_residencia, u_telefono, u_correo_electronico,
                        u_condicion_medica, u_fecha_nacimiento
                    ) VALUES (
                        :nom, :pln, :gen, 'activo', :direc, :tel, :cor, :med, :fec
                    )
                """
                params = {
                    "nom": nombre.strip(),
                    "pln": int(plan_elegido),
                    "gen": genero,
                    "direc": direccion.strip(),
                    "tel": telefono.strip(),
                    "cor": correo.strip(),
                    "med": condicion_medica.strip(),
                    "fec": fecha_nac
                }
                nuevo_id = insertar_con_id(SQL_INS_USUARIO, "u_id_usuario", params)
                st.success(f"🎉 ¡Inscripción exitosa! Tu ID de usuario asignado es #{nuevo_id}. Ya puedes agendar tu clase.")
            except Exception as e:
                st.error(f"Error al procesar la inscripción: {e}")

# -----------------------------------------------------------------
# VISTA 5: AGENDAR RESERVA
# -----------------------------------------------------------------
elif opcion_menu == "📅 Agendar Reserva":
    st.header("📅 Agendamiento de Clases")
    st.write("Selecciona tu nombre, la clase deseada y el instructor de tu preferencia:")

    usuarios_df = consultar(f"SELECT u_id_usuario, u_nombre_completo, u_id_plan FROM {ESQUEMA}.usuario WHERE u_estado = 'activo' ORDER BY u_nombre_completo ASC")
    clases_df = consultar(f"SELECT c_id_clase, c_nombre_clase, c_horario, c_dia FROM {ESQUEMA}.clases WHERE c_estado = 'programada' ORDER BY c_nombre_clase ASC")
    instructores_df = consultar(f"SELECT i_id_instructor, i_nombre_completo, i_especialidad FROM {ESQUEMA}.instructor WHERE i_estado = 'activo' ORDER BY i_nombre_completo ASC")
    planes_df = consultar(f"SELECT p_id_plan, p_precio FROM {ESQUEMA}.plan_membresia")

    if usuarios_df.empty or clases_df.empty or instructores_df.empty:
        st.warning("Debe haber usuarios inscritos, clases programadas e instructores activos para agendar reservas.")
    else:
        with st.form("form_reserva", clear_on_submit=True):
            usr_sel = st.selectbox(
                "1. Selecciona tu Nombre (Cliente) *",
                usuarios_df["u_id_usuario"].tolist(),
                format_func=lambda x: usuarios_df[usuarios_df["u_id_usuario"] == x]["u_nombre_completo"].iloc[0]
            )

            col_c1, col_c2 = st.columns(2)
            with col_c1:
                cls_sel = st.selectbox(
                    "2. Selecciona la Clase y Horario *",
                    clases_df["c_id_clase"].tolist(),
                    format_func=lambda x: f"{clases_df[clases_df['c_id_clase'] == x]['c_nombre_clase'].iloc[0]} - {clases_df[clases_df['c_id_clase'] == x]['c_dia'].iloc[0]} ({clases_df[clases_df['c_id_clase'] == x]['c_horario'].iloc[0]})"
                )
            with col_c2:
                ins_sel = st.selectbox(
                    "3. Selecciona tu Instructor Preferido *",
                    instructores_df["i_id_instructor"].tolist(),
                    format_func=lambda x: f"{instructores_df[instructores_df['i_id_instructor'] == x]['i_nombre_completo'].iloc[0]} ({instructores_df[instructores_df['i_id_instructor'] == x]['i_especialidad'].iloc[0]})"
                )

            fecha_reserva = st.date_input("4. Fecha de la Clase", value=dt.date.today())
            
            btn_agendar = st.form_submit_button("🗓️ Confirmar Reserva")

        if btn_agendar:
            try:
                plan_usr = int(usuarios_df[usuarios_df["u_id_usuario"] == usr_sel]["u_id_plan"].iloc[0])
                precio_val = float(planes_df[planes_df["p_id_plan"] == plan_usr]["p_precio"].iloc[0])
                hora_clase = clases_df[clases_df["c_id_clase"] == cls_sel]["c_horario"].iloc[0]

                SQL_INS_RESERVA = f"""
                    INSERT INTO {ESQUEMA}.kardex_reserva (
                        r_id_usuario, r_id_clase, r_id_instructor, r_id_plan,
                        r_fecha_reserva, r_hora_reserva, r_precio, r_estado_asistencia, r_estado_reserva
                    ) VALUES (
                        :usr, :cls, :ins, :pln, :fec, :hor, :prc, 'no asistió', 'confirmada'
                    )
                """
                params_reserva = {
                    "usr": int(usr_sel),
                    "cls": int(cls_sel),
                    "ins": int(ins_sel),
                    "pln": plan_usr,
                    "fec": fecha_reserva,
                    "hor": hora_clase,
                    "prc": precio_val
                }
                reserva_id = insertar_con_id(SQL_INS_RESERVA, "r_id_reserva", params_reserva)
                st.success(f"🎉 ¡Reserva agendada exitosamente con el código #{reserva_id}!")
            except Exception as e:
                st.error(f"Error al agendar la reserva: {e}")

# -----------------------------------------------------------------
# VISTA 6: VER MIS RESERVAS
# -----------------------------------------------------------------
elif opcion_menu == "📋 Ver mis Reservas":
    st.header("📋 Historial de Reservas Agendadas")

    reservas_df = consultar(f"""
        SELECT kr.r_id_reserva AS id_reserva, u.u_nombre_completo AS cliente,
               c.c_nombre_clase AS clase, c.c_horario AS horario, i.i_nombre_completo AS instructor,
               pm.p_nombre_plan AS plan, kr.r_fecha_reserva AS fecha_reserva,
               kr.r_precio AS precio, kr.r_estado_reserva AS estado
        FROM {ESQUEMA}.kardex_reserva kr
        JOIN {ESQUEMA}.usuario u ON u.u_id_usuario = kr.r_id_usuario
        JOIN {ESQUEMA}.clases c ON c.c_id_clase = kr.r_id_clase
        JOIN {ESQUEMA}.instructor i ON i.i_id_instructor = kr.r_id_instructor
        JOIN {ESQUEMA}.plan_membresia pm ON pm.p_id_plan = kr.r_id_plan
        ORDER BY kr.r_id_reserva DESC
    """)

    if not reservas_df.empty:
        reservas_df["precio"] = reservas_df["precio"].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "$0.00")
        st.dataframe(reservas_df, use_container_width=True, hide_index=True)
    else:
        st.info("Aún no se han agendado reservas en el sistema.")
