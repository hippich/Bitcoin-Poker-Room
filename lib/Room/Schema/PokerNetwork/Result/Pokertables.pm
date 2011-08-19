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


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2010-09-27 11:47:31
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:0zRzp3wUR4KVXGCdR92Wjg


__PACKAGE__->has_many(
    'usertables' => 'Room::Schema::PokerNetwork::Result::User2table',
    { 'foreign.table_serial' => 'self.serial' },
);

__PACKAGE__->many_to_many(
    users => 'usertables', 'user'
);


__PACKAGE__->has_one( 
    tourney => 'Room::Schema::PokerNetwork::Result::Tourneys',
    { 'foreign.serial' => 'self.tourney_serial' },
);


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
