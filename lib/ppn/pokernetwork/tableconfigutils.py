#!/usr/bin/env python
# coding: utf-8

import glob
import os

from pokernetwork import pokernetworkconfig


DEFAULT_TABLE_CONFIGS_DIR = '/etc/poker-network/tables.d'
DEFAULT_TABLE_NODE_XPATH = '/*/table'


def __get_tables(config, table_node_xpath=DEFAULT_TABLE_NODE_XPATH):
    return config.headerGetProperties(table_node_xpath)


def parse_table_config(table_config_path,
                       table_node_xpath=DEFAULT_TABLE_NODE_XPATH):
    """
    Parses table properties from the XML config specified by
    `table_config_path`. Tables are represented as XML nodes and specified by
    the XPath expression, `table_node_xpath`. Table properties are XML
    attributes. nodes specified by the XPath expression, `table_node_xpath`.

    Here is an example of a table config consisting of 2 table nodes, with
    table_node_xpath of '/tables/table':

        <?xml version="1.0" encoding="UTF-8"?>
        <tables>
            <table name="Table1" variant="holdem" betting_structure=".05-.10-no-limit" seats="6" />
            <table name="Table2" variant="omaha8" betting_structure="10-20-limit" seats="10" />
        </tables>

    Returns a list of dicts with keys corresponding to table properties (name,
    variant, betting_structure, seats, etc.).
    """
    config = pokernetworkconfig.Config([''])
    config.load(table_config_path)
    return config.headerGetProperties(table_node_xpath)


def parse_table_configs(table_configs_dir=DEFAULT_TABLE_CONFIGS_DIR,
                        table_node_xpath=DEFAULT_TABLE_NODE_XPATH):
    """
    Parses table configs found in `table_configs_dir`.

    Returns a list of dicts with keys corresponding to table properties (name,
    variant, betting_structure, seats, etc.).

    `table_configs_dir`: directory containing table configuration files
    `table_node_xpath`: the XPath expression used to find table nodes in each
                        config file
    """
    tables = []
    table_config_paths = glob.glob(os.path.join(table_configs_dir, '*.xml'))
    for table_config_path in table_config_paths:
        tables.extend(parse_table_config(table_config_path))
    return tables


def merge_tables(server_config_tables, table_config_tables):
    """
    Merges server_config_tables with table_config_tables.

    When a table with the same name is found in both the server config and
    a table config, we use the table settings from the table config. In
    other words, table entries in table configs take precedence over table
    entries in the server config.

    Returns a list of dictionaries with keys corresponding to table
    properties (name, variant, seats, etc.).

    `server_config_tables`: a list of dictionaries with keys corresponding
                            to table properties (name, variant, seats,
                            etc.)
    `table_config_tables`: a list of dictionaries with keys corresponding
                           to table properties (name, variant, seats,
                           etc.)
    """
    tables = []
    table_names = set()

    def try_add_table(table):
        table_name = table['name']
        if table_name not in table_names:
            table_names.add(table_name)
            tables.append(table)

    for table in table_config_tables:
        try_add_table(table)
    for table in server_config_tables:
        try_add_table(table)
    return tables


def get_table_descriptions(server_config,
                           table_configs_dir=DEFAULT_TABLE_CONFIGS_DIR,
                           table_node_xpath=DEFAULT_TABLE_NODE_XPATH):
    """
    Combines table descriptions in `server_config` with table config files
    located in `table_configs_dir`. Table descriptions in table config files
    take precedence over table descriptions in the server config.

    Returns a list of dicts with keys corresponding to table properties (name,
    variant, betting_structure, seats, etc.).

    `server_config`: a pokernetwork.pokernetworkconfig.Config object
    `table_configs_dir`: directory containing XML table configuration files
    `table_node_xpath`: the XPath expression used to find table nodes in each
                        config file
    """
    server_config.reload()

    server_config_tables = __get_tables(server_config)
    table_config_tables = parse_table_configs(table_configs_dir)
    return merge_tables(server_config_tables, table_config_tables)
