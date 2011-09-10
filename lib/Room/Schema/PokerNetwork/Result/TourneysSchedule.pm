package Room::Schema::PokerNetwork::Result::TourneysSchedule;

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

Room::Schema::PokerNetwork::Result::TourneysSchedule

=cut

__PACKAGE__->table("tourneys_schedule");

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

=head2 name

  data_type: 'varchar'
  is_nullable: 1
  size: 200

=head2 description_short

  data_type: 'varchar'
  is_nullable: 1
  size: 64

=head2 description_long

  data_type: 'text'
  is_nullable: 1

=head2 players_quota

  data_type: 'integer'
  default_value: 10
  is_nullable: 1

=head2 players_min

  data_type: 'integer'
  default_value: 2
  is_nullable: 1

=head2 variant

  data_type: 'varchar'
  is_nullable: 1
  size: 32

=head2 betting_structure

  data_type: 'varchar'
  is_nullable: 1
  size: 32

=head2 seats_per_game

  data_type: 'integer'
  default_value: 10
  is_nullable: 1

=head2 player_timeout

  data_type: 'integer'
  default_value: 60
  is_nullable: 1

=head2 currency_serial

  data_type: 'integer'
  is_nullable: 1

=head2 prize_currency

  data_type: 'integer'
  default_value: 0
  extra: {unsigned => 1}
  is_nullable: 1

=head2 prize_min

  data_type: 'integer'
  default_value: 0
  is_nullable: 1

=head2 bailor_serial

  data_type: 'integer'
  default_value: 0
  is_nullable: 1

=head2 buy_in

  data_type: 'integer'
  default_value: 0
  is_nullable: 1

=head2 rake

  data_type: 'integer'
  default_value: 0
  is_nullable: 1

=head2 sit_n_go

  data_type: 'char'
  default_value: 'y'
  is_nullable: 1
  size: 1

=head2 breaks_first

  data_type: 'integer'
  default_value: 7200
  is_nullable: 1

=head2 breaks_interval

  data_type: 'integer'
  default_value: 3600
  is_nullable: 1

=head2 breaks_duration

  data_type: 'integer'
  default_value: 300
  is_nullable: 1

=head2 rebuy_delay

  data_type: 'integer'
  default_value: 0
  is_nullable: 1

=head2 add_on

  data_type: 'integer'
  default_value: 0
  is_nullable: 1

=head2 add_on_delay

  data_type: 'integer'
  default_value: 60
  is_nullable: 1

=head2 start_time

  data_type: 'integer'
  default_value: 0
  is_nullable: 1

=head2 register_time

  data_type: 'integer'
  default_value: 0
  is_nullable: 1

=head2 active

  data_type: 'char'
  default_value: 'y'
  is_nullable: 1
  size: 1

=head2 respawn

  data_type: 'char'
  default_value: 'n'
  is_nullable: 1
  size: 1

=head2 respawn_interval

  data_type: 'integer'
  default_value: 0
  is_nullable: 1

=head2 currency_serial_from_date_format

  data_type: 'varchar'
  is_nullable: 1
  size: 16

=head2 prize_currency_from_date_format

  data_type: 'varchar'
  is_nullable: 1
  size: 16

=head2 satellite_of

  data_type: 'integer'
  default_value: 0
  extra: {unsigned => 1}
  is_nullable: 1

=head2 via_satellite

  data_type: 'tinyint'
  default_value: 0
  is_nullable: 1

