package Room::Schema::PokerNetwork::Result::User2table;

# Created by DBIx::Class::Schema::Loader
# DO NOT MODIFY THE FIRST PART OF THIS FILE

use strict;
use warnings;

use base 'DBIx::Class::Core';

__PACKAGE__->load_components(
  "InflateColumn::DateTime",
  "FrozenColumns",
  "FilterColumn",
  "EncodedColumn",
);

=head1 NAME

Room::Schema::PokerNetwork::Result::User2table

=cut

__PACKAGE__->table("user2table");

=head1 ACCESSORS

=head2 user_serial

  data_type: 'integer'
  extra: {unsigned => 1}
  is_nullable: 0

=head2 table_serial

  data_type: 'integer'
  extra: {unsigned => 1}
  is_nullable: 0

=head2 money

  data_type: 'integer'
  default_value: 0
  is_nullable: 0

=head2 bet

  data_type: 'integer'
  default_value: 0
  is_nullable: 0

=cut

__PACKAGE__->add_columns(
  "user_serial",
  { data_type => "integer", extra => { unsigned => 1 }, is_nullable => 0 },
  "table_serial",
  { data_type => "integer", extra => { unsigned => 1 }, is_nullable => 0 },
  "money",
  { data_type => "integer", default_value => 0, is_nullable => 0 },
  "bet",
  { data_type => "integer", default_value => 0, is_nullable => 0 },
);
__PACKAGE__->set_primary_key("user_serial", "table_serial");


# Created by DBIx::Class::Schema::Loader v0.07010 @ 2011-09-10 02:25:23
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:ksJEssJDcuSabQaiPePi+g


__PACKAGE__->belongs_to(
  user => 'Room::Schema::PokerNetwork::Result::Users',
  { serial => 'user_serial' }
);

__PACKAGE__->belongs_to(
  pokertable => 'Room::Schema::PokerNetwork::Result::Pokertables',
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
