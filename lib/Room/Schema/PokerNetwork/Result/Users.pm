package Room::Schema::PokerNetwork::Result::Users;

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
__PACKAGE__->table("users");
__PACKAGE__->add_columns(
  "serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "created",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "name",
  {
    data_type => "VARCHAR",
    default_value => undef,
    is_nullable => 1,
    size => 64,
  },
  "email",
  {
    data_type => "VARCHAR",
    default_value => undef,
    is_nullable => 1,
    size => 128,
  },
  "affiliate",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 10 },
  "skin_url",
  {
    data_type => "VARCHAR",
    default_value => "random",
    is_nullable => 1,
    size => 255,
  },
  "skin_outfit",
  {
    data_type => "TEXT",
    default_value => undef,
    is_nullable => 1,
    size => 65535,
  },
  "skin_image",
  {
    data_type => "TEXT",
    default_value => undef,
    is_nullable => 1,
    size => 65535,
  },
  "skin_image_type",
  {
    data_type => "VARCHAR",
    default_value => "image/png",
    is_nullable => 1,
    size => 32,
  },
  "password",
  {
    data_type => "VARCHAR",
    default_value => undef,
    is_nullable => 1,
    size => 40,
  },
  "privilege",
  { data_type => "INT", default_value => 1, is_nullable => 1, size => 11 },
  "locale",
  {
    data_type => "VARCHAR",
    default_value => "en_US",
    is_nullable => 1,
    size => 32,
  },
  "rating",
  { data_type => "INT", default_value => 1000, is_nullable => 1, size => 11 },
  "future_rating",
  { data_type => "FLOAT", default_value => 1000, is_nullable => 1, size => 32 },
  "games_count",
  { data_type => "INT", default_value => 0, is_nullable => 1, size => 11 },
  "data",
  {
    data_type => "TEXT",
    default_value => undef,
    is_nullable => 1,
    size => 65535,
  },
);
__PACKAGE__->set_primary_key("serial");
__PACKAGE__->add_unique_constraint("email_idx", ["email"]);


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2010-09-27 11:47:31
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:vEdFh5CdQczNMcB+q/BW4A

use JSON::XS;
use Hash::AsObject;
use Digest::SHA1 qw(sha1_hex);

__PACKAGE__->add_columns(
    'password' => {
        data_type           => 'VARCHAR',
        size                => 512,
        encode_column       => 1,
        encode_class        => 'Crypt::Eksblowfish::Bcrypt',
        encode_args         => { key_nul => 0, cost => 8 },
        encode_check_method => '_check_password_blowfish',
    },
);

__PACKAGE__->inflate_column(
    'created',
    {
      inflate => sub {
        DateTime->from_epoch(
          epoch => shift
        );
      },
      deflate => sub {
        shift->epoch;
      },
    },
);

__PACKAGE__->add_json_columns(
  data => qw/bitcoin_address bitcoins_received request_password hide_gravatar emergency_address/,
);

__PACKAGE__->has_many(
  'balances' => 'Room::Schema::PokerNetwork::Result::User2money',
  { 'foreign.user_serial' => 'self.serial' },
);

__PACKAGE__->has_many(
  'userhands' => 'Room::Schema::PokerNetwork::Result::User2hand',
  { 'foreign.user_serial' => 'self.serial' },
);
__PACKAGE__->many_to_many(
  hands => 'userhands', 'hand'
);

__PACKAGE__->has_many(
  'usertables' => 'Room::Schema::PokerNetwork::Result::User2table',
  { 'foreign.user_serial' => 'self.serial' },
);
__PACKAGE__->many_to_many(
  tables => 'usertables', 'pokertable'
);

__PACKAGE__->has_many(
  'usertourneys' => 'Room::Schema::PokerNetwork::Result::User2tourney',
  { 'foreign.user_serial' => 'self.serial' },
);
__PACKAGE__->many_to_many(
  tourneys => 'usertourneys', 'tourneys'
);

__PACKAGE__->has_many(
  'deposits' => 'Room::Schema::PokerNetwork::Result::Deposits',
  { 'foreign.user_serial' => 'self.serial' },
);

__PACKAGE__->has_many(
  'withdrawals' => 'Room::Schema::PokerNetwork::Result::Withdrawal',
  { 'foreign.user_serial' => 'self.serial' },
);


=head2 check_password 

Used for authentication. This function first check hash for BCrypt 
hash and if check fails - tries SHA hash. If both checks fails - 
return false value.

=cut 

sub check_password {
    my ($self, $password) = @_;
    my $result;

    eval {
        $result = $self->_check_password_blowfish($password);
    };

    if (!$result) {
        $result = $self->password eq sha1_hex($password);
    }

    return $result;
}


sub get_bitcoin_deposit_address {
  my ($self) = @_;

  return $self->data->bitcoin_address;
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
