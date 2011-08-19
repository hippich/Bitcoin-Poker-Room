package Room::Schema::PokerNetwork::Result::Tourneys;

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
__PACKAGE__->table("tourneys");
__PACKAGE__->add_columns(
  "serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "resthost_serial",
  { data_type => "INT", default_value => 0, is_nullable => 0, size => 10 },
  "name",
  {
    data_type => "VARCHAR",
    default_value => undef,
    is_nullable => 1,
    size => 200,
  },
  "description_short",
  {
    data_type => "VARCHAR",
    default_value => undef,
    is_nullable => 1,
    size => 64,
  },
  "description_long",
  {
    data_type => "TEXT",
    default_value => undef,
    is_nullable => 1,
    size => 65535,
  },
  "players_quota",
  { data_type => "INT", default_value => 10, is_nullable => 1, size => 11 },
  "players_min",
  { data_type => "INT", default_value => 2, is_nullable => 1, size => 11 },
  "variant",
  {
    data_type => "VARCHAR",
    default_value => undef,
    is_nullable => 1,
    size => 32,
  },
  "betting_structure",
  {
    data_type => "VARCHAR",
    default_value => undef,
    is_nullable => 1,
    size => 32,
  },
  "seats_per_game",
  { data_type => "INT", default_value => 10, is_nullable => 1, size => 11 },
  "player_timeout",
  { data_type => "INT", default_value => 60, is_nullable => 1, size => 11 },
  "currency_serial",
  { data_type => "INT", default_value => undef, is_nullable => 1, size => 11 },
  "prize_currency",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 10 },
  "prize_min",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "bailor_serial",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "buy_in",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "rake",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "sit_n_go",
  { data_type => "CHAR", default_value => "y", is_nullable => 1, size => 1 },
  "breaks_first",
  { data_type => "INT", default_value => 7200, is_nullable => 1, size => 11 },
  "breaks_interval",
  { data_type => "INT", default_value => 3600, is_nullable => 1, size => 11 },
  "breaks_duration",
  { data_type => "INT", default_value => 300, is_nullable => 1, size => 11 },
  "rebuy_delay",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "add_on",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "add_on_delay",
  { data_type => "INT", default_value => 60, is_nullable => 1, size => 11 },
  "start_time",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "satellite_of",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 10 },
  "via_satellite",
  { data_type => "TINYINT", default_value => 0, is_nullable => 1, size => 4 },
  "satellite_player_count",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 10 },
  "finish_time",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "state",
  {
    data_type => "VARCHAR",
    default_value => "registering",
    is_nullable => 1,
    size => 16,
  },
  "schedule_serial",
  { data_type => "INT", default_value => undef, is_nullable => 1, size => 11 },
  "add_on_count",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "rebuy_count",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
);
__PACKAGE__->set_primary_key("serial");


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2010-09-27 11:47:31
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:7TyTlrEhWw004Jae61zkSw

__PACKAGE__->load_components( qw( DateTime::Epoch TimeStamp) );


# Relationships

__PACKAGE__->has_many(
    'usertourneys' => 'Room::Schema::PokerNetwork::Result::User2tourney',
    { 'foreign.tourney_serial' => 'self.serial' },
);

__PACKAGE__->many_to_many(
    users => 'usertourneys', 'user'
);

__PACKAGE__->many_to_many(
    tables => 'usertourneys', 'tourney_table'
);

# Inflators

__PACKAGE__->add_columns(
  "start_time",
  { data_type => "INT", inflate_datetime => 'epoch', is_nullable => 1, size => 11 },
  "finish_time",
  { data_type => "INT", inflate_datetime => 'epoch', is_nullable => 1, size => 11 },
);



# Filters

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


sub get_users_registered {
    my ($self) = @_;

    return $self->usertourneys->count;
}


sub get_table_serial {
    my ($self, $serial) = @_;
    my $usertourneys = $self->usertourneys;
    
    return $usertourneys->first->table_serial unless $serial;

    my $users = $usertourneys->find({user_serial => $serial});

    return $users->table_serial unless !$users;

    return $usertourneys->first->table_serial;
}


sub is_user_registered {
    my ($self, $serial) = @_;

    if ($self->usertourneys->find({user_serial => $serial})) {
        return 1;
    }
    else {
        return 0;
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
