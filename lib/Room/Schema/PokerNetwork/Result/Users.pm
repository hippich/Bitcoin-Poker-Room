package Room::Schema::PokerNetwork::Result::Users;

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

Room::Schema::PokerNetwork::Result::Users

=cut

__PACKAGE__->table("users");

=head1 ACCESSORS

=head2 serial

  data_type: 'integer'
  extra: {unsigned => 1}
  is_auto_increment: 1
  is_nullable: 0

=head2 created

  data_type: 'integer'
  extra: {unsigned => 1}
  is_nullable: 0

=head2 name

  data_type: 'varchar'
  is_nullable: 1
  size: 64

=head2 email

  data_type: 'varchar'
  is_nullable: 1
  size: 128

=head2 affiliate

  data_type: 'integer'
  default_value: 0
  extra: {unsigned => 1}
  is_nullable: 1

=head2 skin_url

  data_type: 'varchar'
  default_value: 'random'
  is_nullable: 1
  size: 255

=head2 skin_outfit

  data_type: 'text'
  is_nullable: 1

=head2 skin_image

  data_type: 'text'
  is_nullable: 1

=head2 skin_image_type

  data_type: 'varchar'
  default_value: 'image/png'
  is_nullable: 1
  size: 32

=head2 password

  data_type: 'varchar'
  is_nullable: 1
  size: 512

=head2 privilege

  data_type: 'integer'
  default_value: 1
  is_nullable: 1

=head2 locale

  data_type: 'varchar'
  default_value: 'en_US'
  is_nullable: 1
  size: 32

=head2 rating

  data_type: 'integer'
  default_value: 1000
  is_nullable: 1

=head2 future_rating

  data_type: 'float'
  default_value: 1000
  is_nullable: 1

=head2 games_count

  data_type: 'integer'
  default_value: 0
  is_nullable: 1

=head2 data

  data_type: 'text'
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
  "created",
  { data_type => "integer", extra => { unsigned => 1 }, is_nullable => 0 },
  "name",
  { data_type => "varchar", is_nullable => 1, size => 64 },
  "email",
  { data_type => "varchar", is_nullable => 1, size => 128 },
  "affiliate",
  {
    data_type => "integer",
    default_value => 0,
    extra => { unsigned => 1 },
    is_nullable => 1,
  },
  "skin_url",
  {
    data_type => "varchar",
    default_value => "random",
    is_nullable => 1,
    size => 255,
  },
  "skin_outfit",
  { data_type => "text", is_nullable => 1 },
  "skin_image",
  { data_type => "text", is_nullable => 1 },
  "skin_image_type",
  {
    data_type => "varchar",
    default_value => "image/png",
    is_nullable => 1,
    size => 32,
  },
  "password",
  { data_type => "varchar", is_nullable => 1, size => 512 },
  "privilege",
  { data_type => "integer", default_value => 1, is_nullable => 1 },
  "locale",
  {
    data_type => "varchar",
    default_value => "en_US",
    is_nullable => 1,
    size => 32,
  },
  "rating",
  { data_type => "integer", default_value => 1000, is_nullable => 1 },
  "future_rating",
  { data_type => "float", default_value => 1000, is_nullable => 1 },
  "games_count",
  { data_type => "integer", default_value => 0, is_nullable => 1 },
  "data",
  { data_type => "text", is_nullable => 1 },
);
__PACKAGE__->set_primary_key("serial");
__PACKAGE__->add_unique_constraint("email_idx", ["email"]);


# Created by DBIx::Class::Schema::Loader v0.07010 @ 2011-09-10 02:25:23
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:najOrRPxquNBM6d34xxy8Q

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


=head2 get_bitcoin_deposit_address 

Retrieve user's stored bitcoin deposit address.

=cut 
sub get_bitcoin_deposit_address {
  my ($self) = @_;

  return $self->data->bitcoin_address;
}


=head2 balance 

Retrieve single currency balance Result object 

=cut
sub balance {
    my ($self, $serial) = @_;

    return $self->balances->find_or_create({ currency_serial => $serial });
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
