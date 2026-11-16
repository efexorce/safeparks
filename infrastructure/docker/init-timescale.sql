CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

SELECT create_hypertable('energy_readings', 'recorded_at', if_not_exists => TRUE) WHERE EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'energy_readings');
SELECT create_hypertable('camera_events', 'occurred_at', if_not_exists => TRUE) WHERE EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'camera_events');
SELECT create_hypertable('bandwidth_usage', 'recorded_at', if_not_exists => TRUE) WHERE EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'bandwidth_usage');
SELECT create_hypertable('alarm_logs', 'triggered_at', if_not_exists => TRUE) WHERE EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alarm_logs');

SELECT add_retention_policy('camera_events', INTERVAL '15 days', if_not_exists => TRUE) WHERE EXISTS (SELECT FROM timescaledb_information.hypertables WHERE hypertable_name = 'camera_events');
SELECT add_retention_policy('energy_readings', INTERVAL '90 days', if_not_exists => TRUE) WHERE EXISTS (SELECT FROM timescaledb_information.hypertables WHERE hypertable_name = 'energy_readings');
SELECT add_retention_policy('bandwidth_usage', INTERVAL '30 days', if_not_exists => TRUE) WHERE EXISTS (SELECT FROM timescaledb_information.hypertables WHERE hypertable_name = 'bandwidth_usage');
