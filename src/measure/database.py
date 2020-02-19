import argparse
import logging
import datetime
import psycopg2
from psycopg2.extras import Json
from configparser import ConfigParser

log = logging.getLogger('postgres')

class DNSDatabase:
    def __init__(self, database, user, password, host, har_table, dns_table):
        self.har_table = har_table
        self.dns_table = dns_table
        self._host = host
        self._database = database
        self._user = user
        self._password = password
        self._connect()

    def _connect(self):
        try:
            self.conn = psycopg2.connect(host=self._host,
                                         database=self._database,
                                         user=self._user,
                                         password=self._password)
            psycopg2.extras.register_uuid()
        except Exception as e:
            log.error('Error connecting to database: {}'.format(e))

        try:
            self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        except Exception as e:
            log.error('Error getting cursor from database: {}'.format(e))

    @staticmethod
    def init_from_config_file(cf, section='postgresql'):
        parser = ConfigParser()
        parser.read(cf)

        params = {}
        if parser.has_section(section):
            for param in parser.items(section):
                params[param[0]] = param[1]

        return DNSDatabase(database=params['database'], user=params['user'],
                           password=params['password'], host=params['host'],
                           har_table=params['har_table'], dns_table=params['dns_table'])

    def _execute_command(self, cmd, format_tuple=None):
        if self.conn.closed:
            self._connect()

        try:
            if format_tuple:
                self.cursor.execute(cmd, format_tuple)
            else:
                self.cursor.execute(cmd)
            self.conn.commit()
        except Exception as e:
            print(e)
            self.conn.commit()
            return e
        return None

    def create_har_table(self):
        cmd = '''
                 CREATE TABLE {} (
                 uuid UUID PRIMARY KEY,
                 experiment UUID,
                 insertion_time TIMESTAMP WITH TIME ZONE,
                 domain TEXT,
                 recursive TEXT,
                 dns_type TEXT,
                 har JSONB,
                 error TEXT DEFAULT NULL,
                 delays JSONB
                 )
              '''.format(self.har_table)

        rv = self._execute_command(cmd)
        if rv:
            print('Error creating har table: error: {}'.format(rv))
        return rv

    def create_dns_table(self):
        cmd = '''
                 CREATE TABLE {} (
                 har_uuid UUID,
                 experiment UUID,
                 insertion_time TIMESTAMP WITH TIME ZONE,
                 domain TEXT,
                 recursive TEXT,
                 dns_type TEXT,
                 response_size INTEGER DEFAULT NULL,
                 response_time DOUBLE PRECISION,
                 error INTEGER DEFAULT NULL
                 )
              '''.format(self.dns_table)

        rv = self._execute_command(cmd)
        if rv:
            print('Error creating sizes table: error: {}'.format(rv))
        return rv

    def delete_table(self, table):
        ans = input('Delete table: {} from database? (Y/n): '.format(table))
        if ans == 'Y':
            cmd = 'DROP TABLE {}'.format(table)
        else:
            return

        rv = self._execute_command(cmd)
        if rv:
            pass
        return rv

    def insert_har(self, experiment, domain, recursive, dns_type, har, har_uuid, har_error, delays):
        insert = ''' INSERT INTO {}
                     (uuid, experiment, insertion_time, domain, recursive, dns_type, har, error, delays)
                     VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
                 '''.format(self.har_table)

        now = datetime.datetime.utcnow()
        har_uuid = psycopg2.extensions.adapt(har_uuid)
        if har:
            tup = (har_uuid, experiment, now, domain, recursive,
                   dns_type, Json(har), None, Json(delays))
        else:
            tup = (har_uuid, experiment, now, domain, recursive,
                   dns_type, None, har_error, Json(delays))

        rv = self._execute_command(insert, tup)
        if rv:
            print('Error inserting har into database, error: {}'.format(rv))
        return rv

    def insert_dns(self, har_uuid, experiment, recursive,
                   dns_type, all_dns_info):
        insert = '''INSERT INTO {}
                    (har_uuid, experiment,
                     insertion_time, domain,
                     recursive, dns_type,
                     response_size, response_time,
                     error)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                 '''.format(self.dns_table)

        for domain in all_dns_info:
            dns_info = all_dns_info[domain]
            now = datetime.datetime.utcnow()
            response_size = dns_info['response_size']
            response_time = dns_info['response_time']
            error = dns_info['error']
            tup = (har_uuid, experiment, now,
                   domain, recursive, dns_type,
                   response_size, response_time,
                   error)

            rv = self._execute_command(insert, tup)
            if rv:
                err = 'Error inserting into database, error: {}'
                print(err.format(rv))
                return rv
        return rv

    def get_hars(self, recursive, dns_type, domains):
        domains = tuple(domains)
        cmd = '''
                 SELECT *
                 FROM {}
                 WHERE recursive = %s AND
                       dns_type  = %s AND
                       domain IN %s
              '''.format(self.har_table)

        rv = self._execute_command(cmd, (recursive, dns_type, domains))
        if rv:
            err = 'Error getting HARs from database, error: {}'
            print(err.format(rv))
            return rv
        rv = self.cursor.fetchall()
        return rv

    def get_unique_uuids(self, recursive, dns_type):
        cmd = '''
            SELECT distinct uuid
            FROM {}
            WHERE recursive = %s AND
                  dns_type = %s
          '''.format(self.har_table)
        rv = self._execute_command(cmd, (recursive, dns_type))
        if rv:
            err = 'Error getting UUIDs from database, error: {}'
            print(err.format(rv))
            return rv
        rv = self.cursor.fetchall()
        return rv

    def get_resources(self, domains, experiments=None):
        domains = tuple(domains)
        if experiments:
            experiments = tuple(experiments)
            cmd = '''
                SELECT uuid, domain, experiment,
                       dns_type, recursive,
                       (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, 'entries')), 'request')->>'url') as url
                FROM {}
                WHERE domain IN %s AND experiment IN %s
                '''.format(self.har_table)
            rv = self._execute_command(cmd, (domains, experiments))
        else:
            cmd = '''
                SELECT uuid, domain, experiment,
                       dns_type, recursive,
                       (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, 'entries')), 'request')->>'url') as url,
                       (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, 'entries')), 'serverIPAddress')) as serverIPAddress
                FROM {}
                WHERE domain IN %s
                '''.format(self.har_table)
            rv = self._execute_command(cmd, (domains, ))

        if rv:
            err = 'Error getting pageloads from resource URLs from database, error: {}'
            print(err.format(rv))
            return rv

        rv = self.cursor.fetchall()
        return rv

    def get_resource_counts(self, domains, experiments=None):
        domains = tuple(domains)
        if experiments:
            experiments = tuple(experiments)
            cmd = '''
                SELECT uuid, domain, recursive, dns_type,
                        jsonb_array_length(jsonb_extract_path(har, 'entries')) as resources,
                        (jsonb_extract_path(har, 'pages', '0', 'pageTimings')->>'onLoad')::float as pageload
                FROM {}
                WHERE domain IN %s AND experiment IN %s
                '''.format(self.har_table)
            rv = self._execute_command(cmd, (domains, experiments))
        else:
            cmd = '''
                SELECT uuid, domain, recursive, dns_type,
                        jsonb_array_length(jsonb_extract_path(har, 'entries')) as resources,
                        (jsonb_extract_path(har, 'pages', '0', 'pageTimings')->>'onLoad')::float as pageload
                FROM {}
                WHERE domain IN %s
                '''.format(self.har_table)
            rv = self._execute_command(cmd, (domains, ))

        if rv:
            err = 'Error getting resource counts from database, error: {}'
            print(err.format(rv))
            return rv

        rv = self.cursor.fetchall()
        return rv

    def get_pageloads(self, domains, experiments=None):
        domains = tuple(domains)
        if experiments:
            experiments = tuple(experiments)
            cmd = '''
                SELECT uuid, domain, experiment,
                        dns_type, recursive,
                        jsonb_extract_path(har, 'pages', '0', 'pageTimings')->>'onLoad' as pageload
                FROM {}
                WHERE domain IN %s AND experiment IN %s
                '''.format(self.har_table)
            rv = self._execute_command(cmd, (domains, experiments))
        else:
            cmd = '''
                SELECT uuid, domain, experiment,
                       dns_type, recursive,
                       jsonb_extract_path(har, 'pages', '0', 'pageTimings')->>'onLoad' as pageload
                FROM {}
                WHERE domain IN %s
                '''.format(self.har_table)
            rv = self._execute_command(cmd, (domains, ))

        if rv:
            err = 'Error getting pageloads from database, error: {}'
            print(err.format(rv))
            return rv

        rv = self.cursor.fetchall()
        return rv

    def get_dns_timings_domains(self, domains, experiments=None):
        domains = tuple(domains)
        if experiments:
            experiments = tuple(experiments)
            cmd = '''
                SELECT har_uuid, domain, experiment, dns_type, recursive,
                       response_time, response_size, error
                FROM {}
                WHERE domain IN %s AND experiment IN %s
                '''.format(self.dns_table)
            rv = self._execute_command(cmd, (domains, experiments))
        else:
            cmd = '''
                SELECT har_uuid, domain, experiment, dns_type, recursive,
                       response_time, response_size, error
                FROM {}
                WHERE domain IN %s
                '''.format(self.dns_table)
            rv = self._execute_command(cmd, (domains, ))

        if rv:
            err = 'Error getting DNS timings from database, error: {}'
            print(err.format(rv))
            return rv

        rv = self.cursor.fetchall()
        return rv

    def get_dns_timings(self, experiments=None):
        if experiments:
            experiments = tuple(experiments)
            cmd = '''
                SELECT har_uuid, domain, experiment, dns_type, recursive,
                       response_time, response_size, error
                FROM {}
                WHERE experiment IN %s
                '''.format(self.dns_table)
            rv = self._execute_command(cmd, (experiments, ))
        else:
            cmd = '''
                SELECT har_uuid, domain, experiment, dns_type, recursive,
                       response_time, response_size, error
                FROM {}
                '''.format(self.dns_table)
            rv = self._execute_command(cmd)

        if rv:
            err = 'Error getting DNS timings from database, error: {}'
            print(err.format(rv))
            return rv

        rv = self.cursor.fetchall()
        return rv

    def get_content_sizes(self, experiments=None):
        if experiments:
            experiments = tuple(experiments)
            cmd = '''
                SELECT uuid, domain, recursive, dns_type,
                       (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, 'entries')), 'request')->'headersSize') as requestHeadersSize,
                       (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, 'entries')), 'request')->'bodySize') as requestBodySize,
                       (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, 'entries')), 'response')->'headersSize') as responseHeadersSize,
                       (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, 'entries')), 'response')->'bodySize') as responseBodySize
                FROM {}
                '''.format(self.har_table)
            rv = self._execute_command(cmd, (experiments, ))
        else:
            cmd = '''
                SELECT uuid, domain, recursive, dns_type,
                       (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, 'entries')), 'request')->'headersSize') as requestHeadersSize,
                       (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, 'entries')), 'request')->'bodySize') as requestBodySize,
                       (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, 'entries')), 'response')->'headersSize') as responseHeadersSize,
                       (jsonb_extract_path(jsonb_array_elements(jsonb_extract_path(har, 'entries')), 'response')->'bodySize') as responseBodySize
                FROM {}
                '''.format(self.har_table)
            rv = self._execute_command(cmd)

        if rv:
            err = 'Error getting request header sizes from database, error: {}'
            print(err.format(rv))
            return rv

        rv = self.cursor.fetchall()
        return rv

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('database_config_file')
    parser.add_argument('-ct', '--clear_table', action='store_true')
    args = parser.parse_args()

    d = DNSDatabase.init_from_config_file(args.database_config_file)
    if args.clear_table:
        d.delete_table(d.har_table)
        d.delete_table(d.dns_table)
    d.create_har_table()
    d.create_dns_table()

if __name__ == "__main__":
    main()
