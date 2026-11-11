-- =====================================================
-- INSERCIÓN CORREGIDA - ESTUDIO DE YOGA (10 FILAS)

-- 1. PLAN MEMBRESIA (3 Planes)
INSERT INTO plan_membresia (p_id_plan, p_nombre_plan, p_duracion_plan, p_fecha_inicio, p_fecha_finalizacion, p_limite_clases, p_tipo_clase, p_precio, p_precio_descuento, p_cantidad_planes, p_estado) 
VALUES (1, 'Plan Yoga Total', 30, TO_DATE('2026-01-01','YYYY-MM-DD'), TO_DATE('2026-12-31','YYYY-MM-DD'), 12, 'yoga', 150000.00, 120000.00, 50, 'activo');

INSERT INTO plan_membresia (p_id_plan, p_nombre_plan, p_duracion_plan, p_fecha_inicio, p_fecha_finalizacion, p_limite_clases, p_tipo_clase, p_precio, p_precio_descuento, p_cantidad_planes, p_estado) 
VALUES (2, 'Plan Pilates Premium', 60, TO_DATE('2026-01-01','YYYY-MM-DD'), TO_DATE('2026-12-31','YYYY-MM-DD'), 0, 'pilates', 250000.00, NULL, 30, 'disponible');

INSERT INTO plan_membresia (p_id_plan, p_nombre_plan, p_duracion_plan, p_fecha_inicio, p_fecha_finalizacion, p_limite_clases, p_tipo_clase, p_precio, p_precio_descuento, p_cantidad_planes, p_estado) 
VALUES (3, 'Plan Barre Flex', 30, TO_DATE('2026-01-01','YYYY-MM-DD'), TO_DATE('2026-12-31','YYYY-MM-DD'), 8, 'barre', 180000.00, 160000.00, 20, 'activo');


-- 2. INSTRUCTOR (4 Instructores)
INSERT INTO instructor (i_id_instructor, i_nombre_completo, i_especialidad, i_tipo_contrato, i_cantidad_certificaciones, i_tipo_certificacion, i_estado) 
VALUES (101, 'Ana María Gómez', 'yoga', 'tiempo completo', 3, 'Certificación Hatha Yoga 200h', 'activo');

INSERT INTO instructor (i_id_instructor, i_nombre_completo, i_especialidad, i_tipo_contrato, i_cantidad_certificaciones, i_tipo_certificacion, i_estado) 
VALUES (102, 'Carlos Ruiz', 'pilates', 'medio tiempo', 2, 'Certificación Pilates Mat', 'activo');

INSERT INTO instructor (i_id_instructor, i_nombre_completo, i_especialidad, i_tipo_contrato, i_cantidad_certificaciones, i_tipo_certificacion, i_estado) 
VALUES (103, 'Sofía Ramírez', 'barre', 'cátedra', 1, 'Certificación Barre Intensity', 'activo');

INSERT INTO instructor (i_id_instructor, i_nombre_completo, i_especialidad, i_tipo_contrato, i_cantidad_certificaciones, i_tipo_certificacion, i_estado) 
VALUES (104, 'David Morales', 'multidisciplinario', 'tiempo completo', 4, 'Certificación Yoga & Pilates Master', 'activo');


-- 3. CLASES (5 Clases)
INSERT INTO clases (c_id_clase, c_nombre_clase, c_tipo_clase, c_dia, c_horario, c_salon_clase, c_cupo_max, c_intensidad, c_modalidad, c_estado) 
VALUES (201, 'Hatha Yoga Matutino', 'yoga', 'lunes', '07:00 AM', 'Salón A', 15, 'principiante', 'mat', 'programada');

INSERT INTO clases (c_id_clase, c_nombre_clase, c_tipo_clase, c_dia, c_horario, c_salon_clase, c_cupo_max, c_intensidad, c_modalidad, c_estado) 
VALUES (202, 'Pilates Reformer Tarde', 'pilates', 'miércoles', '05:00 PM', 'Salón B', 10, 'intermedio', 'reforma', 'programada');

INSERT INTO clases (c_id_clase, c_nombre_clase, c_tipo_clase, c_dia, c_horario, c_salon_clase, c_cupo_max, c_intensidad, c_modalidad, c_estado) 
VALUES (203, 'Hot Yoga Nocturno', 'yoga', 'martes', '08:00 PM', 'Salón A', 12, 'avanzado', 'hot', 'programada');

INSERT INTO clases (c_id_clase, c_nombre_clase, c_tipo_clase, c_dia, c_horario, c_salon_clase, c_cupo_max, c_intensidad, c_modalidad, c_estado) 
VALUES (204, 'Barre Fitness Express', 'barre', 'jueves', '06:00 PM', 'Salón C', 14, 'intermedio', 'normal', 'programada');

INSERT INTO clases (c_id_clase, c_nombre_clase, c_tipo_clase, c_dia, c_horario, c_salon_clase, c_cupo_max, c_intensidad, c_modalidad, c_estado) 
VALUES (205, 'Vinyasa Flow Sábado', 'yoga', 'sabado', '09:00 AM', 'Salón A', 18, 'principiante', 'mat', 'programada');


