package Room::Schema::PokerNetwork::Result::Tourneys;

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
__PACKAGE__->table("tourneys");
__PACKAGE__->add_columns(
  "serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "resthost_serial",
  { data_type => "INT", default_value => 0, is_nullable => 0, size => 10 },
  "name",
  {
    data_type => "VARCHAR",
    default_value => undef,
    is_nullable => 1,
    size => 200,
  },
  "description_short",
  {
    data_type => "VARCHAR",
    default_value => undef,
    is_nullable => 1,
    size => 64,
  },
  "description_long",
  {
    data_type => "TEXT",
    default_value => undef,
    is_nullable => 1,
    size => 65535,
  },
  "players_quota",
  { data_type => "INT", default_value => 10, is_nullable => 1, size => 11 },
  "players_min",
  { data_type => "INT", default_value => 2, is_nullable => 1, size => 11 },
  "variant",
  {
    data_type => "VARCHAR",
    default_value => undef,
    is_nullable => 1,
    size => 32,
  },
  "betting_structure",
  {
    data_type => "VARCHAR",
    default_value => undef,
    is_nullable => 1,
    size => 32,
  },
  "seats_per_game",
  { data_type => "INT", default_value => 10, is_nullable => 1, size => 11 },
  "player_timeout",
  { data_type => "INT", default_value => 60, is_nullable => 1, size => 11 },
  "currency_serial",
  { data_type => "INT", default_value => undef, is_nullable => 1, size => 11 },
  "prize_currency",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 10 },
  "prize_min",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "bailor_serial",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "buy_in",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "rake",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "sit_n_go",
  { data_type => "CHAR", default_value => "y", is_nullable => 1, size => 1 },
  "breaks_first",
  { data_type => "INT", default_value => 7200, is_nullable => 1, size => 11 },
  "breaks_interval",
  { data_type => "INT", default_value => 3600, is_nullable => 1, size => 11 },
  "breaks_duration",
  { data_type => "INT", default_value => 300, is_nullable => 1, size => 11 },
  "rebuy_delay",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "add_on",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "add_on_delay",
  { data_type => "INT", default_value => 60, is_nullable => 1, size => 11 },
  "start_time",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "satellite_of",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 10 },
  "via_satellite",
  { data_type => "TINYINT", default_value => 0, is_nullable => 1, size => 4 },
  "satellite_player_count",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 10 },
  "finish_time",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "state",
  {
    data_type => "VARCHAR",
    default_value => "registering",
    is_nullable => 1,
    size => 16,
  },
  "schedule_serial",
  { data_type => "INT", default_value => undef, is_nullable => 1, size => 11 },
  "add_on_count",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "rebuy_count",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
);
__PACKAGE__->set_primary_key("serial");


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2010-08-27 00:26:16
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:81idk819dL/2JN2y06Ma6w


# You can replace this text with custom content, and it will be preserved on regeneration
1;
