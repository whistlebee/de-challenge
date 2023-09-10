CREATE TABLE IF NOT EXISTS joulescale_measurements (
  timestamp         TIMESTAMP WITH TIME ZONE NOT NULL,
  current           FLOAT,
  voltage           FLOAT,
  _loaded_at        TIMESTAMPTZ DEFAULT NOW()
);

SELECT create_hypertable('joulescale_measurements', 'timestamp', if_not_exists=>TRUE);

