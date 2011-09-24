package Room::Schema::PokerNetwork::Result::User2hand;

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

Room::Schema::PokerNetwork::Result::User2hand

=cut

__PACKAGE__->table("user2hand");

=head1 ACCESSORS

=head2 user_serial

  data_type: 'integer'
  is_nullable: 0

=head2 hand_serial

  data_type: 'integer'
  is_nullable: 0

=head2 ip6

  data_type: 'bigint'
  extra: {unsigned => 1}
  is_nullable: 1

=head2 ip

  data_type: 'bigint'
  extra: {unsigned => 1}
  is_nullable: 1

=head2 share

  data_type: 'bigint'
  is_nullable: 0

=head2 pot

  data_type: 'bigint'
  is_nullable: 0

=head2 rake

  data_type: 'bigint'
  is_nullable: 0

=head2 points

  data_type: 'decimal'
  is_nullable: 0
  size: [64,4]

=cut

__PACKAGE__->add_columns(
  "user_serial",
  { data_type => "integer", is_nullable => 0 },
  "hand_serial",
  { data_type => "integer", is_nullable => 0 },
  "ip6",
  { data_type => "bigint", extra => { unsigned => 1 }, is_nullable => 1 },
  "ip",
  { data_type => "bigint", extra => { unsigned => 1 }, is_nullable => 1 },
  "share",
  { data_type => "bigint", is_nullable => 0 },
  "pot",
  { data_type => "bigint", is_nullable => 0 },
  "rake",
  { data_type => "bigint", is_nullable => 0 },
  "points",
  { data_type => "decimal", is_nullable => 0, size => [64, 4] },
);
__PACKAGE__->set_primary_key("user_serial", "hand_serial");


# Created by DBIx::Class::Schema::Loader v0.07010 @ 2011-09-23 23:34:41
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:PV/zN6KldFvbw9rvS1MVeQ


__PACKAGE__->belongs_to(
  user => 'Room::Schema::PokerNetwork::Result::Users',
  { serial => 'user_serial' }
);

__PACKAGE__->belongs_to(
  hand => 'Room::Schema::PokerNetwork::Result::Hands',
  { serial => 'hand_serial' }
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
