#!/usr/bin/env python3
"""
Script para probar la conexión a la base de datos PostgreSQL
"""

import psycopg2
import psycopg2.extras

# Configuración de la base de datos PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'user',
    'password': 'ups_bet05',
    'database': 'UPS_BET',
    'port': 5432
}

def test_connection():
    """Probar conexión básica"""
    print("Probando conexión básica...")
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        print("✓ Conexión exitosa")
        
        # Probar una consulta simple
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✓ PostgreSQL version: {version[0]}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ Error de conexión: {e}")
        print(f"Tipo de error: {type(e)}")
        return False

def test_table_exists():
    """Verificar si la tabla corners_tabla existe"""
    print("\nVerificando tabla corners_tabla...")
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'corners_tabla'
                );
            """)
            exists = cursor.fetchone()[0]
            
            if exists:
                print("✓ Tabla corners_tabla existe")
                
                # Verificar estructura
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'corners_tabla'
                    ORDER BY ordinal_position;
                """)
                columns = cursor.fetchall()
                print(f"✓ Columnas encontradas: {len(columns)}")
                for col in columns:
                    print(f"  - {col[0]}: {col[1]}")
                
                # Verificar datos
                cursor.execute("SELECT COUNT(*) FROM corners_tabla;")
                count = cursor.fetchone()[0]
                print(f"✓ Registros en la tabla: {count}")
                
            else:
                print("✗ Tabla corners_tabla no existe")
        
        connection.close()
        return exists
        
    except Exception as e:
        print(f"✗ Error verificando tabla: {e}")
        return False

def test_sample_query():
    """Probar una consulta de ejemplo"""
    print("\nProbando consulta de ejemplo...")
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        
        with connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            # Buscar un registro de ejemplo
            cursor.execute("""
                SELECT * FROM corners_tabla 
                WHERE equipo_local_id = 4 AND equipo_visitante_id = 0 
                ORDER BY fecha DESC 
                LIMIT 1
            """)
            result = cursor.fetchone()
            
            if result:
                print("✓ Consulta exitosa")
                print(f"✓ Registro encontrado con fecha: {result['fecha']}")
                print(f"✓ Datos: {dict(result)}")
            else:
                print("✓ Consulta exitosa pero no se encontraron datos")
                print("  (Esto es normal si no hay datos para esos equipos)")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ Error en consulta: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 50)
    print("PRUEBA DE CONEXIÓN A BASE DE DATOS")
    print("=" * 50)
    
    # Probar conexión básica
    if not test_connection():
        print("\n❌ No se puede conectar a la base de datos")
        print("Verifica que PostgreSQL esté ejecutándose y las credenciales sean correctas")
        return
    
    # Verificar tabla
    if not test_table_exists():
        print("\n❌ La tabla corners_tabla no existe")
        print("Verifica que la base de datos tenga la estructura correcta")
        return
    
    # Probar consulta
    test_sample_query()
    
    print("\n" + "=" * 50)
    print("PRUEBA COMPLETADA")
    print("=" * 50)

if __name__ == "__main__":
    main()
