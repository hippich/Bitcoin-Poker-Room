#!/usr/bin/env python
# coding: utf-8


class Error(RuntimeError):
    pass


class APIService(object):
    """A wrapper around pokernetwork.pokerservice.PokerService for
    pokernetwork.apiserver.APIServer to use."""

    def __init__(self, poker_service):
        self.poker_service = poker_service

    def get_active_tables(self):
        """Returns a list of pokernetwork.pokertable.PokerTable objects
        corresponding to tables that currently have players seated."""
        active_tables = []
        for _, table in self.poker_service.tables.iteritems():
            if len(table.listPlayers()) > 0:
                active_tables.append(table)
        return active_tables

    def add_table(self, table_settings):
        pass

    def remove_table(self, table_name):
        pass

    def reload_server_config(self):
        """
        Reloads and returns the current pokernetwork.pokernetworkconfig.Config.
        """
        config = self.poker_service.settings
        config.reload()
        return config

    def refresh_table_config(self):
        """
        Reloads the server config then performs the following algorithm:

            For each table that has no seated players:
                - If the table is not listed in the config, delete the table.
                - Otherwise, update the table settings to the settings in the
                  config.
        """
        config = self.reload_server_config()

        config_tables = {table['name']: table for table in
                         config.headerGetProperties('/server/table')}

        active_table_names = set()
        tables_to_delete = []
        for table_id, table in self.poker_service.tables.iteritems():
            table_name = table.game.name
            if len(table.listPlayers()) > 0:
                active_table_names.add(table_name)
            elif table_name not in config_tables:
                tables_to_delete.append(table_id)

        for table_id in tables_to_delete:
            self.poker_service.deleteTable(self.poker_service.tables[table_id])

        for table_name, table_settings in config_tables.iteritems():
            if table_name not in active_table_names:
                self.poker_service.createTable(0, table_settings)
