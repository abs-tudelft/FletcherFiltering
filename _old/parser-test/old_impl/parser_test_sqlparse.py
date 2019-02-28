import sqlparse

if __name__ == "__main__":
    query = "select a, CONCAT('a','b','c') as concat from jobs WHERE a > 5 AND (-b) < 3"
    #queries = sqlparse.split(query)
    print(sqlparse.format(query, reindent=True, keyword_case='upper'))

    parsed = sqlparse.parse(query)

    first_statement = parsed[0]

    print(first_statement.tokens)