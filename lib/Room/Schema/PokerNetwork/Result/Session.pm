package Room::Schema::PokerNetwork::Result::Session;

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

Room::Schema::PokerNetwork::Result::Session

=cut

__PACKAGE__->table("session");

=head1 ACCESSORS

=head2 user_serial

  data_type: 'integer'
  is_nullable: 0

=head2 started

  data_type: 'integer'
  default_value: 0
  is_nullable: 1

=head2 ended

  data_type: 'integer'
  default_value: 0
  is_nullable: 1

=head2 ip

  data_type: 'varchar'
  default_value: (empty string)
  is_nullable: 0
  size: 16

=cut

__PACKAGE__->add_columns(
  "user_serial",
  { data_type => "integer", is_nullable => 0 },
  "started",
  { data_type => "integer", default_value => 0, is_nullable => 1 },
  "ended",
  { data_type => "integer", default_value => 0, is_nullable => 1 },
  "ip",
  { data_type => "varchar", default_value => "", is_nullable => 0, size => 16 },
);
__PACKAGE__->set_primary_key("user_serial", "ip");


# Created by DBIx::Class::Schema::Loader v0.07010 @ 2011-09-10 02:25:23
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:3mKfYXQDNrHvts9WKYtiaQ


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
