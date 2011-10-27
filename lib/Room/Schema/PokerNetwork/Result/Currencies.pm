package Room::Schema::PokerNetwork::Result::Currencies;

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

Room::Schema::PokerNetwork::Result::Currencies

=cut

__PACKAGE__->table("currencies");

=head1 ACCESSORS

=head2 serial

  data_type: 'integer'
  is_auto_increment: 1
  is_nullable: 0

=head2 url

  data_type: 'char'
  is_nullable: 0
  size: 255

=head2 symbol

  data_type: 'char'
  is_nullable: 1
  size: 8

=head2 name

  data_type: 'char'
  is_nullable: 1
  size: 32

=head2 cash_out

  data_type: 'integer'
  is_nullable: 1

=cut

__PACKAGE__->add_columns(
  "serial",
  { data_type => "integer", is_auto_increment => 1, is_nullable => 0 },
  "url",
  { data_type => "char", is_nullable => 0, size => 255 },
  "symbol",
  { data_type => "char", is_nullable => 1, size => 8 },
  "name",
  { data_type => "char", is_nullable => 1, size => 32 },
  "cash_out",
  { data_type => "integer", is_nullable => 1 },
);
__PACKAGE__->set_primary_key("serial", "url");
__PACKAGE__->add_unique_constraint("serial", ["serial"]);
__PACKAGE__->add_unique_constraint("url", ["url"]);


# Created by DBIx::Class::Schema::Loader v0.07010 @ 2011-09-10 02:20:28
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:tF51aRUWxeNBdLYh+LX7Iw


__PACKAGE__->add_columns(
    "id",
    { 
        data_type => "char", 
        is_nullable => 0, 
        size => 255 
    },
    "rate",
    {
        data_type => "decimal",
        default_value => "0.0000",
        is_nullable => 0,
        size => [64, 4],
    },
    "minconf",
    {
        data_type => "integer",
        is_nullable => 0,
        default_value => 6,
    },
    "class",
    {
        data_type => "char",
        is_nullable => 0,
        size => 255,
    }
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