-- 4. USUARIOS (10 Usuarios)
INSERT INTO usuario (u_id_usuario, u_nombre_completo, u_id_plan, u_genero, u_estado, u_direccion_residencia, u_telefono, u_correo_electronico, u_condicion_medica, u_fecha_nacimiento) 
VALUES (1, 'Laura Fernández', 1, 'femenino', 'activo', 'Calle 10 # 45-12', '3001234567', 'laura@email.com', 'Ninguna', TO_DATE('1995-04-15','YYYY-MM-DD'));

INSERT INTO usuario (u_id_usuario, u_nombre_completo, u_id_plan, u_genero, u_estado, u_direccion_residencia, u_telefono, u_correo_electronico, u_condicion_medica, u_fecha_nacimiento) 
VALUES (2, 'Julian Martínez', 2, 'masculino', 'activo', 'Carrera 7 # 80-20', '3159876543', 'julian@email.com', 'Molestia rodilla derecha', TO_DATE('1990-08-22','YYYY-MM-DD'));

INSERT INTO usuario (u_id_usuario, u_nombre_completo, u_id_plan, u_genero, u_estado, u_direccion_residencia, u_telefono, u_correo_electronico, u_condicion_medica, u_fecha_nacimiento) 
VALUES (3, 'Camila Ospina', 1, 'femenino', 'activo', 'Avenida 33 # 12-05', '3014445566', 'camila@email.com', 'Hipertensión controlada', TO_DATE('1988-11-03','YYYY-MM-DD'));

INSERT INTO usuario (u_id_usuario, u_nombre_completo, u_id_plan, u_genero, u_estado, u_direccion_residencia, u_telefono, u_correo_electronico, u_condicion_medica, u_fecha_nacimiento) 
VALUES (4, 'Mateo Gómez', 3, 'masculino', 'activo', 'Calle 50 # 20-15', '3108889900', 'mateo@email.com', 'Ninguna', TO_DATE('1998-02-18','YYYY-MM-DD'));

INSERT INTO usuario (u_id_usuario, u_nombre_completo, u_id_plan, u_genero, u_estado, u_direccion_residencia, u_telefono, u_correo_electronico, u_condicion_medica, u_fecha_nacimiento) 
VALUES (5, 'Daniela Torres', 2, 'femenino', 'activo', 'Carrera 43A # 1-50', '3023334455', 'daniela@email.com', 'Ninguna', TO_DATE('1992-07-29','YYYY-MM-DD'));

INSERT INTO usuario (u_id_usuario, u_nombre_completo, u_id_plan, u_genero, u_estado, u_direccion_residencia, u_telefono, u_correo_electronico, u_condicion_medica, u_fecha_nacimiento) 
VALUES (6, 'Santiago Restrepo', 1, 'masculino', 'activo', 'Calle 70 # 5-10', '3176667788', 'santiago@email.com', 'Dolor lumbar leve', TO_DATE('1985-05-12','YYYY-MM-DD'));

INSERT INTO usuario (u_id_usuario, u_nombre_completo, u_id_plan, u_genero, u_estado, u_direccion_residencia, u_telefono, u_correo_electronico, u_condicion_medica, u_fecha_nacimiento) 
VALUES (7, 'Valentina Ríos', 3, 'femenino', 'activo', 'Carrera 25 # 40-30', '3045556677', 'valentina@email.com', 'Ninguna', TO_DATE('2000-09-08','YYYY-MM-DD'));

INSERT INTO usuario (u_id_usuario, u_nombre_completo, u_id_plan, u_genero, u_estado, u_direccion_residencia, u_telefono, u_correo_electronico, u_condicion_medica, u_fecha_nacimiento) 
VALUES (8, 'Andrés Castro', 2, 'masculino', 'inactivo', 'Avenida 19 # 100-02', '3182223344', 'andres@email.com', 'Ninguna', TO_DATE('1993-12-01','YYYY-MM-DD'));

INSERT INTO usuario (u_id_usuario, u_nombre_completo, u_id_plan, u_genero, u_estado, u_direccion_residencia, u_telefono, u_correo_electronico, u_condicion_medica, u_fecha_nacimiento) 
VALUES (9, 'Mariana López', 1, 'femenino', 'activo', 'Calle 8 # 30-40', '3051112233', 'mariana@email.com', 'Asma controlado', TO_DATE('1997-03-25','YYYY-MM-DD'));

INSERT INTO usuario (u_id_usuario, u_nombre_completo, u_id_plan, u_genero, u_estado, u_direccion_residencia, u_telefono, u_correo_electronico, u_condicion_medica, u_fecha_nacimiento) 
VALUES (10, 'Alejandro Vargas', 2, 'masculino', 'activo', 'Carrera 15 # 60-12', '3169990011', 'alejandro@email.com', 'Ninguna', TO_DATE('1991-10-14','YYYY-MM-DD'));


