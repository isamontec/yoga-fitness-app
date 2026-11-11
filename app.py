import datetime as dt
import oracledb
import pandas as pd
import streamlit as st

# Configuración inicial de la página
st.set_page_config(page_title="Lumina Zen Studio", layout="wide")

# Estilos personalizados (Girly, rosado pastel, lila y minimalista)
st.markdown(
    """
    <style>
    .banner {background: linear-gradient(90deg, #F48FB1, #E1BEE7 60%, #CE93D8); color:#fff;
             padding:1.5rem 2rem; border-radius:15px; margin-bottom:1.5rem; text-align: center;
             box-shadow: 0 4px 6px rgba(0,0,0,0.1);}
    .banner h1 {margin:0; font-size:2.8rem; color:#fff; font-family: 'Georgia', serif; letter-spacing: 2px;}
    .banner p {margin:0; opacity:.9; font-size:1.2rem; font-weight: 300; font-style: italic;}
    
    div[data-testid="stMetric"] {background:#FFF0F5; border:1px solid #F8BBD0; border-left:5px solid #D81B60;
                                 padding:.8rem 1rem; border-radius:10px;}
    
    /* Mensajes gigantes de éxito */
    .success-msg {
        background-color: #FCE4EC; color: #AD1457; padding: 20px; 
        border-radius: 12px; font-size: 22px; font-weight: bold; text-align: center;
        border: 2px dashed #F06292; margin: 20px 0;
    }
    
    /* Botones femeninos */
    .stButton>button {background-color: #F06292; color: white; border-radius: 20px; border: none; padding: 10px 24px;}
    .stButton>button:hover {background-color: #D81B60; color: white;}
    
    /* Descripción de ejercicios */
    .desc-box {background: #FAFAFA; border-left: 4px solid #CE93D8; padding: 15px; border-radius: 8px; margin-bottom: 10px;}
    .desc-title {color: #8E24AA; font-weight: bold; font-size: 1.1rem; margin-bottom: 5px;}
    
    /* Plan Premium Destacado */
    .premium-plan {background: linear-gradient(135deg, #FFF0F5, #FCE4EC); border: 2px solid #D81B60; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 20px;}
    .premium-plan h3 {color: #C2185B; margin-top: 0;}
    </style>
    <div class="banner">
        <h1>Lumina Zen Studio</h1>
        <p>Tu espacio seguro para sanar, tonificar y brillar desde adentro hacia afuera.</p>
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
    "Menú del Studio",
    ["Planes y Precios", "Clases y Horarios", "Instructores", "Inscribirse", "Agendar Reserva", "Ver mis Reservas", "📊 Panel de Administrador"]
)

# -----------------------------------------------------------------
# VISTA 1: PLANES, PRECIOS Y DESCRIPCIÓN DE CLASES
# -----------------------------------------------------------------
if opcion_menu == "Planes y Precios":
    st.header("Nuestros Planes y Disciplinas")
    
    st.markdown("""
        <div class="desc-box">
            <div class="desc-title">✨ Yoga & Vinyasa</div>
            Conecta cuerpo y mente a través de la respiración. Ideal para mejorar la flexibilidad, reducir el estrés y encontrar tu centro. Vinyasa ofrece secuencias más fluidas y dinámicas.
        </div>
        <div class="desc-box">
            <div class="desc-title">🔥 Hot Yoga & Hot Pilates</div>
            Practicados en un salón aclimatado. El calor ayuda a desintoxicar el cuerpo, profundizar los estiramientos y quemar calorías intensamente.
        </div>
        <div class="desc-box">
            <div class="desc-title">🩰 Barre</div>
            Una mezcla elegante de ballet, pilates y yoga. Utiliza la barra de ballet para realizar micromovimientos que tonifican y alargan los músculos sin impacto.
        </div>
        <div class="desc-box">
            <div class="desc-title">💫 Pilates & Pilates Reformer</div>
            Enfocado en fortalecer el "core" (centro del cuerpo). El Reformer utiliza una cama con poleas y resortes para crear resistencia, mejorando la postura, fuerza y alineación.
        </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    st.markdown("""
        <div class="premium-plan">
            <h3>⭐ PLAN RECOMENDADO: Premium Pilates & Full Studio ⭐</h3>
            <p>Acceso ilimitado a todas nuestras clases: Reformer, Vinyasa, Hot Pilates y Barre. La experiencia Lumina completa para tu transformación.</p>
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
    st.header("Horarios de Sesiones")
    clases_df = consultar(f"SELECT c_nombre_clase AS nombre_clase, c_tipo_clase AS disciplina, c_dia AS dia, c_horario AS horario, c_salon_clase AS salon FROM {ESQUEMA}.clases ORDER BY c_id_clase ASC")
    st.dataframe(clases_df, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------
# VISTA 3: INSTRUCTORES
# -----------------------------------------------------------------
elif opcion_menu == "Instructores":
    st.header("Nuestro Staff")
    instructores_df = consultar(f"SELECT i_nombre_completo AS nombre, i_especialidad AS especialidad, i_tipo_certificacion AS certificacion FROM {ESQUEMA}.instructor WHERE i_estado = 'activo' ORDER BY i_nombre_completo ASC")
    st.dataframe(instructores_df, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------
# VISTA 4: INSCRIBIRSE (NUEVO CLIENTE)
# -----------------------------------------------------------------
elif opcion_menu == "Inscribirse":
    st.header("Únete al Studio")
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
            # --- RANGO DE EDAD CORREGIDO: 1965 a 2009 ---
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
            st.warning("Completa los campos obligatorios.")
        else:
            try:
                SQL = f"INSERT INTO {ESQUEMA}.usuario (u_nombre_completo, u_id_plan, u_genero, u_estado, u_direccion_residencia, u_telefono, u_correo_electronico, u_condicion_medica, u_fecha_nacimiento) VALUES (:nom, :pln, :gen, 'activo', :direc, :tel, :cor, 'Ninguna', :fec)"
                p = {"nom": nombre.strip(), "pln": int(plan_elegido), "gen": genero, "direc": direccion.strip(), "tel": telefono.strip(), "cor": correo.strip(), "fec": fecha_nac}
                nuevo_id = insertar_con_id(SQL, "u_id_usuario", p)
                st.session_state["mi_id"] = nuevo_id
                
                st.balloons()
                st.markdown(f'<div class="success-msg">Inscripción Exitosa.<br>Tu ID de Cliente es: #{nuevo_id}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")

# -----------------------------------------------------------------
# VISTA 5: AGENDAR RESERVA (Lógica de Planes Premium)
# -----------------------------------------------------------------
elif opcion_menu == "Agendar Reserva":
    st.header("Agendamiento")
    
    id_default = st.session_state.get("mi_id", 12)
    id_ingresado = st.number_input("Ingresa tu ID de Cliente:", min_value=1, value=int(id_default), step=1)

    usuario_info = consultar(f"SELECT u.u_id_usuario, u.u_nombre_completo, u.u_id_plan, p.p_nombre_plan, p.p_tipo_clase, p.p_precio FROM {ESQUEMA}.usuario u JOIN {ESQUEMA}.plan_membresia p ON p.p_id_plan = u.u_id_plan WHERE u.u_id_usuario = {id_ingresado} AND u.u_estado = 'activo'")

    if usuario_info.empty:
        st.error("No se encontró el usuario. Inscríbete primero.")
    else:
        usr = usuario_info.iloc[0]
        nombre_plan = usr['p_nombre_plan'].lower()
        
        # VALIDACIÓN DEL PLAN PREMIUM
        es_premium = "premium" in nombre_plan or "pilates" in nombre_plan
        
        if es_premium:
            st.success(f"Hola {usr['u_nombre_completo']} | Tienes el **{usr['p_nombre_plan']}**. ¡Puedes reservar TODAS las disciplinas del Studio!")
            query_clases = f"SELECT c_id_clase, c_nombre_clase FROM {ESQUEMA}.clases"
            query_inst = f"SELECT i_id_instructor, i_nombre_completo FROM {ESQUEMA}.instructor WHERE i_estado = 'activo'"
        else:
            st.success(f"Hola {usr['u_nombre_completo']} | Tienes el **{usr['p_nombre_plan']}**. Puedes reservar clases de: {usr['p_tipo_clase'].title()}")
            query_clases = f"SELECT c_id_clase, c_nombre_clase FROM {ESQUEMA}.clases WHERE LOWER(c_tipo_clase) = '{usr['p_tipo_clase'].lower()}'"
            query_inst = f"SELECT i_id_instructor, i_nombre_completo FROM {ESQUEMA}.instructor WHERE LOWER(i_especialidad) LIKE '%{usr['p_tipo_clase'].lower()}%'"

        clases_perm = consultar(query_clases)
        instructores = consultar(query_inst)

        if clases_perm.empty:
            st.warning("No hay clases disponibles en este momento.")
        else:
            with st.form("form_reserva", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    cls_sel = st.selectbox("Selecciona la Clase", clases_perm["c_id_clase"].tolist(), format_func=lambda x: clases_perm[clases_perm['c_id_clase'] == x]['c_nombre_clase'].iloc[0])
                    dia_sel = st.selectbox("Día", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"])
                    
                    # SELECCIÓN DE HORA CON MULTIPLES OPCIONES
                    franja_sel = st.selectbox("Franja Horaria", ["Mañana (AM)", "Mediodía (PM)", "Tarde/Noche (PM)"])
                    
                    if franja_sel == "Mañana (AM)":
                        opciones_hora = ["06:00 AM", "08:00 AM", "10:00 AM"]
                    elif franja_sel == "Mediodía (PM)":
                        opciones_hora = ["12:00 PM", "02:00 PM"]
                    else:
                        opciones_hora = ["04:00 PM", "06:00 PM", "08:00 PM"]
                        
                    hora_sel = st.selectbox("Hora Exacta", opciones_hora)
                    
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
                    
                    st.balloons()
                    st.markdown(f'<div class="success-msg">¡Reserva Confirmada!<br>Código de Reserva: #{res_id}<br>Te esperamos el {dia_sel} a las {hora_sel}.</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error: {e}")

# -----------------------------------------------------------------
# VISTA 6: VER MIS RESERVAS (Solo las privadas del usuario)
# -----------------------------------------------------------------
elif opcion_menu == "Ver mis Reservas":
    st.header("Mi Historial de Reservas")
    
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
        st.success(f"Aquí tienes tus reservas, Cliente #{id_ingresado_historial}:")
        st.dataframe(historial, use_container_width=True, hide_index=True)
    else:
        st.info("Aún no tienes reservas agendadas con este ID.")

# -----------------------------------------------------------------
# VISTA 7: PANEL DE ADMINISTRADOR (Módulo Privado)
# -----------------------------------------------------------------
elif opcion_menu == "📊 Panel de Administrador":
    st.header("Acceso Privado Administrador")
    
    codigo_acceso = st.text_input("Ingresa el código PIN para acceder:", type="password")
    
    if codigo_acceso == "001":
        st.success("Acceso concedido.")
        st.write("---")
        st.subheader("Resumen de Ganancias y Reservas")
        
        # OBTENEMOS LOS TOTALES (Ingresos y Cantidad de Reservas)
        ganancias_query = f"""
            SELECT SUM(r_precio) as total_ingresos, COUNT(r_id_reserva) as total_reservas 
            FROM {ESQUEMA}.kardex_reserva
        """
        ganancias_data = consultar(ganancias_query)
        
        col_m1, col_m2 = st.columns(2)
        if not ganancias_data.empty:
            # Manejamos el caso en que la suma sea Nula (0 reservas)
            total_ingresos = ganancias_data.iloc[0]['total_ingresos']
            if pd.isna(total_ingresos):
                total_ingresos = 0.0
                
            total_reservas = ganancias_data.iloc[0]['total_reservas']
            
            col_m1.metric("Ingresos Totales (Mes)", f"${total_ingresos:,.2f}")
            col_m2.metric("Total Reservas Agendadas", int(total_reservas))
            
        st.write("---")
        st.subheader("Historial Completo de Reservas (Clientes y Pagos)")
        
        # TABLA DETALLADA DEL HISTORIAL
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
            # Formateamos la columna 'pago' para que se vea como moneda
            historial_admin["pago"] = historial_admin["pago"].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "$0.00")
            st.dataframe(historial_admin, use_container_width=True, hide_index=True)
        else:
            st.info("No hay reservas registradas en el sistema aún.")
            
    elif codigo_acceso:
        st.error("Código PIN incorrecto.")
