package Room::Schema::PokerNetwork::Result::Rank;

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
__PACKAGE__->table("rank");
__PACKAGE__->add_columns(
  "user_serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "currency_serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "amount",
  { data_type => "BIGINT", default_value => undef, is_nullable => 0, size => 20 },
  "rank",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "percentile",
  { data_type => "TINYINT", default_value => 0, is_nullable => 0, size => 3 },
);
__PACKAGE__->set_primary_key("user_serial", "currency_serial");


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2010-08-27 00:26:16
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:gWnYdOCqtXIsUKvUPcjJ7g


# You can replace this text with custom content, and it will be preserved on regeneration
1;
