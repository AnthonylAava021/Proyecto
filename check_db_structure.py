#!/usr/bin/env python3
"""
Script para verificar la estructura de la tabla corners_tabla en PostgreSQL
"""

import psycopg2
import psycopg2.extras
import sys

# Configuración de la base de datos PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'user',
    'password': 'ups_bet05',
    'database': 'UPS_BET',
    'port': 5432
}

def check_table_structure():
    """Verificar la estructura de la tabla corners_tabla"""
    print("🔍 Verificando estructura de la tabla corners_tabla...")
    
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            # Verificar si la tabla existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'corners_tabla'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                print("❌ La tabla 'corners_tabla' no existe")
                return False
            
            print("✅ La tabla 'corners_tabla' existe")
            
            # Obtener estructura de la tabla
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'corners_tabla'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print("\n📋 Estructura de la tabla:")
            print("-" * 50)
            for col in columns:
                print(f"  {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            
            # Verificar columnas específicas
            column_names = [col[0] for col in columns]
            required_columns = ['equipo_local_id', 'equipo_visitante_id', 'fecha']
            
            missing_columns = [col for col in required_columns if col not in column_names]
            if missing_columns:
                print(f"\n❌ Faltan columnas requeridas: {missing_columns}")
                return False
            
            print(f"\n✅ Todas las columnas requeridas están presentes")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM corners_tabla;")
            count = cursor.fetchone()[0]
            print(f"📊 Total de registros: {count}")
            
            # Mostrar algunos ejemplos
            if count > 0:
                cursor.execute("""
                    SELECT equipo_local_id, equipo_visitante_id, fecha 
                    FROM corners_tabla 
                    ORDER BY fecha DESC 
                    LIMIT 5;
                """)
                examples = cursor.fetchall()
                print(f"\n📝 Últimos 5 registros:")
                print("-" * 50)
                for i, example in enumerate(examples, 1):
                    print(f"  {i}. Local: {example[0]}, Visitante: {example[1]}, Fecha: {example[2]}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()

def test_connection():
    """Probar conexión a la base de datos"""
    print("🔍 Probando conexión a PostgreSQL...")
    
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        print("✅ Conexión exitosa a PostgreSQL")
        connection.close()
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Verificando configuración de PostgreSQL...")
    print("=" * 60)
    
    # Probar conexión
    if not test_connection():
        print("\n❌ No se puede conectar a PostgreSQL")
        print("   Verifica que:")
        print("   1. PostgreSQL esté corriendo")
        print("   2. Las credenciales en DB_CONFIG sean correctas")
        print("   3. La base de datos UPS_BET exista")
        sys.exit(1)
    
    # Verificar estructura
    if not check_table_structure():
        print("\n❌ Problemas con la estructura de la tabla")
        print("   Verifica que:")
        print("   1. La tabla corners_tabla exista")
        print("   2. Tenga las columnas: equipo_local_id, equipo_visitante_id, fecha")
        print("   3. Tenga datos para hacer predicciones")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Configuración de PostgreSQL correcta!")
    print("\n💡 Ahora puedes ejecutar el backend:")
    print("   python app.py")

if __name__ == "__main__":
    main()
