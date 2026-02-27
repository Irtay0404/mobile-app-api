CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    name_kz     VARCHAR(255),
    category    VARCHAR(100),
    description TEXT,
    price       NUMERIC(10,2) NOT NULL,
    image_url   TEXT,
    barcode     VARCHAR(50),
    in_stock    BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Индекс для быстрого fuzzy-поиска по имени
CREATE INDEX idx_products_name_trgm ON products USING GIN (name gin_trgm_ops);
CREATE INDEX idx_products_name_lower ON products (LOWER(name));