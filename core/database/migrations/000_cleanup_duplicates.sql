-- =================================================================
-- CLEANUP: Eliminar Índices Duplicados
-- Ejecutar SOLO si ya tienes las tablas creadas con índices duplicados
-- =================================================================
-- Si ya ejecutaste la migración anterior, corre esto primero para limpiar:
DROP INDEX IF EXISTS idx_contacts_whatsapp;

-- Verificar que el constraint UNIQUE sigue activo (este NO se elimina):
-- SELECT constraint_name, constraint_type 
-- FROM information_schema.table_constraints 
-- WHERE table_name = 'contacts' AND constraint_type = 'UNIQUE';
-- Resultado esperado: Deberías ver 'contacts_whatsapp_number_key' o similar