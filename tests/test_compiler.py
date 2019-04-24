import mysql.connector
from . import test_settings
from pathlib import Path

def test_query(printer, test_class):
    printer('Started')
    cnx = mysql.connector.connect(user=test_settings.MYSQL_USER, password=test_settings.MYSQL_PASSWORD,
                                  host=test_settings.MYSQL_HOST,
                                  database=test_settings.MYSQL_DATABASE)
    test = test_class(printer, cnx, working_dir_base=Path('.'), clean_workdir=test_settings.CLEAN_WORKDIR)

    try:
        assert test.setup()
        assert test.run()
    finally:
        test.cleanup()

    cnx.close()
