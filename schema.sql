-- Create cities table
CREATE TABLE cities (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  country TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create clues table
CREATE TABLE clues (
  id SERIAL PRIMARY KEY,
  city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
  text TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create fun_facts table
CREATE TABLE fun_facts (
  id SERIAL PRIMARY KEY,
  city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
  text TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create trivia table
CREATE TABLE trivia (
  id SERIAL PRIMARY KEY,
  city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
  text TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE questions (
    question_id TEXT PRIMARY KEY,
    correct_city_id INT NOT NULL,
    correct_obfuscated_id TEXT NOT NULL,
    clues TEXT[] NOT NULL,  -- Array of text clues
    choices JSONB NOT NULL, -- JSON array for city choices
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Create indexes for better query performance
CREATE INDEX idx_clues_city_id ON clues(city_id);
CREATE INDEX idx_fun_facts_city_id ON fun_facts(city_id);
CREATE INDEX idx_trivia_city_id ON trivia(city_id);
