-- Initialize PostgreSQL schemas for AgentGate
-- One shared database instance with strict schema separation between Engine and Gateway

CREATE SCHEMA IF NOT EXISTS engine;
CREATE SCHEMA IF NOT EXISTS gateway;

-- Set search path or grant permissions if needed
GRANT ALL ON SCHEMA engine TO agentgate;
GRANT ALL ON SCHEMA gateway TO agentgate;
