-- 01_create_tables.sql - Schéma DEPE855
CREATE TABLE IF NOT EXISTS news (
    id                  SERIAL PRIMARY KEY,
    news_uid            VARCHAR(255) UNIQUE,
    title               TEXT NOT NULL,
    summary             TEXT,
    source              VARCHAR(100),
    publication_date    TIMESTAMP,
    event_date          TIMESTAMP,
    verification_status VARCHAR(20) DEFAULT 'pending',
    confidence_score    FLOAT,
    first_seen          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_date     TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_news_uid      ON news(news_uid);
CREATE INDEX        IF NOT EXISTS idx_news_source   ON news(source);
CREATE INDEX        IF NOT EXISTS idx_news_status   ON news(verification_status);
CREATE INDEX        IF NOT EXISTS idx_news_pub_date ON news(publication_date DESC);
