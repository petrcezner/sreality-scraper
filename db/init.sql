CREATE TABLE sreality
(
    id            BIGINT PRIMARY KEY,
    title          text,
    location      text,
    price         text,
    living_area   text,
    reality_type  text,
    building_type text,
    deal_type     text,
    url           text,
    images        text[],
    created_at    timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at    timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);
