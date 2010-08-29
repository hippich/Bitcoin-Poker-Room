package Room::Schema::PokerNetwork::Result::Route;

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
__PACKAGE__->table("route");
__PACKAGE__->add_columns(
  "table_serial",
  { data_type => "INT", default_value => 0, is_nullable => 0, size => 10 },
  "tourney_serial",
  { data_type => "INT", default_value => 0, is_nullable => 0, size => 10 },
  "modified",
  { data_type => "INT", default_value => undef, is_nullable => 1, size => 10 },
  "resthost_serial",
  { data_type => "INT", default_value => undef, is_nullable => 1, size => 10 },
);
__PACKAGE__->set_primary_key("table_serial", "tourney_serial");


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2010-08-27 00:26:16
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:k6umH5YZHGcZ7ti6ZadxsQ


# You can replace this text with custom content, and it will be preserved on regeneration
1;
