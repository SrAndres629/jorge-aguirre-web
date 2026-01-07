-- =================================================================
-- INIT_CRM_MASTER.SQL
-- Schema para Jorge Aguirre Ecosistema 360º
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
    whatsapp_number TEXT UNIQUE NOT NULL,
    full_name TEXT,
    profile_pic_url TEXT,
    
    -- Marketing Intelligence (Meta Bridge)
    fb_click_id TEXT, -- fbc
    fb_browser_id TEXT, -- fbp
    utm_source TEXT,
    utm_campaign TEXT,
    utm_medium TEXT,
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

-- Indices para Performance de Contactos
CREATE INDEX IF NOT EXISTS idx_contacts_whatsapp ON contacts(whatsapp_number);
CREATE INDEX IF NOT EXISTS idx_contacts_status ON contacts(status);
CREATE INDEX IF NOT EXISTS idx_contacts_fb_click_id ON contacts(fb_click_id);

-- 3. Tabla de Historial de Mensajes (Chat Memory)
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), -- Fixed: using uuid for consistency
    contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
    role TEXT CHECK (role IN ('user', 'assistant', 'system', 'tool')),
    content TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indice para Mensajes
CREATE INDEX IF NOT EXISTS idx_messages_contact_id ON messages(contact_id);

COMMENT ON TABLE contacts IS 'Core CRM table for storage of lead and client info';
COMMENT ON TABLE messages IS 'Message history for AI context window';
