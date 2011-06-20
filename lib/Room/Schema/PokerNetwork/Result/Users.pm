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
  "Core",
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
  extra: {unsigned => 1}
  is_foreign_key: 1
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
  size: 40

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
    extra => { unsigned => 1 },
    is_foreign_key => 1,
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
  { data_type => "varchar", is_nullable => 1, size => 40 },
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

=head1 RELATIONS

=head2 affiliate

Type: belongs_to

Related object: L<Room::Schema::PokerNetwork::Result::Affiliates>

=cut

__PACKAGE__->belongs_to(
  "affiliate",
  "Room::Schema::PokerNetwork::Result::Affiliates",
  { serial => "affiliate" },
);


# Created by DBIx::Class::Schema::Loader v0.07010 @ 2011-06-20 00:12:57
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:5/tqO6H1Qu+FUIi1JvY+lg

use JSON::XS;
use Hash::AsObject;

__PACKAGE__->add_columns(
  'password' => {
    data_type           => 'VARCHAR',
    size                => 40,
    encode_column       => 1,
    encode_class        => 'Digest',
    encode_check_method => 'check_password',
    encode_args         => {
                             algorithm    => 'SHA-1',
                             format       => 'hex',
                           },
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
  'deposits' => 'Room::Schema::PokerNetwork::Result::Deposits',
  { 'foreign.user_serial' => 'self.serial' },
);

__PACKAGE__->has_many(
  'withdrawals' => 'Room::Schema::PokerNetwork::Result::Withdrawal',
  { 'foreign.user_serial' => 'self.serial' },
);


sub get_bitcoin_deposit_address {
  my ($self) = @_;

  if (! $self->data->bitcoin_address) {
    
  }

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
