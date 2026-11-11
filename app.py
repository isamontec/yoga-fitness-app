import datetime as dt
import oracledb
import pandas as pd
import streamlit as st

# Configuración inicial de la página
st.set_page_config(page_title="Lumina Zen Studio", layout="wide")

# Estilos CSS Ultra Girly, Sofisticado y sin emojis
st.markdown(
    """
    <style>
    .banner {
        background: linear-gradient(135deg, #F48FB1, #F8BBD0 50%, #E1BEE7); 
        color: #4A148C; padding: 2rem 2.5rem; border-radius: 20px; 
        margin-bottom: 2rem; text-align: center;
        box-shadow: 0 8px 20px rgba(244, 143, 177, 0.3);
    }
    .banner h1 {margin: 0; font-size: 3rem; color: #4A148C; font-family: 'Georgia', serif; letter-spacing: 2px; font-weight: normal;}
    .banner p {margin: 5px 0 0 0; color: #6A1B9A; font-size: 1.25rem; font-weight: 300; font-style: italic;}
    
    div[data-testid="stMetric"] {
        background: #FFF0F5; border: 1px solid #F8BBD0; border-left: 6px solid #D81B60;
        padding: 1rem 1.2rem; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.02);
    }
    div[data-testid="stMetric"] label {color: #880E4F !important; font-weight: 600; font-size: 1.1rem !important;}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {color: #AD1457 !important; font-size: 2.5rem !important; font-weight: bold;}

    .success-msg {
        background-color: #FCE4EC; color: #AD1457; padding: 25px; 
        border-radius: 15px; font-size: 22px; font-weight: bold; text-align: center;
        border: 2px dashed #F06292; margin: 25px 0; box-shadow: 0 4px 15px rgba(240, 98, 146, 0.2);
    }
    
    .stButton>button {
        background-color: #F06292; color: white; border-radius: 25px; 
        border: none; padding: 12px 28px; font-weight: 600; letter-spacing: 1px;
        box-shadow: 0 4px 12px rgba(240, 98, 146, 0.4);
    }
    .stButton>button:hover {background-color: #D81B60; color: white;}
    
    .desc-box {
        background: #FFFFFF; border-left: 5px solid #F06292; padding: 18px; 
        border-radius: 12px; margin-bottom: 15px; box-shadow: 0 3px 10px rgba(0,0,0,0.04);
    }
    .desc-title {color: #C2185B; font-weight: bold; font-size: 1.2rem; margin-bottom: 6px; font-family: 'Georgia', serif;}
    
    .premium-plan {
        background: linear-gradient(135deg, #FFF0F5, #FCE4EC); 
        border: 2px solid #F06292; padding: 25px; border-radius: 15px; 
        text-align: center; margin-bottom: 25px; box-shadow: 0 5px 15px rgba(240, 98, 146, 0.15);
    }
    .premium-plan h3 {color: #AD1457; margin-top: 0; font-family: 'Georgia', serif;}
    </style>
    <div class="banner">
        <h1>Lumina Zen Studio</h1>
        <p>Tu santuario exclusivo de bienestar, pilates y armonía corporal.</p>
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
        oracledb.init_oracle_client(lib_dir=s["lib_dir"], config_dir=s["config_dir"])
        return oracledb.connect(user=s["user"], password=s["password"], dsn=s["dsn"])
    
    kwargs = {}
    if s.get("config_dir") and not str(s.get("config_dir")).startswith("/app"):
        kwargs["config_dir"] = s.get("config_dir")
        kwargs["wallet_location"] = s.get("wallet_location", s.get("config_dir"))
    if s.get("wallet_password"):
        kwargs["wallet_password"] = s.get("wallet_password")
        
    return oracledb.connect(user=s["user"], password=s["password"], dsn=s["dsn"], **kwargs)

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
    "Menú Principal",
    ["Planes y Precios", "Clases y Horarios", "Instructores", "Inscribirse", "Agendar Reserva", "Ver mis Reservas", "Panel de Administrador"]
)

# -----------------------------------------------------------------
# VISTA 1: PLANES Y PRECIOS
# -----------------------------------------------------------------
if opcion_menu == "Planes y Precios":
    st.header("Explora Nuestras Disciplinas y Planes")
    st.markdown("Conoce cada experiencia diseñada especialmente para tu bienestar integral:")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown("""
            <div class="desc-box">
                <div class="desc-title">Yoga y Vinyasa Flow</div>
                Conecta cuerpo y mente mediante respiración consciente. Ideal para flexibilidad, paz interior y fluidez corporal.
            </div>
            <div class="desc-box">
                <div class="desc-title">Hot Yoga y Hot Pilates</div>
                Sesiones en estudio aclimatado para desintoxicar profundamente, ganar elasticidad y acelerar la quema calórica.
            </div>
        """, unsafe_allow_html=True)
    with col_d2:
        st.markdown("""
            <div class="desc-box">
                <div class="desc-title">Barre Studio</div>
                Fusión elegante de ballet, pilates y yoga en barra fija para tonificar y estilizar sin impacto articular.
            </div>
            <div class="desc-box">
                <div class="desc-title">Pilates Reformer y Mat</div>
                Fortalecimiento absoluto del centro corporal con camas de resortes y poleas que mejoran la postura.
            </div>
        """, unsafe_allow_html=True)
    
    st.write("---")
    
    st.markdown("""
        <div class="premium-plan">
            <h3>PLAN RECOMENDADO: Premium Pilates y Full Studio</h3>
            <p>Acceso total e ilimitado a todas nuestras clases de Reformer, Hot Pilates, Vinyasa y Barre. La experiencia Lumina definitiva.</p>
        </div>
    """, unsafe_allow_html=True)
    
    planes_df = consultar(f"SELECT p_id_plan AS id, p_nombre_plan AS plan, p_tipo_clase AS disciplina, p_duracion_plan AS duracion_dias, p_precio AS precio FROM {ESQUEMA}.plan_membresia ORDER BY p_precio DESC")

    if not planes_df.empty:
        planes_df["precio"] = planes_df["precio"].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "$0.00")
        st.dataframe(planes_df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay planes registrados.")

# -----------------------------------------------------------------
# VISTA 2: CLASES Y HORARIOS
# -----------------------------------------------------------------
elif opcion_menu == "Clases y Horarios":
    st.header("Horarios de Clases Programadas")
    clases_df = consultar(f"SELECT c_nombre_clase AS nombre_clase, c_tipo_clase AS disciplina, c_dia AS dia, c_horario AS horario, c_salon_clase AS salon FROM {ESQUEMA}.clases ORDER BY c_id_clase ASC")
    st.dataframe(clases_df, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------
# VISTA 3: INSTRUCTORES
# -----------------------------------------------------------------
elif opcion_menu == "Instructores":
    st.header("Nuestro Staff de Profesionales")
    instructores_df = consultar(f"SELECT i_nombre_completo AS nombre, i_especialidad AS especialidad, i_tipo_certificacion AS certificacion FROM {ESQUEMA}.instructor WHERE i_estado = 'activo' ORDER BY i_nombre_completo ASC")
    st.dataframe(instructores_df, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------
# VISTA 4: INSCRIBIRSE (NUEVO CLIENTE)
# -----------------------------------------------------------------
elif opcion_menu == "Inscribirse":
    st.header("Registro de Nueva Alumna")
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
            # RANGO DE EDAD ESTRICTO: 1965 a 2009
            fecha_nac = st.date_input(
                "Fecha de Nacimiento *",
                value=dt.date(1995, 1, 1),
                min_value=dt.date(1965, 1, 1),
                max_value=dt.date(2009, 12, 31)
            )
            plan_elegido = st.selectbox("Selecciona tu Plan", planes_op["p_id_plan"].tolist(), format_func=lambda x: f"{planes_op[planes_op['p_id_plan'] == x]['p_nombre_plan'].iloc[0]}")

        btn_inscribir = st.form_submit_button("Completar Inscripción")

    if btn_inscribir:
        if not nombre.strip() or not correo.strip():
            st.warning("Por favor completa los campos obligatorios.")
        else:
            try:
                SQL = f"INSERT INTO {ESQUEMA}.usuario (u_nombre_completo, u_id_plan, u_genero, u_estado, u_direccion_residencia, u_telefono, u_correo_electronico, u_condicion_medica, u_fecha_nacimiento) VALUES (:nom, :pln, :gen, 'activo', :direc, :tel, :cor, 'Ninguna', :fec)"
                p = {"nom": nombre.strip(), "pln": int(plan_elegido), "gen": genero, "direc": direccion.strip(), "tel": telefono.strip(), "cor": correo.strip(), "fec": fecha_nac}
                nuevo_id = insertar_con_id(SQL, "u_id_usuario", p)
                st.session_state["mi_id"] = nuevo_id
                
                st.balloons()
                st.markdown(f'<div class="success-msg">¡Inscripción Exitosa!<br>Tu ID de Cliente es: #{nuevo_id}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error al registrar: {e}")

# -----------------------------------------------------------------
# VISTA 5: AGENDAR RESERVA (Horarios estrictos PM corregidos)
# -----------------------------------------------------------------
elif opcion_menu == "Agendar Reserva":
    st.header("Reserva tu Clase Favorita")
    
    id_default = st.session_state.get("mi_id", 12)
    id_ingresado = st.number_input("Ingresa tu ID de Cliente:", min_value=1, value=int(id_default), step=1)

    usuario_info = consultar(f"SELECT u.u_id_usuario, u.u_nombre_completo, u.u_id_plan, p.p_nombre_plan, p.p_tipo_clase, p.p_precio FROM {ESQUEMA}.usuario u JOIN {ESQUEMA}.plan_membresia p ON p.p_id_plan = u.u_id_plan WHERE u.u_id_usuario = {id_ingresado} AND u.u_estado = 'activo'")

    if usuario_info.empty:
        st.error("No se encontró el usuario. Inscríbete primero.")
    else:
        usr = usuario_info.iloc[0]
        nombre_plan = usr['p_nombre_plan'].lower()
        
        es_premium = "premium" in nombre_plan or "pilates" in nombre_plan
        
        if es_premium:
            st.success(f"Bienvenida, {usr['u_nombre_completo']} | Tienes el **{usr['p_nombre_plan']}**. ¡Puedes reservar TODAS las disciplinas!")
            query_clases = f"SELECT c_id_clase, c_nombre_clase FROM {ESQUEMA}.clases"
            query_inst = f"SELECT i_id_instructor, i_nombre_completo FROM {ESQUEMA}.instructor WHERE i_estado = 'activo'"
        else:
            st.success(f"Bienvenida, {usr['u_nombre_completo']} | Tienes el **{usr['p_nombre_plan']}**. Disciplina permitida: {usr['p_tipo_clase'].title()}")
            query_clases = f"SELECT c_id_clase, c_nombre_clase FROM {ESQUEMA}.clases WHERE LOWER(c_tipo_clase) = '{usr['p_tipo_clase'].lower()}'"
            query_inst = f"SELECT i_id_instructor, i_nombre_completo FROM {ESQUEMA}.instructor WHERE LOWER(i_especialidad) LIKE '%{usr['p_tipo_clase'].lower()}%'"

        clases_perm = consultar(query_clases)
        instructores = consultar(query_inst)

        if clases_perm.empty:
            st.warning("No hay clases disponibles para este plan.")
        else:
            with st.form("form_reserva", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    cls_sel = st.selectbox("Selecciona la Clase", clases_perm["c_id_clase"].tolist(), format_func=lambda x: clases_perm[clases_perm['c_id_clase'] == x]['c_nombre_clase'].iloc[0])
                    dia_sel = st.selectbox("Día de la Semana", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"])
                    
                    # FRANJA HORARIA Y HORAS EXACTAS ESTRICTAS SEGÚN LA SELECCIÓN
                    franja_sel = st.selectbox("Franja Horaria", ["Mañana (AM)", "Tarde (PM)", "Tarde/Noche (PM)"])
                    
                    if franja_sel == "Mañana (AM)":
                        opciones_hora = ["06:00 AM", "08:00 AM", "10:00 AM"]
                    elif franja_sel == "Tarde (PM)":
                        opciones_hora = ["02:00 PM", "03:30 PM", "05:00 PM"]
                    else:
                        opciones_hora = ["06:00 PM", "07:30 PM", "09:00 PM"]
                        
                    hora_sel = st.selectbox("Hora Exacta", opciones_hora)
                    
                with col2:
                    if not instructores.empty:
                        ins_sel = st.selectbox("Instructor/a", instructores["i_id_instructor"].tolist(), format_func=lambda x: instructores[instructores['i_id_instructor'] == x]['i_nombre_completo'].iloc[0])
                    else:
                        ins_sel = st.selectbox("Instructor (General)", [1])
                    fecha_sel = st.date_input("Fecha Exacta", value=dt.date.today())

                btn_agendar = st.form_submit_button("Confirmar Reserva de Cupo")

            if btn_agendar:
                try:
                    SQL = f"INSERT INTO {ESQUEMA}.kardex_reserva (r_id_usuario, r_id_clase, r_id_instructor, r_id_plan, r_fecha_reserva, r_hora_reserva, r_precio, r_estado_asistencia, r_estado_reserva) VALUES (:usr, :cls, :ins, :pln, :fec, :hor, :prc, 'no asistió', 'confirmada')"
                    p = {"usr": int(usr['u_id_usuario']), "cls": int(cls_sel), "ins": int(ins_sel), "pln": int(usr['u_id_plan']), "fec": fecha_sel, "hor": hora_sel, "prc": float(usr['p_precio'])}
                    res_id = insertar_con_id(SQL, "r_id_reserva", p)
                    
                    st.balloons()
                    st.markdown(f'<div class="success-msg">¡Reserva Confirmada con Éxito!<br>Código de Reserva: #{res_id}<br>Te esperamos el {dia_sel} a las {hora_sel}.</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error al agendar: {e}")

# -----------------------------------------------------------------
# VISTA 6: VER MIS RESERVAS (Privadas del usuario)
# -----------------------------------------------------------------
elif opcion_menu == "Ver mis Reservas":
    st.header("Mis Reservas Activas")
    
    id_default = st.session_state.get("mi_id", 12)
    id_ingresado_historial = st.number_input("Ingresa tu ID de Cliente para ver tus reservas:", min_value=1, value=int(id_default), step=1)
    
    historial = consultar(f"""
        SELECT kr.r_id_reserva AS id_reserva, c.c_nombre_clase AS clase, kr.r_hora_reserva AS hora, i.i_nombre_completo AS instructor 
        FROM {ESQUEMA}.kardex_reserva kr 
        JOIN {ESQUEMA}.clases c ON c.c_id_clase = kr.r_id_clase 
        JOIN {ESQUEMA}.instructor i ON i.i_id_instructor = kr.r_id_instructor 
        WHERE kr.r_id_usuario = {id_ingresado_historial}
        ORDER BY kr.r_id_reserva DESC
    """)
    
    if not historial.empty:
        st.success(f"Tus reservas registradas, Cliente #{id_ingresado_historial}:")
        st.dataframe(historial, use_container_width=True, hide_index=True)
    else:
        st.info("Aún no tienes reservas agendadas con este ID.")

# -----------------------------------------------------------------
# VISTA 7: PANEL DE ADMINISTRADOR (PIN: 001)
# -----------------------------------------------------------------
elif opcion_menu == "Panel de Administrador":
    st.header("Panel de Control de Propietaria")
    
    codigo_acceso = st.text_input("Ingresa el PIN de Administradora (001):", type="password")
    
    if codigo_acceso == "001":
        st.success("¡Acceso autorizado!")
        st.write("---")
        st.subheader("Resumen Financiero y Ocupación")
        
        ganancias_query = f"""
            SELECT SUM(r_precio) as total_ingresos, COUNT(r_id_reserva) as total_reservas 
            FROM {ESQUEMA}.kardex_reserva
        """
        ganancias_data = consultar(ganancias_query)
        
        col_m1, col_m2 = st.columns(2)
        if not ganancias_data.empty:
            total_ingresos = ganancias_data.iloc[0]['total_ingresos']
            if pd.isna(total_ingresos):
                total_ingresos = 0.0
                
            total_reservas = ganancias_data.iloc[0]['total_reservas']
            
            col_m1.metric("Ingresos Totales (Mes)", f"${total_ingresos:,.2f}")
            col_m2.metric("Total Reservas Agendadas", int(total_reservas))
            
        st.write("---")
        st.subheader("Historial Detallado de Clientes y Pagos")
        
        historial_admin = consultar(f"""
            SELECT kr.r_id_reserva AS id_reserva, 
                   TO_CHAR(kr.r_fecha_reserva, 'YYYY-MM-DD') AS fecha, 
                   u.u_nombre_completo AS cliente, 
                   c.c_nombre_clase AS clase, 
                   kr.r_precio AS pago, 
                   kr.r_estado_reserva AS estado 
            FROM {ESQUEMA}.kardex_reserva kr 
            JOIN {ESQUEMA}.usuario u ON u.u_id_usuario = kr.r_id_usuario 
            JOIN {ESQUEMA}.clases c ON c.c_id_clase = kr.r_id_clase 
            ORDER BY kr.r_id_reserva DESC
        """)
        
        if not historial_admin.empty:
            historial_admin["pago"] = historial_admin["pago"].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "$0.00")
            st.dataframe(historial_admin, use_container_width=True, hide_index=True)
        else:
            st.info("No hay reservas registradas en el sistema aún.")
            
    elif codigo_acceso:
        st.error("PIN incorrecto.")
