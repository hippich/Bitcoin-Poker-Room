package Room::Schema::PokerNetwork::Result::Currencies;

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
__PACKAGE__->table("currencies");
__PACKAGE__->add_columns(
  "serial",
  { data_type => "INT", default_value => undef, is_nullable => 0, size => 11 },
  "url",
  { data_type => "CHAR", default_value => undef, is_nullable => 0, size => 255 },
  "symbol",
  { data_type => "CHAR", default_value => undef, is_nullable => 1, size => 8 },
  "name",
  { data_type => "CHAR", default_value => undef, is_nullable => 1, size => 32 },
  "cash_out",
  { data_type => "INT", default_value => undef, is_nullable => 1, size => 11 },
);
__PACKAGE__->set_primary_key("serial", "url");
__PACKAGE__->add_unique_constraint("serial", ["serial"]);
__PACKAGE__->add_unique_constraint("url", ["url"]);


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2010-08-27 00:26:16
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:i6Ef4a/aqKYXOmKQohg07Q


# You can replace this text with custom content, and it will be preserved on regeneration
1;
