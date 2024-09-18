CREATE TABLE worksites (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE risk_notes (
    id SERIAL PRIMARY KEY,
    worksite_id INT REFERENCES worksites(id),
    note TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    worksite_id INT REFERENCES worksites(id) ON DELETE CASCADE
);

-- Create indexes to speed up queries
CREATE INDEX idx_workers_worksite ON workers (worksite_id);
