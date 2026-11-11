import datetime as dt
import oracledb
import pandas as pd
import streamlit as st

# Configuración inicial de la página
st.set_page_config(page_title="Lumina Zen Studio", layout="wide")

# Estilos personalizados (Rosados, minimalista y mensajes grandes)
st.markdown(
    """
    <style>
    .banner {background: linear-gradient(90deg, #F06292, #E91E63 60%, #C2185B); color:#fff;
             padding:1.2rem 1.8rem; border-radius:12px; margin-bottom:1.5rem;}
    .banner h1 {margin:0; font-size:2.2rem; color:#fff; font-weight: 300;}
    .banner p {margin:0; opacity:.9; font-size:1.1rem; font-weight: 300;}
    
    div[data-testid="stMetric"] {background:#FCE4EC; border:1px solid #F8BBD0; border-left:5px solid #E91E63;
                                 padding:.6rem .9rem; border-radius:8px;}
    
    /* Mensajes gigantes de éxito */
    .success-msg {
        background-color: #D1C4E9; color: #4A148C; padding: 25px; 
        border-radius: 10px; font-size: 24px; font-weight: bold; text-align: center;
        border: 2px solid #7E57C2; margin-top: 20px; margin-bottom: 20px;
    }
    
    .stButton>button {background-color: #E91E63; color: white; border-radius: 8px;}
    .stButton>button:hover {background-color: #C2185B; border-color: #C2185B;}
    </style>
    <div class="banner">
        <h1>Lumina Zen Studio</h1>
        <p>Encuentra tu equilibrio. Planes de membresía, clases y reservas en línea.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

ESQUEMA = "ADMIN"

# ---------------- 1. Conexión a Oracle Cloud ----------------

@st.cache_resource
def conectar():
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
        user=s["user"], password=s["password"], dsn=s["dsn"], **kwargs
    )

try:
    conn = conectar()
except Exception as err:
    st.error(f"Error conectando a la base de datos Oracle: {err}")
    st.stop()


# ---------------- 2. Funciones SQL ----------------

def consultar(sql, params=None):
    df = pd.read_sql(sql, conn, params=params)
    df.columns = [c.lower() for c in df.columns]
    return df

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


# ---------------- 3. Menú Principal ----------------

opcion_menu = st.sidebar.radio(
    "Navegación",
    ["Planes y Precios", "Clases y Horarios", "Instructores", "Inscribirse", "Agendar Reserva", "Ver mis Reservas"]
)

# -----------------------------------------------------------------
# VISTA 1: PLANES Y PRECIOS
# -----------------------------------------------------------------
if opcion_menu == "Planes y Precios":
    st.header("Planes de Membresía")
    planes_df = consultar(f"SELECT p_id_plan AS id, p_nombre_plan AS plan, p_tipo_clase AS disciplina, p_duracion_plan AS duracion_dias, p_precio AS precio FROM {ESQUEMA}.plan_membresia ORDER BY p_precio ASC")

    if not planes_df.empty:
        planes_df["precio"] = planes_df["precio"].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "$0.00")
        st.dataframe(planes_df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay planes registrados.")

# -----------------------------------------------------------------
# VISTA 2: CLASES Y HORARIOS
# -----------------------------------------------------------------
elif opcion_menu == "Clases y Horarios":
    st.header("Clases Programadas")
    clases_df = consultar(f"SELECT c_nombre_clase AS nombre_clase, c_tipo_clase AS disciplina, c_dia AS dia, c_horario AS horario, c_salon_clase AS salon FROM {ESQUEMA}.clases ORDER BY c_id_clase ASC")
    st.dataframe(clases_df, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------
# VISTA 3: INSTRUCTORES
# -----------------------------------------------------------------
elif opcion_menu == "Instructores":
    st.header("Nuestro Equipo")
    instructores_df = consultar(f"SELECT i_nombre_completo AS nombre, i_especialidad AS especialidad, i_tipo_certificacion AS certificacion FROM {ESQUEMA}.instructor WHERE i_estado = 'activo' ORDER BY i_nombre_completo ASC")
    st.dataframe(instructores_df, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------
# VISTA 4: INSCRIBIRSE (NUEVO CLIENTE)
# -----------------------------------------------------------------
elif opcion_menu == "Inscribirse":
    st.header("Formulario de Inscripción")
    planes_op = consultar(f"SELECT p_id_plan, p_nombre_plan, p_precio FROM {ESQUEMA}.plan_membresia")

    with st.form("form_inscripcion", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            nombre = st.text_input("Nombre Completo *")
            correo = st.text_input("Correo Electrónico *")
            telefono = st.text_input("Teléfono *")
            genero = st.selectbox("Género", ["femenino", "masculino", "otro"])
        with col_b:
            direccion = st.text_input("Dirección")
            # EDAD HASTA 1960
            fecha_nac = st.date_input(
                "Fecha de Nacimiento *",
                value=dt.date(1995, 1, 1),
                min_value=dt.date(1960, 1, 1),
                max_value=dt.date(2009, 12, 31)
            )
            plan_elegido = st.selectbox("Selecciona tu Plan", planes_op["p_id_plan"].tolist(), format_func=lambda x: f"{planes_op[planes_op['p_id_plan'] == x]['p_nombre_plan'].iloc[0]}")

        btn_inscribir = st.form_submit_button("Completar Inscripción")

    if btn_inscribir:
        if not nombre.strip() or not correo.strip():
            st.warning("Completa los campos obligatorios.")
        else:
            try:
                SQL = f"INSERT INTO {ESQUEMA}.usuario (u_nombre_completo, u_id_plan, u_genero, u_estado, u_direccion_residencia, u_telefono, u_correo_electronico, u_condicion_medica, u_fecha_nacimiento) VALUES (:nom, :pln, :gen, 'activo', :direc, :tel, :cor, 'Ninguna', :fec)"
                p = {"nom": nombre.strip(), "pln": int(plan_elegido), "gen": genero, "direc": direccion.strip(), "tel": telefono.strip(), "cor": correo.strip(), "fec": fecha_nac}
                nuevo_id = insertar_con_id(SQL, "u_id_usuario", p)
                st.session_state["mi_id"] = nuevo_id
                
                # MENSAJE GIGANTE DE CONFIRMACIÓN
                st.balloons()
                st.markdown(f'<div class="success-msg">Inscripción Exitosa.<br>Tu ID de Cliente es: #{nuevo_id}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")

# -----------------------------------------------------------------
# VISTA 5: AGENDAR RESERVA (Horarios Mejorados)
# -----------------------------------------------------------------
elif opcion_menu == "Agendar Reserva":
    st.header("Agendamiento de Clases")
    
    id_default = st.session_state.get("mi_id", 12)
    id_ingresado = st.number_input("Ingresa tu ID de Cliente:", min_value=1, value=int(id_default), step=1)

    usuario_info = consultar(f"SELECT u.u_id_usuario, u.u_nombre_completo, u.u_id_plan, p.p_nombre_plan, p.p_tipo_clase, p.p_precio FROM {ESQUEMA}.usuario u JOIN {ESQUEMA}.plan_membresia p ON p.p_id_plan = u.u_id_plan WHERE u.u_id_usuario = {id_ingresado} AND u.u_estado = 'activo'")

    if usuario_info.empty:
        st.error("No se encontró el usuario. Inscríbete primero.")
    else:
        usr = usuario_info.iloc[0]
        st.success(f"Cliente: {usr['u_nombre_completo']} | Disciplina Permitida: {usr['p_tipo_clase'].title()}")

        clases_perm = consultar(f"SELECT c_id_clase, c_nombre_clase FROM {ESQUEMA}.clases WHERE LOWER(c_tipo_clase) = '{usr['p_tipo_clase'].lower()}'")
        instructores = consultar(f"SELECT i_id_instructor, i_nombre_completo FROM {ESQUEMA}.instructor WHERE LOWER(i_especialidad) LIKE '%{usr['p_tipo_clase'].lower()}%'")

        if clases_perm.empty:
            st.warning("No hay clases para esta disciplina.")
        else:
            with st.form("form_reserva", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    cls_sel = st.selectbox("Clase", clases_perm["c_id_clase"].tolist(), format_func=lambda x: clases_perm[clases_perm['c_id_clase'] == x]['c_nombre_clase'].iloc[0])
                    # SELECCIÓN PRECISA DE DÍA Y HORA
                    dia_sel = st.selectbox("Día", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"])
                    hora_sel = st.selectbox("Hora", ["06:00 AM", "08:00 AM", "10:00 AM", "05:00 PM", "06:00 PM", "08:00 PM"])
                with col2:
                    if not instructores.empty:
                        ins_sel = st.selectbox("Instructor", instructores["i_id_instructor"].tolist(), format_func=lambda x: instructores[instructores['i_id_instructor'] == x]['i_nombre_completo'].iloc[0])
                    else:
                        ins_sel = st.selectbox("Instructor (General)", [1])
                    fecha_sel = st.date_input("Fecha Exacta", value=dt.date.today())

                btn_agendar = st.form_submit_button("Confirmar Reserva")

            if btn_agendar:
                try:
                    SQL = f"INSERT INTO {ESQUEMA}.kardex_reserva (r_id_usuario, r_id_clase, r_id_instructor, r_id_plan, r_fecha_reserva, r_hora_reserva, r_precio, r_estado_asistencia, r_estado_reserva) VALUES (:usr, :cls, :ins, :pln, :fec, :hor, :prc, 'no asistió', 'confirmada')"
                    p = {"usr": int(usr['u_id_usuario']), "cls": int(cls_sel), "ins": int(ins_sel), "pln": int(usr['u_id_plan']), "fec": fecha_sel, "hor": hora_sel, "prc": float(usr['p_precio'])}
                    res_id = insertar_con_id(SQL, "r_id_reserva", p)
                    
                    # MENSAJE GIGANTE DE CONFIRMACIÓN
                    st.balloons()
                    st.markdown(f'<div class="success-msg">Reserva Confirmada.<br>Tu ID de Reserva es: #{res_id}<br>Te esperamos el {dia_sel} a las {hora_sel}.</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error: {e}")

# -----------------------------------------------------------------
# VISTA 6: VER RESERVAS
# -----------------------------------------------------------------
elif opcion_menu == "Ver mis Reservas":
    st.header("Historial de Reservas")
    historial = consultar(f"SELECT kr.r_id_reserva AS id_reserva, u.u_nombre_completo AS cliente, c.c_nombre_clase AS clase, kr.r_hora_reserva AS hora, i.i_nombre_completo AS instructor FROM {ESQUEMA}.kardex_reserva kr JOIN {ESQUEMA}.usuario u ON u.u_id_usuario = kr.r_id_usuario JOIN {ESQUEMA}.clases c ON c.c_id_clase = kr.r_id_clase JOIN {ESQUEMA}.instructor i ON i.i_id_instructor = kr.r_id_instructor ORDER BY kr.r_id_reserva DESC")
    st.dataframe(historial, use_container_width=True, hide_index=True)
