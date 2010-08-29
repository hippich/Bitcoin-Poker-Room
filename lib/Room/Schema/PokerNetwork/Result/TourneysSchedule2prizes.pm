package Room::Schema::PokerNetwork::Result::TourneysSchedule2prizes;

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
__PACKAGE__->table("tourneys_schedule2prizes");
__PACKAGE__->add_columns(
  "tourneys_schedule_serial",
  { data_type => "INT", default_value => undef, is_nullable => 1, size => 11 },
  "prize_serial",
  { data_type => "INT", default_value => undef, is_nullable => 1, size => 11 },
);


# Created by DBIx::Class::Schema::Loader v0.04006 @ 2010-08-27 00:26:16
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:ef6o2Kna26hEXiygRjM4iQ


# You can replace this text with custom content, and it will be preserved on regeneration
1;
