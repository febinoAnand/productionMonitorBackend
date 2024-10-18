from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [

        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS production_data (
                id SERIAL NOT NULL,
                date DATE NOT NULL,
                time TIME NOT NULL,
                shift_number INT NOT NULL,
                shift_name VARCHAR(45),
                target_production INT NOT NULL,
                machine_id VARCHAR(45) NOT NULL,
                machine_name VARCHAR(45) NOT NULL,
                production_count INT NOT NULL,
                production_date DATE NOT NULL,
                log_data_id INT NOT NULL,
                timestamp VARCHAR(50),
                PRIMARY KEY (id, production_date)  -- Include production_date in the primary key
            ) PARTITION BY RANGE (production_date);
            """
        ),

        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS production_data_default PARTITION OF production_data DEFAULT;
            """
        ),

        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION create_production_data_partition()
            RETURNS TRIGGER AS $$
            DECLARE
                partition_name TEXT;
                start_date DATE;
                end_date DATE;
            BEGIN
                start_date := NEW.production_date;
                end_date := start_date + INTERVAL '1 day';
                partition_name := 'production_data_' || TO_CHAR(start_date, 'YYYY_MM_DD');

                EXECUTE format(
                    'CREATE TABLE IF NOT EXISTS %I PARTITION OF production_data
                    FOR VALUES FROM (%L) TO (%L)',
                    partition_name, start_date, end_date
                );

                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """
        ),

        migrations.RunSQL(
            """
            CREATE TRIGGER create_partition_before_insert
            BEFORE INSERT ON production_data
            FOR EACH ROW
            EXECUTE FUNCTION create_production_data_partition();
            """
        ),
    ]
