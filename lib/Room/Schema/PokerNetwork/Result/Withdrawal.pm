package Room::Schema::PokerNetwork::Result::Withdrawal;

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

Room::Schema::PokerNetwork::Result::Withdrawal

=cut

__PACKAGE__->table("withdrawal");

=head1 ACCESSORS

=head2 withdrawal_id

  data_type: 'integer'
  is_auto_increment: 1
  is_nullable: 0

=head2 user_serial

  data_type: 'integer'
  is_nullable: 0

=head2 currency_serial

  data_type: 'integer'
  is_nullable: 0

=head2 amount

  data_type: 'float'
  is_nullable: 0

=head2 processed

  data_type: 'integer'
  is_nullable: 0

=head2 info

  data_type: 'text'
  is_nullable: 0

=head2 created_at

  data_type: 'datetime'
  datetime_undef_if_invalid: 1
  is_nullable: 0

=head2 processed_at

  data_type: 'datetime'
  datetime_undef_if_invalid: 1
  is_nullable: 0

=head2 dest

  data_type: 'text'
  is_nullable: 1

=cut

__PACKAGE__->add_columns(
  "withdrawal_id",
  { data_type => "integer", is_auto_increment => 1, is_nullable => 0 },
  "user_serial",
  { data_type => "integer", is_nullable => 0 },
  "currency_serial",
  { data_type => "integer", is_nullable => 0 },
  "amount",
  { data_type => "float", is_nullable => 0 },
  "processed",
  { data_type => "integer", is_nullable => 0 },
  "info",
  { data_type => "text", is_nullable => 0 },
  "created_at",
  {
    data_type => "datetime",
    datetime_undef_if_invalid => 1,
    is_nullable => 0,
  },
  "processed_at",
  {
    data_type => "datetime",
    datetime_undef_if_invalid => 1,
    is_nullable => 0,
  },
  "dest",
  { data_type => "text", is_nullable => 1 },
);
__PACKAGE__->set_primary_key("withdrawal_id");


# Created by DBIx::Class::Schema::Loader v0.07010 @ 2011-09-10 02:25:23
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:SHPD20AdhWWrXU6EKEfx8g

__PACKAGE__->add_columns(
  "processed_at",
  {
    data_type => "DATETIME",
    default_value => undef,
    is_nullable => 0,
    size => 19,
    datetime_undef_if_invalid => 1,
  },
);

__PACKAGE__->has_one(
  'currency' => 'Room::Schema::PokerNetwork::Result::Currencies',
  { 'foreign.serial' => 'self.currency_serial' },
);

__PACKAGE__->has_one(
  'user' => 'Room::Schema::PokerNetwork::Result::Users',
  { 'foreign.serial' => 'self.user_serial' },
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
