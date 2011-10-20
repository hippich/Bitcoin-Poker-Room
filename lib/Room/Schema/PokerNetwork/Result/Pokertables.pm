package Room::Schema::PokerNetwork::Result::Pokertables;

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

Room::Schema::PokerNetwork::Result::Pokertables

=cut

__PACKAGE__->table("pokertables");

=head1 ACCESSORS

=head2 serial

  data_type: 'integer'
  extra: {unsigned => 1}
  is_auto_increment: 1
  is_nullable: 0

=head2 resthost_serial

  data_type: 'integer'
  default_value: 0
  extra: {unsigned => 1}
  is_nullable: 0

=head2 seats

  data_type: 'tinyint'
  default_value: 10
  is_nullable: 1

=head2 average_pot

  data_type: 'integer'
  default_value: 0
  extra: {unsigned => 1}
  is_nullable: 1

=head2 hands_per_hour

  data_type: 'integer'
  default_value: 0
  extra: {unsigned => 1}
  is_nullable: 1

=head2 percent_flop

  data_type: 'tinyint'
  default_value: 0
  is_nullable: 1

=head2 players

  data_type: 'tinyint'
  default_value: 0
  is_nullable: 1

=head2 observers

  data_type: 'integer'
  default_value: 0
  extra: {unsigned => 1}
  is_nullable: 1

=head2 waiting

  data_type: 'tinyint'
  default_value: 0
  is_nullable: 1

=head2 player_timeout

  data_type: 'integer'
  default_value: 60
  extra: {unsigned => 1}
  is_nullable: 1

=head2 muck_timeout

  data_type: 'integer'
  default_value: 5
  extra: {unsigned => 1}
  is_nullable: 1

=head2 currency_serial

  data_type: 'integer'
  is_nullable: 0

=head2 name

  data_type: 'varchar'
  is_nullable: 0
  size: 255

=head2 variant

  data_type: 'varchar'
  is_nullable: 0
  size: 255

=head2 betting_structure

  data_type: 'varchar'
  is_nullable: 0
  size: 255

=head2 small_blind

  data_type: 'bigint'
  extra: {unsigned => 1}
  is_nullable: 0

=head2 big_blind

  data_type: 'bigint'
  extra: {unsigned => 1}
  is_nullable: 0

=head2 ante_value

  data_type: 'bigint'
  extra: {unsigned => 1}
  is_nullable: 0

=head2 ante_bring_in

  data_type: 'bigint'
  extra: {unsigned => 1}
  is_nullable: 0

=head2 limit_type

  data_type: 'varchar'
  is_nullable: 0
  size: 20

=head2 betting_description

  data_type: 'varchar'
  is_nullable: 0
  size: 255

=head2 skin

  data_type: 'varchar'
  default_value: 'default'
  is_nullable: 0
  size: 255

=head2 tourney_serial

  data_type: 'integer'
  default_value: 0
  extra: {unsigned => 1}
  is_nullable: 0

=cut

__PACKAGE__->add_columns(
  "serial",
  {
    data_type => "integer",
    extra => { unsigned => 1 },
    is_auto_increment => 1,
    is_nullable => 0,
  },
  "resthost_serial",
  {
    data_type => "integer",
    default_value => 0,
    extra => { unsigned => 1 },
    is_nullable => 0,
  },
  "seats",
  { data_type => "tinyint", default_value => 10, is_nullable => 1 },
  "average_pot",
  {
    data_type => "integer",
    default_value => 0,
    extra => { unsigned => 1 },
    is_nullable => 1,
  },
  "hands_per_hour",
  {
    data_type => "integer",
    default_value => 0,
    extra => { unsigned => 1 },
    is_nullable => 1,
  },
  "percent_flop",
  { data_type => "tinyint", default_value => 0, is_nullable => 1 },
  "players",
  { data_type => "tinyint", default_value => 0, is_nullable => 1 },
  "observers",
  {
    data_type => "integer",
    default_value => 0,
    extra => { unsigned => 1 },
    is_nullable => 1,
  },
  "waiting",
  { data_type => "tinyint", default_value => 0, is_nullable => 1 },
  "player_timeout",
  {
    data_type => "integer",
    default_value => 60,
    extra => { unsigned => 1 },
    is_nullable => 1,
  },
  "muck_timeout",
  {
    data_type => "integer",
    default_value => 5,
    extra => { unsigned => 1 },
    is_nullable => 1,
  },
  "currency_serial",
  { data_type => "integer", is_nullable => 0 },
  "name",
  { data_type => "varchar", is_nullable => 0, size => 255 },
  "variant",
  { data_type => "varchar", is_nullable => 0, size => 255 },
  "betting_structure",
  { data_type => "varchar", is_nullable => 0, size => 255 },
  "small_blind",
  { data_type => "bigint", extra => { unsigned => 1 }, is_nullable => 0 },
  "big_blind",
  { data_type => "bigint", extra => { unsigned => 1 }, is_nullable => 0 },
  "ante_value",
  { data_type => "bigint", extra => { unsigned => 1 }, is_nullable => 0 },
  "ante_bring_in",
  { data_type => "bigint", extra => { unsigned => 1 }, is_nullable => 0 },
  "limit_type",
  { data_type => "varchar", is_nullable => 0, size => 20 },
  "betting_description",
  { data_type => "varchar", is_nullable => 0, size => 255 },
  "skin",
  {
    data_type => "varchar",
    default_value => "default",
    is_nullable => 0,
    size => 255,
  },
  "tourney_serial",
  {
    data_type => "integer",
    default_value => 0,
    extra => { unsigned => 1 },
    is_nullable => 0,
  },
);
__PACKAGE__->set_primary_key("serial");
__PACKAGE__->add_unique_constraint("name", ["name"]);


# Created by DBIx::Class::Schema::Loader v0.07010 @ 2011-09-25 13:41:03
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:zaJQIyj0H+kR3ho+s6JRTg


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

__PACKAGE__->has_one( 
    resthost => 'Room::Schema::PokerNetwork::Result::Resthost',
    { 'foreign.serial' => 'self.resthost_serial' },
);


sub host {
    my ($self) = @_;

    if ($self->resthost->host) {
        return $self->resthost->host .':'. $self->resthost->port;
    }
}

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
