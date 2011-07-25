#!/usr/bin/env python
# coding: utf-8

import pokerpackets


class Error(RuntimeError):
    pass


class APIService(object):
    """A wrapper around pokernetwork.pokerservice.PokerService for
    pokernetwork.apiserver.APIServer to use."""

    def __init__(self, poker_service):
        self.poker_service = poker_service

    def broadcast_to_all(self, message):
        """
        Broadcasts a PacketPokerMessage packet to all clients.
        """
        packet = pokerpackets.PacketPokerMessage(string=message)
        self.poker_service.broadcast_to_all(packet)

    def broadcast_to_player(self, message, player_serial):
        """
        Broadcasts a PacketPokerMessage packet to a specific player.
        """
        packet = pokerpackets.PacketPokerMessage(string=message)
        return self.poker_service.broadcast_to_player(packet, player_serial)

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

    def refresh_table_config(self):
        """
        Create/modify/delete tables at runtime, by loading table descriptions
        (XML <table /> nodes) from the server config and table configs.

        Gets table descriptions from the server config and table configs, then
        performs the following algorithm:

            For each active table that has NO seated players:
                - If the table has no associated table description, then delete
                  it.
                - Otherwise, modify the table's attributes to match its
                  associated table description.

            For each table description, d:
                - If a table with name d['name'] is not running on the server,
                  then create it.
        """
        config_tables = {}
        for table in self.poker_service.get_table_descriptions():
            config_tables[table['name']] = table

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

        for table_name, table_description in config_tables.iteritems():
            if table_name not in active_table_names:
                self.poker_service.createTable(0, table_description)
