#!/usr/bin/env python
# coding: utf-8

import os
import tempfile
import unittest

from pokernetwork import tableconfigutils


SERVER_CONFIG_TEMPLATE = """\
<?xml version="1.0" encoding="ISO-8859-1"?>
<server xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="server.xsd" poker_network_version="2.0.0">
%s
</server>"""


TABLE_CONFIG_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<tables>
%s
</tables>"""


TABLE_NODE_TEMPLATE = """\
<table name="%(name)s" variant="%(variant)s" betting_structure="%(betting_structure)s" seats="%(seats)s" />"""


SERVER_CONFIG_TABLES = [
    ('One', 'holdem', '5-10-no-limit'),
    ('Two', 'omaha', '2-4-limit'),
    ('Four', 'omaha8', '.01-.02-pot-limit'),
    ('Ten', 'stud', '10-20-limit'),
    ('Eleven', 'stud', '30-60-limit')
]


TABLE_CONFIGS = {
    'holdem.limit.xml': [('One', 'holdem', '2-4-limit'),
                         ('Two', 'holdem', '10-20-limit')],
    'holdem.no-limit.xml': [('Three', 'holdem', '.02-.04-no-limit'),
                            ('Four', 'holdem', '.05-.10-no-limit', '6'),
                            ('Five', 'holdem', '100-200-no-limit')],
    'omaha.limit.xml': [('Six', 'omaha', '2-4-limit'),
                        ('Seven', 'omaha', '10-20-limit', '8')],
    'omaha8.limit.xml': [('Eight', 'omaha8', '20-40-limit'),
                         ('Nine', 'omaha8', '5-10-limit')]
}


# result of merging SERVER_CONFIG_TABLES with tables in TABLE_CONFIGS
MERGED_TABLES = [
    ('One', 'holdem', '2-4-limit'),
    ('Two', 'holdem', '10-20-limit'),
    ('Three', 'holdem', '.02-.04-no-limit'),
    ('Four', 'holdem', '.05-.10-no-limit', '6'),
    ('Five', 'holdem', '100-200-no-limit'),
    ('Six', 'omaha', '2-4-limit'),
    ('Seven', 'omaha', '10-20-limit', '8'),
    ('Eight', 'omaha8', '20-40-limit'),
    ('Nine', 'omaha8', '5-10-limit'),
    ('Ten', 'stud', '10-20-limit'),
    ('Eleven', 'stud', '30-60-limit')
]


def create_table_dict(name, variant, betting_structure, seats='10'):
    return {'name': name, 'variant': variant,
            'betting_structure': betting_structure, 'seats': seats}


def create_table_xml_entry(table_properties):
    return TABLE_NODE_TEMPLATE % table_properties


def create_config(config_template, tables):
    table_xml_entries = []
    for table in tables:
        table_properties = create_table_dict(*table)
        table_xml_entries.append(create_table_xml_entry(table_properties))
    return config_template % '\n'.join(table_xml_entries)


class DummyServerConfig():
    def __init__(self, table_descriptions,
                 table_node_xpath=tableconfigutils.DEFAULT_TABLE_NODE_XPATH):
        self.path = None
        self.table_descriptions = table_descriptions
        self.table_node_xpath = table_node_xpath

    def reload(self):
         pass

    def headerGetProperties(self, name):
        if name is self.table_node_xpath:
            return self.table_descriptions
        return []


class TableConfigUtilsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_basedir = tempfile.mkdtemp()
        cls.server_config_path = os.path.join(cls.config_basedir,
                                              'poker.server.xml')
        with open(cls.server_config_path, 'w+t') as server_config:
            contents = create_config(SERVER_CONFIG_TEMPLATE,
                                     SERVER_CONFIG_TABLES)
            server_config.write(contents)

        cls.table_configs_dir = os.path.join(cls.config_basedir, 'tables.d')
        os.mkdir(cls.table_configs_dir)

        cls.table_config_paths = []
        for config_filename, tables in TABLE_CONFIGS.iteritems():
            config_path = os.path.join(cls.table_configs_dir, config_filename)
            cls.table_config_paths.append(config_path)
            with open(config_path, 'w+t') as table_config:
                contents = create_config(TABLE_CONFIG_TEMPLATE, tables)
                table_config.write(contents)

    @classmethod
    def tearDownClass(cls):
        for config_path in cls.table_config_paths:
            os.remove(config_path)
        os.removedirs(cls.table_configs_dir)

    def test_parse_table_config(self):
        tables = tableconfigutils.parse_table_config(self.server_config_path)
        assert len(tables) == len(SERVER_CONFIG_TABLES)

    def test_parse_table_configs(self):
        tables = tableconfigutils.parse_table_configs(self.table_configs_dir)
        assert len(tables) == sum(len(tables) for tables in
                                  TABLE_CONFIGS.values())

    def _compare_tables(self, tables_a, tables_b):
        """
        Returns True if both lists of tables contain the same table entries
        (order is not important).

        `tables_a`: a list of dicts containing table properties as keys
        `tables_b`: a list of dicts containing table properties as keys
        """
        if len(tables_a) != len(tables_b):
            return False

        seen = {}
        for table in tables_a:
            seen[table['name']] = table

        for table in tables_b:
            table_name = table['name']
            if table_name not in seen or table != seen[table_name]:
                return False
        return True

    def test_merge_tables_with_no_tables(self):
        assert tableconfigutils.merge_tables([], []) == []

    def test_merge_tables_with_no_server_config_tables(self):
        table_config_tables = [
            create_table_dict('One', 'holdem', '2-4-limit'),
            create_table_dict('Two', 'holdem', '5-10-no-limit'),
            create_table_dict('Three', 'omaha8', '3-6-limit')
        ]
        merged_tables = tableconfigutils.merge_tables([], table_config_tables)
        assert self._compare_tables(merged_tables, table_config_tables)

    def test_merge_tables_with_no_table_config_tables(self):
        server_config_tables = [
            create_table_dict('One', 'holdem', '2-4-limit'),
            create_table_dict('Two', 'holdem', '5-10-no-limit'),
            create_table_dict('Five', 'omaha', '.10-.20-pot-limit'),
            create_table_dict('Six', 'omaha8', '3-6-limit')
        ]
        merged_tables = tableconfigutils.merge_tables(server_config_tables, [])
        assert self._compare_tables(merged_tables, server_config_tables)

    def test_get_all_table_descriptions(self):
        server_config_tables = [create_table_dict(*table) for table in
                                SERVER_CONFIG_TABLES]
        server_config = DummyServerConfig(server_config_tables)
        table_descriptions = tableconfigutils.get_table_descriptions(
                                server_config, self.table_configs_dir)

        expected_tables = [create_table_dict(*table) for table in MERGED_TABLES]

        assert self._compare_tables(table_descriptions, expected_tables)
