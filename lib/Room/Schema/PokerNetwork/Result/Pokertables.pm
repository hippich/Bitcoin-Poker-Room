package Room::Schema::PokerNetwork::Result::Pokertables;

use strict;
use warnings;

use base 'DBIx::Class';

__PACKAGE__->load_components(
  "InflateColumn::DateTime",
  "FrozenColumns",
  "FilterColumn",
  "EncodedColumn",
  "Core",
);
__PACKAGE__->table("pokertables");
__PACKAGE__->add_columns(
  "serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "resthost_serial",
  { data_type => "INT", default_value => 0, is_nullable => 0, size => 10 },
  "seats",
  { data_type => "TINYINT", default_value => 10, is_nullable => 1, size => 4 },
  "average_pot",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 10 },
  "hands_per_hour",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 10 },
  "percent_flop",
  { data_type => "TINYINT", default_value => 0, is_nullable => 1, size => 4 },
  "players",
  { data_type => "TINYINT", default_value => 0, is_nullable => 1, size => 4 },
  "observers",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 10 },
  "waiting",
  { data_type => "TINYINT", default_value => 0, is_nullable => 1, size => 4 },
  "player_timeout",
  { data_type => "INT", default_value => 60, is_nullable => 1, size => 10 },
  "muck_timeout",
  { data_type => "INT", default_value => 5, is_nullable => 1, size => 10 },
  "currency_serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 11 },
  "name",
  {
    data_type => "VARCHAR",
    default_value => undef,
    is_nullable => 0,
    size => 255,
  },
  "variant",
  {
    data_type => "VARCHAR",
    default_value => undef,
    is_nullable => 0,
    size => 255,
  },
  "betting_structure",
  {
    data_type => "VARCHAR",
    default_value => undef,
    is_nullable => 0,
    size => 255,
  },
  "skin",
  {
    data_type => "VARCHAR",
    default_value => "default",
    is_nullable => 0,
    size => 255,
  },
  "tourney_serial",
  { data_type => "INT", default_value => 0, is_nullable => 0, size => 10 },
);
__PACKAGE__->set_primary_key("serial");
__PACKAGE__->add_unique_constraint("name", ["name"]);


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2010-08-27 00:26:16
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:+bA/P9NZKkRRK9sTb/gsqg


# You can replace this text with custom content, and it will be preserved on regeneration
1;
