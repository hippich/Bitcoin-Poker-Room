package Room::Schema::PokerNetwork::Result::User2table;

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
__PACKAGE__->table("user2table");
__PACKAGE__->add_columns(
  "user_serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "table_serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "money",
  { data_type => "INT", default_value => 0, is_nullable => 0, size => 11 },
  "bet",
  { data_type => "INT", default_value => 0, is_nullable => 0, size => 11 },
);
__PACKAGE__->set_primary_key("user_serial", "table_serial");


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2010-08-27 00:26:16
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:KwfFs3yeCiDqXyzQ/z5R6g


# You can replace this text with custom content, and it will be preserved on regeneration
1;
