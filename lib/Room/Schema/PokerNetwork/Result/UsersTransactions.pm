package Room::Schema::PokerNetwork::Result::UsersTransactions;

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
__PACKAGE__->table("users_transactions");
__PACKAGE__->add_columns(
  "from_serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "to_serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "modified",
  {
    data_type => "TIMESTAMP",
    default_value => "CURRENT_TIMESTAMP",
    is_nullable => 0,
    size => 14,
  },
  "amount",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "currency_serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 11 },
  "status",
  { data_type => "CHAR", default_value => "n", is_nullable => 1, size => 1 },
  "notes",
  {
    data_type => "TEXT",
    default_value => undef,
    is_nullable => 1,
    size => 65535,
  },
  "id",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 11 },
);
__PACKAGE__->set_primary_key("id");


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2010-08-27 00:26:16
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:30xtWYs1Tynyt2X7au8EEw


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
