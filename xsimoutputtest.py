from tests.helpers.xsim_output_reader import XSIMOutputReader
from tests.queries.test_nullable import Nullable
from tests.queries.test_combination1 import Combination1
from tests.queries.test_concat import Concat
from fletcherfiltering import settings
import pyarrow as pa
from pathlib import Path
from terminaltables import AsciiTable as Table
import colorama

colorama.init(autoreset=True)

COLOR_DEBUG = False

RED = colorama.Fore.RED+('<red>' if COLOR_DEBUG else '')
GREEN = colorama.Fore.GREEN+('<green>' if COLOR_DEBUG else '')
CYAN = colorama.Fore.CYAN+('<blue>' if COLOR_DEBUG else '')
BLUE = colorama.Fore.BLUE+('<cyan>' if COLOR_DEBUG else '')
RESET = colorama.Fore.RESET+('<reset>' if COLOR_DEBUG else '')

def insert_color(string, index, color):
    return string[:index] + color + string[index:]

def get_colors(data):
    if not data['dvalid'] and data['last']:
        return CYAN
    if data['last']:
        return BLUE
    if not data['dvalid']:
        return GREEN
    if not data['valid']:
        return RED
    return RESET


def handle_column(cols, query):
    line = []
    for key in cols:
        value = cols[key]
        length_column = False
        if key.endswith(settings.LENGTH_SUFFIX):
            col_name = key[:-len(settings.LENGTH_SUFFIX)]
            length_column = True
        else:
            col_name = key
        if col_name == 'ap_return':
            schema = pa.schema([('ap_return', pa.bool_(), False)])
            col = schema[0]
        else:
            col = query.out_schema.field_by_name(col_name)
        assert col is not None

        if isinstance(value,list) and col.type == pa.string() and not length_column:
            datas = []
            string = b""
            for item in value:
                if not item['valid']:
                    item['data'] = '.'
                datas.append(item)
                string += item['data']
            string = string.decode('utf-8')
            i = 0
            offset = 0
            current_color = RESET
            for data in datas:
                color = get_colors(data)
                if current_color != color:
                    string = insert_color(string, i + offset, color)
                    current_color = color
                    offset += len(color)
                i += 1
            line.append(string + RESET)
        elif value['dvalid'] is not None:
            colors = get_colors(value)
            if not value['valid']:
                value['data'] = None
            line.append("{}{}{}".format(colors, value['data'], RESET))
        else:
            print("Found empty record: {}".format(value))
            line.append("<nothing>")
    return line

def run_test(q):
    print("Running for {}...".format(q.__class__.__name__))
    xor = XSIMOutputReader(q.in_schema, q.out_schema)

    data = xor.read(Path('fletcherfiltering_test_workspace/{0}/{0}/automated_tests/sim/tv'.format(q.__class__.__name__)),
                    q.__class__.__name__, full_output=True)
    # print("Transactions: ", num)
    table_data = [data[0].keys()]
    for v in data:
        table_data.append(handle_column(v, q))

    table = Table(table_data, title=q.__class__.__name__)

    print(table.table)

if __name__ == '__main__':
    run_test(Combination1(None, None))
    run_test(Concat(None, None))
    run_test(Nullable(None, None))