=head2 satellite_player_count

  data_type: 'integer'
  default_value: 0
  extra: {unsigned => 1}
  is_nullable: 1

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
  "name",
  { data_type => "varchar", is_nullable => 1, size => 200 },
  "description_short",
  { data_type => "varchar", is_nullable => 1, size => 64 },
  "description_long",
  { data_type => "text", is_nullable => 1 },
  "players_quota",
  { data_type => "integer", default_value => 10, is_nullable => 1 },
  "players_min",
  { data_type => "integer", default_value => 2, is_nullable => 1 },
  "variant",
  { data_type => "varchar", is_nullable => 1, size => 32 },
  "betting_structure",
  { data_type => "varchar", is_nullable => 1, size => 32 },
  "seats_per_game",
  { data_type => "integer", default_value => 10, is_nullable => 1 },
  "player_timeout",
  { data_type => "integer", default_value => 60, is_nullable => 1 },
  "currency_serial",
  { data_type => "integer", is_nullable => 1 },
  "prize_currency",
  {
    data_type => "integer",
    default_value => 0,
    extra => { unsigned => 1 },
    is_nullable => 1,
  },
  "prize_min",
  { data_type => "integer", default_value => 0, is_nullable => 1 },
  "bailor_serial",
  { data_type => "integer", default_value => 0, is_nullable => 1 },
  "buy_in",
  { data_type => "integer", default_value => 0, is_nullable => 1 },
  "rake",
  { data_type => "integer", default_value => 0, is_nullable => 1 },
  "sit_n_go",
  { data_type => "char", default_value => "y", is_nullable => 1, size => 1 },
  "breaks_first",
  { data_type => "integer", default_value => 7200, is_nullable => 1 },
  "breaks_interval",
  { data_type => "integer", default_value => 3600, is_nullable => 1 },
  "breaks_duration",
  { data_type => "integer", default_value => 300, is_nullable => 1 },
  "rebuy_delay",
  { data_type => "integer", default_value => 0, is_nullable => 1 },
  "add_on",
  { data_type => "integer", default_value => 0, is_nullable => 1 },
  "add_on_delay",
  { data_type => "integer", default_value => 60, is_nullable => 1 },
  "start_time",
  { data_type => "integer", default_value => 0, is_nullable => 1 },
  "register_time",
  { data_type => "integer", default_value => 0, is_nullable => 1 },
  "active",
  { data_type => "char", default_value => "y", is_nullable => 1, size => 1 },
  "respawn",
  { data_type => "char", default_value => "n", is_nullable => 1, size => 1 },
  "respawn_interval",
  { data_type => "integer", default_value => 0, is_nullable => 1 },
  "currency_serial_from_date_format",
  { data_type => "varchar", is_nullable => 1, size => 16 },
  "prize_currency_from_date_format",
  { data_type => "varchar", is_nullable => 1, size => 16 },
  "satellite_of",
  {
    data_type => "integer",
    default_value => 0,
    extra => { unsigned => 1 },
    is_nullable => 1,
  },
  "via_satellite",
  { data_type => "tinyint", default_value => 0, is_nullable => 1 },
  "satellite_player_count",
  {
    data_type => "integer",
    default_value => 0,
    extra => { unsigned => 1 },
    is_nullable => 1,
  },
);
__PACKAGE__->set_primary_key("serial");


# Created by DBIx::Class::Schema::Loader v0.07010 @ 2011-09-10 02:25:23
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:yYpaNSuMISJa5Ryzs7ccWA

__PACKAGE__->load_components( qw( DateTime::Epoch TimeStamp) );
__PACKAGE__->add_columns(
  "start_time",
  { data_type => "INT", inflate_datetime => 'epoch', is_nullable => 1, size => 11 },
  "register_time",
  { data_type => "INT", inflate_datetime => 'epoch', is_nullable => 1, size => 11 },
);

__PACKAGE__->filter_column(
  prize_min => {
    filter_to_storage => '__filter_multi',
    filter_from_storage =>  '__filter_divide',
  }
);


__PACKAGE__->filter_column(
  rake => {
    filter_to_storage => '__filter_multi',
    filter_from_storage =>  '__filter_divide',
  }
);


__PACKAGE__->filter_column(
  buy_in => {
    filter_to_storage => '__filter_multi',
    filter_from_storage =>  '__filter_divide',
  }
);


sub __filter_multi { my $self = shift; shift() * 100 }
sub __filter_divide { my $self = shift; shift() / 100 }


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
