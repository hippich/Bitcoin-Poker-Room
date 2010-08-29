package Room::Schema::PokerNetwork::Result::Users;

use strict;
use warnings;

use base 'DBIx::Class';

__PACKAGE__->load_components(
  "InflateColumn::DateTime",
  "FrozenColumns",
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


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2010-08-26 21:04:22
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:4TfnDhaW/o97I6JP9kbmcw

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
  data => qw/bitcoin_address bitcoins_received/,
);

__PACKAGE__->has_many(
  'balances' => 'Room::Schema::PokerNetwork::Result::User2money',
  { 'foreign.user_serial' => 'self.serial' },
);

__PACKAGE__->has_many(
  'deposits' => 'Room::Schema::PokerNetwork::Result::Deposits',
  { 'foreign.user_serial' => 'self.serial' },
);


sub get_bitcoin_deposit_address {
  my ($self) = @_;

  if (! $self->data->bitcoin_address) {
    
  }

  return $self->data->bitcoin_address;
}

1;