-- 5. KARDEX RESERVA (10 Reservas con valores CHECK válidos)
INSERT INTO kardex_reserva (r_id_reserva, r_id_usuario, r_id_clase, r_id_instructor, r_id_plan, r_fecha_reserva, r_hora_reserva, r_precio, r_estado_asistencia, r_estado_reserva) 
VALUES (5001, 1, 201, 101, 1, TO_DATE('2026-11-10','YYYY-MM-DD'), '07:00 AM', 150000.00, 'asistió', 'confirmada');

INSERT INTO kardex_reserva (r_id_reserva, r_id_usuario, r_id_clase, r_id_instructor, r_id_plan, r_fecha_reserva, r_hora_reserva, r_precio, r_estado_asistencia, r_estado_reserva) 
VALUES (5002, 2, 202, 102, 2, TO_DATE('2026-11-11','YYYY-MM-DD'), '05:00 PM', 250000.00, 'no asistió', 'en espera');

INSERT INTO kardex_reserva (r_id_reserva, r_id_usuario, r_id_clase, r_id_instructor, r_id_plan, r_fecha_reserva, r_hora_reserva, r_precio, r_estado_asistencia, r_estado_reserva) 
VALUES (5003, 3, 203, 101, 1, TO_DATE('2026-11-12','YYYY-MM-DD'), '08:00 PM', 150000.00, 'asistió', 'confirmada');

INSERT INTO kardex_reserva (r_id_reserva, r_id_usuario, r_id_clase, r_id_instructor, r_id_plan, r_fecha_reserva, r_hora_reserva, r_precio, r_estado_asistencia, r_estado_reserva) 
VALUES (5004, 4, 204, 103, 3, TO_DATE('2026-11-12','YYYY-MM-DD'), '06:00 PM', 180000.00, 'no asistió', 'confirmada');

INSERT INTO kardex_reserva (r_id_reserva, r_id_usuario, r_id_clase, r_id_instructor, r_id_plan, r_fecha_reserva, r_hora_reserva, r_precio, r_estado_asistencia, r_estado_reserva) 
VALUES (5005, 5, 202, 102, 2, TO_DATE('2026-11-13','YYYY-MM-DD'), '05:00 PM', 250000.00, 'asistió', 'confirmada');

INSERT INTO kardex_reserva (r_id_reserva, r_id_usuario, r_id_clase, r_id_instructor, r_id_plan, r_fecha_reserva, r_hora_reserva, r_precio, r_estado_asistencia, r_estado_reserva) 
VALUES (5006, 6, 201, 101, 1, TO_DATE('2026-11-14','YYYY-MM-DD'), '07:00 AM', 150000.00, 'cancelado', 'cancelada');

INSERT INTO kardex_reserva (r_id_reserva, r_id_usuario, r_id_clase, r_id_instructor, r_id_plan, r_fecha_reserva, r_hora_reserva, r_precio, r_estado_asistencia, r_estado_reserva) 
VALUES (5007, 7, 204, 103, 3, TO_DATE('2026-11-14','YYYY-MM-DD'), '06:00 PM', 180000.00, 'asistió', 'confirmada');

INSERT INTO kardex_reserva (r_id_reserva, r_id_usuario, r_id_clase, r_id_instructor, r_id_plan, r_fecha_reserva, r_hora_reserva, r_precio, r_estado_asistencia, r_estado_reserva) 
VALUES (5008, 9, 205, 104, 1, TO_DATE('2026-11-15','YYYY-MM-DD'), '09:00 AM', 150000.00, 'asistió', 'confirmada');

INSERT INTO kardex_reserva (r_id_reserva, r_id_usuario, r_id_clase, r_id_instructor, r_id_plan, r_fecha_reserva, r_hora_reserva, r_precio, r_estado_asistencia, r_estado_reserva) 
VALUES (5009, 10, 202, 102, 2, TO_DATE('2026-11-15','YYYY-MM-DD'), '05:00 PM', 250000.00, 'no asistió', 'en espera');

INSERT INTO kardex_reserva (r_id_reserva, r_id_usuario, r_id_clase, r_id_instructor, r_id_plan, r_fecha_reserva, r_hora_reserva, r_precio, r_estado_asistencia, r_estado_reserva) 
VALUES (5010, 3, 205, 104, 1, TO_DATE('2026-11-16','YYYY-MM-DD'), '09:00 AM', 150000.00, 'asistió', 'confirmada');


-- Sincronizar secuencias de auto-incremento al valor más alto insertado
ALTER TABLE plan_membresia MODIFY p_id_plan GENERATED BY DEFAULT AS IDENTITY (START WITH LIMIT VALUE);
ALTER TABLE instructor MODIFY i_id_instructor GENERATED BY DEFAULT AS IDENTITY (START WITH LIMIT VALUE);
ALTER TABLE clases MODIFY c_id_clase GENERATED BY DEFAULT AS IDENTITY (START WITH LIMIT VALUE);
ALTER TABLE usuario MODIFY u_id_usuario GENERATED BY DEFAULT AS IDENTITY (START WITH LIMIT VALUE);
ALTER TABLE kardex_reserva MODIFY r_id_reserva GENERATED BY DEFAULT AS IDENTITY (START WITH LIMIT VALUE);

COMMIT;