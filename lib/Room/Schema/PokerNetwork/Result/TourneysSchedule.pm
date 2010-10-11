package Room::Schema::PokerNetwork::Result::TourneysSchedule;

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
__PACKAGE__->table("tourneys_schedule");
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
  "register_time",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "active",
  { data_type => "CHAR", default_value => "y", is_nullable => 1, size => 1 },
  "respawn",
  { data_type => "CHAR", default_value => "n", is_nullable => 1, size => 1 },
  "respawn_interval",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "currency_serial_from_date_format",
  {
    data_type => "VARCHAR",
    default_value => undef,
    is_nullable => 1,
    size => 16,
  },
  "prize_currency_from_date_format",
  {
    data_type => "VARCHAR",
    default_value => undef,
    is_nullable => 1,
    size => 16,
  },
  "satellite_of",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 10 },
  "via_satellite",
  { data_type => "TINYINT", default_value => 0, is_nullable => 1, size => 4 },
  "satellite_player_count",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 10 },
);
__PACKAGE__->set_primary_key("serial");


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2010-09-27 11:47:31
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:O2277E53gsHcqAQ/KwS6Cw


# You can replace this text with custom content, and it will be preserved on regeneration

=head1 AUTHOR

Pavel Karoukin

=head1 LICENSE

Copyright (C) 2010 Pavel A. Karoukin <pavel@yepcorp.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

=cut

1;
