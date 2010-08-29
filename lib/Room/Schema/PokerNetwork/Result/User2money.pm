package Room::Schema::PokerNetwork::Result::User2money;

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
__PACKAGE__->table("user2money");
__PACKAGE__->add_columns(
  "user_serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "currency_serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "amount",
  { data_type => "BIGINT", default_value => undef, is_nullable => 0, size => 20 },
  "rake",
  { data_type => "BIGINT", default_value => 0, is_nullable => 0, size => 20 },
  "points",
  { data_type => "BIGINT", default_value => 0, is_nullable => 0, size => 20 },
);
__PACKAGE__->set_primary_key("user_serial", "currency_serial");


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2010-08-27 00:26:16
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:6PSsuoZ8jb9gQ+2LnBFbCw


__PACKAGE__->filter_column(
  amount => {
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


sub __filter_multi { my $self = shift; shift() * 100 }
sub __filter_divide { my $self = shift; shift() / 100 }

__PACKAGE__->has_one(
  'currency' => 'Room::Schema::PokerNetwork::Result::Currencies',
  { 'foreign.serial' => 'self.currency_serial' },
);


1;
