-- Create chapters table
CREATE TABLE IF NOT EXISTS chapters (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    chapter_number INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    volume VARCHAR(100),
    content TEXT,
    outline TEXT,
    summary TEXT,
    display_summary TEXT,
    pov_character_id INTEGER,
    featured_characters TEXT,
    locations TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    word_count INTEGER DEFAULT 0,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_chapters_project_id ON chapters(project_id);
CREATE INDEX IF NOT EXISTS idx_chapters_status ON chapters(status);
CREATE INDEX IF NOT EXISTS idx_chapters_chapter_number ON chapters(chapter_number);
CREATE INDEX IF NOT EXISTS idx_chapters_created_at ON chapters(created_at);
CREATE INDEX IF NOT EXISTS idx_chapters_project_chapter ON chapters(project_id, chapter_number);