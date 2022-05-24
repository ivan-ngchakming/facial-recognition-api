from alembic.config import Config
from flask_migrate import downgrade, stamp, upgrade


def test_all_migrations_pass(app_empty_db):
    """
    Test to check that when the database is at alembic's base revision,
    an upgrade to 'head' followed by a downgrade to 'base' both proceed successfully
    Required input db state:
    alembic_version.version_num = empty OR table does not exist
    tables = empty OR alembic_version only
    Output db state:
    Same as input.
    db.create_all(), db.drop_all() do not affect alembic_version
    because alembic creates and maintains this table, not Flask-SQLAlchemy, so
    if you need to edit this version_num, either use the stamp() function or
    connect to TEST_DATABASE_URL with psql and do it directly.
    """
    with app_empty_db.app_context():
        config = Config()

        config.set_main_option("script_location", "migrations")

        try:
            upgrade(config.get_main_option("migrations"))
            downgrade(config.get_main_option("migrations"), revision="base")
        finally:
            # when there is an exception thrown and the test fails, set
            # the alembic_version table to empty in order to be able to re-run the test
            # without having to manually delete the alembic_version entry the db got stuck at
            stamp(config.get_main_option("migrations"), revision="base")
