from rets.models import Record
from rets.models import Results
import xmltodict
from rets.parsers.base import Base


class OneXSearchCursor(Base):

    xml = None
    base = None

    def get_total_count(self):
        if 'COUNT' in self.base:
            return int(self.base['COUNT'].get('@Records'))
        return None

    def get_found_max_rows(self):
        return 'MAXROWS' in self.base

    def get_delimiter(self):
        if 'DELIMITER' in self.base:
            # delimiter found so we have at least a COLUMNS row to parse
            return chr(int(self.base['DELIMITER'].get('@value', 9)))
        else:
            # assume tab delimited since it wasn't given
            print('Assuming TAB delimiter since none specified in response')
            return chr(9)

    def get_column_names(self):
        # break out and track the column names in the response
        column_names = self.base.get('COLUMNS')

        # take out the first and last delimiter
        column_names = column_names.strip(self.get_delimiter())

        # parse and return the rest
        return column_names.split(self.get_delimiter())

    def parse(self, rets_response, parameters):
        self.xml = xmltodict.parse(rets_response.text)
        self.base = self.xml.get('RETS')

        rs = Results()
        rs.resource = parameters.get('SearchType')
        rs.resource_class = parameters.get('Class')
        rs.dmql = parameters.get('Query')
        rs.metadata = parameters.get('ResourceModel')

        if parameters.get('RestrictedIndicator', None):
            rs.restricted_indicator = parameters.get('RestrictedIndicator', None)

        rs.headers = self.get_column_names()

        if 'DATA' in self.base:
            for line in self.base['DATA']:
                delim = self.get_delimiter()
                result_dict = self.data_columns_to_dict(columns_string=self.base.get('COLUMNS', ''),
                                                        dict_string=line,
                                                        delimiter=delim)
                r = Record()
                r.values = result_dict

                rs.add_record(r)

        if self.get_total_count() is not None:
            rs.total_results_count = self.get_total_count()
            print("%s results found" % rs.total_results_count)

        print('%s results' % rs.results_count)

        if self.get_found_max_rows():
            '''
            MAXROWS tag found.  the RETS server withheld records.
            if the server supports Offset, more requests can be sent to page through results
            until this tag isn't found anymore.
            '''
            rs.max_rows_reached = True
            print("Maximum rows returned in response")

        return rs
