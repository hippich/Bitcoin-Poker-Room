package Room::Schema::PokerNetwork::Result::Monitor;

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
__PACKAGE__->table("monitor");
__PACKAGE__->add_columns(
  "serial",
  { data_type => "BIGINT", default_value => undef, is_nullable => 0, size => 20 },
  "created",
  {
    data_type => "TIMESTAMP",
    default_value => "CURRENT_TIMESTAMP",
    is_nullable => 0,
    size => 14,
  },
  "event",
  { data_type => "TINYINT", default_value => undef, is_nullable => 0, size => 4 },
  "param1",
  { data_type => "BIGINT", default_value => undef, is_nullable => 0, size => 20 },
  "param2",
  { data_type => "BIGINT", default_value => undef, is_nullable => 0, size => 20 },
  "param3",
  { data_type => "BIGINT", default_value => undef, is_nullable => 0, size => 20 },
);
__PACKAGE__->set_primary_key("serial");


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2010-08-27 00:26:16
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:QBu5Au49RvE23mVyvNuLRw


# You can replace this text with custom content, and it will be preserved on regeneration
1;
