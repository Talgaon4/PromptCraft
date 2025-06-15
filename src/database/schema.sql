-- src/database/schema.sql
-- Run this file to create the database schema

-- Prompts table
CREATE TABLE IF NOT EXISTS prompts (
    id VARCHAR(36) PRIMARY KEY,
    text TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    description TEXT,
    parent_id VARCHAR(36) REFERENCES prompts(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prompt instances table
CREATE TABLE IF NOT EXISTS prompt_instances (
    id VARCHAR(36) PRIMARY KEY,
    prompt_id VARCHAR(36) NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
    formatted_text TEXT NOT NULL,
    context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Responses table
CREATE TABLE IF NOT EXISTS responses (
    id VARCHAR(36) PRIMARY KEY,
    prompt_instance_id VARCHAR(36) NOT NULL REFERENCES prompt_instances(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    response_metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Feedback table
CREATE TABLE IF NOT EXISTS feedback (
    id VARCHAR(36) PRIMARY KEY,
    response_id VARCHAR(36) NOT NULL REFERENCES responses(id) ON DELETE CASCADE,
    score DECIMAL(3,2) NOT NULL CHECK (score >= 0.0 AND score <= 1.0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Optimization jobs table (for later)
CREATE TABLE IF NOT EXISTS optimization_jobs (
    id VARCHAR(36) PRIMARY KEY,
    prompt_id VARCHAR(36) NOT NULL REFERENCES prompts(id),
    status VARCHAR(20) DEFAULT 'queued',
    strategy VARCHAR(50) DEFAULT 'simple_ai',
    progress INTEGER DEFAULT 0,
    result TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Essential indexes
CREATE INDEX IF NOT EXISTS idx_prompt_instances_prompt_id ON prompt_instances(prompt_id);
CREATE INDEX IF NOT EXISTS idx_responses_prompt_instance_id ON responses(prompt_instance_id);
CREATE INDEX IF NOT EXISTS idx_feedback_response_id ON feedback(response_id);
CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON feedback(created_at);
CREATE INDEX IF NOT EXISTS idx_optimization_jobs_prompt_id ON optimization_jobs(prompt_id);