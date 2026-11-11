----------------------------- QUIERES ------------------------
-- ---------------------- CONSULTAS DE ANALÍTICA ----------------------

SELECT 
    u.u_id_usuario AS id_usuario,
    u.u_nombre_completo AS nombre_cliente,
    u.u_correo_electronico AS correo,
    u.u_condicion_medica AS condicion_medica,
    pm.p_nombre_plan AS plan_actual
FROM usuario u
INNER JOIN plan_membresia pm ON u.u_id_plan = pm.p_id_plan
WHERE u.u_estado = 'activo';

-- Consulta 1: Informe general de reservas activas cruzando todas las entidades
SELECT 
    kr.r_id_reserva AS id_reserva,
    u.u_nombre_completo AS cliente,
    c.c_nombre_clase AS clase,
    c.c_modalidad AS modalidad,
    i.i_nombre_completo AS instructor,
    pm.p_nombre_plan AS plan_membresia,
    kr.r_fecha_reserva AS fecha,
    kr.r_estado_reserva AS estado_reserva
FROM kardex_reserva kr
INNER JOIN usuario u ON kr.r_id_usuario = u.u_id_usuario
INNER JOIN clases c ON kr.r_id_clase = c.c_id_clase
INNER JOIN instructor i ON kr.r_id_instructor = i.i_id_instructor
INNER JOIN plan_membresia pm ON kr.r_id_plan = pm.p_id_plan
ORDER BY kr.r_fecha_reserva DESC;


-- Consulta 2: Total de reservas e ingresos generados por tipo de clase
SELECT 
    c.c_tipo_clase AS tipo_clase,
    COUNT(kr.r_id_reserva) AS total_reservas,
    NVL(SUM(kr.r_precio), 0) AS ingresos_totales
FROM clases c
LEFT JOIN kardex_reserva kr ON c.c_id_clase = kr.r_id_clase
GROUP BY c.c_tipo_clase
ORDER BY ingresos_totales DESC;


-- Consulta 3: Usuarios activos con alguna condición médica registrada
-- Consulta 3: Usuarios activos y su condición médica
SELECT 
    u.u_id_usuario AS id_usuario,
    u.u_nombre_completo AS nombre_cliente,
    u.u_correo_electronico AS correo,
    u.u_condicion_medica AS condicion_medica,
    pm.p_nombre_plan AS plan_actual
FROM usuario u
INNER JOIN plan_membresia pm ON u.u_id_plan = pm.p_id_plan
WHERE u.u_estado = 'activo';


SELECT u_id_usuario, u_nombre_completo, u_id_plan, u_estado FROM usuario;
