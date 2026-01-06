-- =================================================================
-- INIT_CRM_MASTER.SQL (Clean Version)
-- Schema para Jorge Aguirre Ecosistema 360º
-- Version: 2.0 (Sin índices duplicados)
-- =================================================================

-- 1. Enum para Estados de Lead
DO $$ BEGIN
    CREATE TYPE lead_status AS ENUM (
        'new', 'interested', 'nurturing', 'ghost', 'booked', 
        'client_active', 'client_loyal', 'archived'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 2. Tabla Central de Contactos (CRM)
CREATE TABLE IF NOT EXISTS contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    whatsapp_number TEXT UNIQUE NOT NULL, -- UNIQUE ya crea un índice automáticamente
    full_name TEXT,
    profile_pic_url TEXT,
    
    -- Marketing Intelligence (Meta Bridge)
    fb_click_id TEXT,
    fb_browser_id TEXT,
    utm_source TEXT,
    utm_campaign TEXT,
    utm_medium TEXT,
    utm_term TEXT,
    utm_content TEXT,
    web_visit_count INT DEFAULT 0,
    conversion_sent_to_meta BOOLEAN DEFAULT FALSE,
    
    -- Ventas
    status lead_status DEFAULT 'new',
    lead_score INT DEFAULT 50,
    pain_point TEXT,
    
    -- Operaciones
    service_interest TEXT,
    service_booked_date TIMESTAMPTZ,
    appointment_count INT DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    last_interaction TIMESTAMPTZ
);

-- Indices para Performance (Sin duplicar el de whatsapp_number)
CREATE INDEX IF NOT EXISTS idx_contacts_status ON contacts(status);
CREATE INDEX IF NOT EXISTS idx_contacts_fb_click_id ON contacts(fb_click_id);
CREATE INDEX IF NOT EXISTS idx_contacts_created_at ON contacts(created_at);

-- 3. Tabla de Visitantes Anónimos (Tracking Pre-Conversión)
CREATE TABLE IF NOT EXISTS visitors (
    id SERIAL PRIMARY KEY,
    external_id TEXT,
    fbclid TEXT,
    ip_address TEXT,
    user_agent TEXT,
    source TEXT,
    
    -- UTM Parameters (Campañas de Marketing)
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    utm_term TEXT,
    utm_content TEXT,
    
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Indices para Visitors
CREATE INDEX IF NOT EXISTS idx_visitors_external_id ON visitors(external_id);
CREATE INDEX IF NOT EXISTS idx_visitors_fbclid ON visitors(fbclid);
CREATE INDEX IF NOT EXISTS idx_visitors_timestamp ON visitors(timestamp);

-- 4. Tabla de Historial de Mensajes (Chat Memory)
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
    role TEXT CHECK (role IN ('user', 'assistant', 'system', 'tool')),
    content TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indice para Mensajes
CREATE INDEX IF NOT EXISTS idx_messages_contact_id ON messages(contact_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

-- =================================================================
-- COMENTARIOS DE DOCUMENTACIÓN
-- =================================================================
COMMENT ON TABLE contacts IS 'Core CRM table - Almacena información de leads y clientes confirmados';
COMMENT ON TABLE visitors IS 'Tracking anónimo pre-conversión - Captura datos de Meta CAPI antes de identificar al usuario';
COMMENT ON TABLE messages IS 'Message history for AI context window - Usado por n8n Agent';

COMMENT ON COLUMN contacts.whatsapp_number IS 'Phone number único - Primary identifier para toda comunicación';
COMMENT ON COLUMN contacts.fb_click_id IS 'Facebook Click ID (fbclid) - Para atribución en Meta Ads';
COMMENT ON COLUMN contacts.utm_source IS 'UTM Source - Ej: facebook, instagram, google';
COMMENT ON COLUMN visitors.external_id IS 'ID generado en frontend - Para vincular con eventos de Meta Pixel';
