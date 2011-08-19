package Room::Schema::PokerNetwork::Result::User2tourney;

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
__PACKAGE__->table("user2tourney");
__PACKAGE__->add_columns(
  "user_serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 11 },
  "currency_serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "tourney_serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 11 },
  "table_serial",
  { data_type => "INT", default_value => undef, is_nullable => 1, size => 11 },
  "rank",
  { data_type => "INT", default_value => -1, is_nullable => 1, size => 11 },
);
__PACKAGE__->set_primary_key("user_serial", "tourney_serial");


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2010-09-27 11:47:31
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:yoOcj0wl6dbSxMO3lcWsow

__PACKAGE__->belongs_to(
  user => 'Room::Schema::PokerNetwork::Result::Users',
  { serial => 'user_serial' }
);

__PACKAGE__->belongs_to(
  tourney => 'Room::Schema::PokerNetwork::Result::Tourneys',
  { serial => 'tourney_serial' }
);

__PACKAGE__->belongs_to(
  tourney_table => 'Room::Schema::PokerNetwork::Result::Pokertables',
  { serial => 'table_serial' }
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
