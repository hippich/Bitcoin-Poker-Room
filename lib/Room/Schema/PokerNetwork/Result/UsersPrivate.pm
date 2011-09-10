package Room::Schema::PokerNetwork::Result::UsersPrivate;

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

Room::Schema::PokerNetwork::Result::UsersPrivate

=cut

__PACKAGE__->table("users_private");

=head1 ACCESSORS

=head2 serial

  data_type: 'integer'
  extra: {unsigned => 1}
  is_nullable: 0

=head2 firstname

  data_type: 'varchar'
  default_value: (empty string)
  is_nullable: 1
  size: 255

=head2 lastname

  data_type: 'varchar'
  default_value: (empty string)
  is_nullable: 1
  size: 255

=head2 addr_street

  data_type: 'varchar'
  default_value: (empty string)
  is_nullable: 1
  size: 255

=head2 addr_street2

  data_type: 'varchar'
  default_value: (empty string)
  is_nullable: 1
  size: 255

=head2 addr_zip

  data_type: 'varchar'
  default_value: (empty string)
  is_nullable: 1
  size: 64

=head2 addr_town

  data_type: 'varchar'
  default_value: (empty string)
  is_nullable: 1
  size: 64

=head2 addr_state

  data_type: 'varchar'
  default_value: (empty string)
  is_nullable: 1
  size: 128

=head2 addr_country

  data_type: 'varchar'
  default_value: (empty string)
  is_nullable: 1
  size: 64

=head2 phone

  data_type: 'varchar'
  default_value: (empty string)
  is_nullable: 1
  size: 64

=head2 gender

  data_type: 'char'
  default_value: (empty string)
  is_nullable: 1
  size: 1

=head2 birthdate

  data_type: 'date'
  datetime_undef_if_invalid: 1
  is_nullable: 1

=head2 verified

  data_type: 'char'
  default_value: 'n'
  is_nullable: 1
  size: 1

=head2 verified_time

  data_type: 'integer'
  default_value: 0
  is_nullable: 1

=cut

__PACKAGE__->add_columns(
  "serial",
  { data_type => "integer", extra => { unsigned => 1 }, is_nullable => 0 },
  "firstname",
  { data_type => "varchar", default_value => "", is_nullable => 1, size => 255 },
  "lastname",
  { data_type => "varchar", default_value => "", is_nullable => 1, size => 255 },
  "addr_street",
  { data_type => "varchar", default_value => "", is_nullable => 1, size => 255 },
  "addr_street2",
  { data_type => "varchar", default_value => "", is_nullable => 1, size => 255 },
  "addr_zip",
  { data_type => "varchar", default_value => "", is_nullable => 1, size => 64 },
  "addr_town",
  { data_type => "varchar", default_value => "", is_nullable => 1, size => 64 },
  "addr_state",
  { data_type => "varchar", default_value => "", is_nullable => 1, size => 128 },
  "addr_country",
  { data_type => "varchar", default_value => "", is_nullable => 1, size => 64 },
  "phone",
  { data_type => "varchar", default_value => "", is_nullable => 1, size => 64 },
  "gender",
  { data_type => "char", default_value => "", is_nullable => 1, size => 1 },
  "birthdate",
  { data_type => "date", datetime_undef_if_invalid => 1, is_nullable => 1 },
  "verified",
  { data_type => "char", default_value => "n", is_nullable => 1, size => 1 },
  "verified_time",
  { data_type => "integer", default_value => 0, is_nullable => 1 },
);
__PACKAGE__->set_primary_key("serial");


# Created by DBIx::Class::Schema::Loader v0.07010 @ 2011-09-10 02:25:23
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:65XNsUDfo9fzZCWAYroVCw


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
