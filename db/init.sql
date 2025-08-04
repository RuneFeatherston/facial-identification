-- Database initialization script
-- This script is executed when the PostgreSQL container starts for the first time

-- Create the UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    join_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create face_embeddings table to store vector embeddings
CREATE TABLE IF NOT EXISTS face_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    embedding_vector FLOAT8[] NOT NULL, -- Store the face embedding as array of floats
    quality VARCHAR(10) NOT NULL CHECK (quality IN ('high', 'medium', 'low')),
    confidence_score FLOAT4 DEFAULT 0.0, -- Confidence score from ML service
    is_active BOOLEAN NOT NULL DEFAULT true,
    metadata JSONB DEFAULT '{}', -- Store additional metadata (image dimensions, etc.)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create auth_sessions table
CREATE TABLE IF NOT EXISTS auth_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token TEXT NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT true
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_face_embeddings_user_id ON face_embeddings(user_id);
CREATE INDEX IF NOT EXISTS idx_face_embeddings_active ON face_embeddings(is_active);
CREATE INDEX IF NOT EXISTS idx_face_embeddings_quality ON face_embeddings(quality);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_user_id ON auth_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_token ON auth_sessions(token);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_active ON auth_sessions(is_active);

-- Insert sample data for testing
INSERT INTO users (username, full_name, email) VALUES 
    ('test', 'Test User', 'test@example.com'),
    ('demo', 'Demo User', 'demo@example.com'),
    ('admin', 'Admin User', 'admin@example.com')
ON CONFLICT (username) DO NOTHING;
