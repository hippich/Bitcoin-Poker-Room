package Room::Schema::PokerNetwork::Result::User2tourney;

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
__PACKAGE__->table("user2tourney");
__PACKAGE__->add_columns(
  "user_serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 11 },
  "currency_serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 10 },
  "tourney_serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 11 },
  "table_serial",
  { data_type => "INT", default_value => undef, is_nullable => 1, size => 11 },
  "rank",
  { data_type => "INT", default_value => -1, is_nullable => 1, size => 11 },
);
__PACKAGE__->set_primary_key("user_serial", "tourney_serial");


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2010-08-27 00:26:16
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:qC4grysymfZjP3Rza9KxvA


# You can replace this text with custom content, and it will be preserved on regeneration
1;
