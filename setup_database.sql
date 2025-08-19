-- ========================================
-- UPSBet - Configuración de Base de Datos
-- ========================================
-- Ejecutar este archivo como superusuario de PostgreSQL

-- 1. Crear la base de datos
CREATE DATABASE "UPS_BET";

-- 2. Crear el usuario
CREATE USER "user" WITH PASSWORD 'ups_bet05';

-- 3. Dar permisos al usuario
GRANT ALL PRIVILEGES ON DATABASE "UPS_BET" TO "user";

-- 4. Conectar a la base de datos UPS_BET
\c "UPS_BET";

-- 5. Dar permisos adicionales al usuario
GRANT ALL ON SCHEMA public TO "user";
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "user";
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "user";

-- 6. Configurar permisos para futuras tablas
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "user";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO "user";

-- ========================================
-- INSTRUCCIONES DE USO:
-- ========================================
-- 1. Abrir pgAdmin o psql como superusuario
-- 2. Ejecutar este archivo: \i setup_database.sql
-- 3. O ejecutar línea por línea en psql
--
-- Alternativa desde línea de comandos:
-- psql -U postgres -f setup_database.sql
-- ========================================
