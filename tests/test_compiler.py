import mysql.connector


def test_query(printer, test_class):
    printer('Started')
    cnx = mysql.connector.connect(user='fletcherfiltering', password='pfUcFN4S9Qq7X6NDBMHk',
                                  host='127.0.0.1',
                                  database='fletcherfiltering')
    test = test_class(printer, cnx, '.')
    try:
        assert test.setup()
        assert test.run()
    finally:
        test.cleanup()

    cnx.close()
