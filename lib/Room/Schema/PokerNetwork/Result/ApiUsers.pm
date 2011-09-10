package Room::Schema::PokerNetwork::Result::ApiUsers;

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
);

=head1 NAME

Room::Schema::PokerNetwork::Result::ApiUsers

=cut

__PACKAGE__->table("api_users");

=head1 ACCESSORS

=head2 id

  data_type: 'integer'
  is_auto_increment: 1
  is_nullable: 0

=head2 email

  data_type: 'varchar'
  is_nullable: 0
  size: 255

=head2 api_key

  data_type: 'varchar'
  is_nullable: 0
  size: 255

=head2 secret

  data_type: 'varchar'
  is_nullable: 0
  size: 255

=cut

__PACKAGE__->add_columns(
  "id",
  { data_type => "integer", is_auto_increment => 1, is_nullable => 0 },
  "email",
  { data_type => "varchar", is_nullable => 0, size => 255 },
  "api_key",
  { data_type => "varchar", is_nullable => 0, size => 255 },
  "secret",
  { data_type => "varchar", is_nullable => 0, size => 255 },
);
__PACKAGE__->set_primary_key("id");
__PACKAGE__->add_unique_constraint("key_secret", ["api_key", "secret"]);


# Created by DBIx::Class::Schema::Loader v0.07010 @ 2011-09-10 02:20:28
# DO NOT MODIFY THIS OR ANYTHING ABOVE! md5sum:1M+gF15B+99CQTq3Q6WonA


# You can replace this text with custom code or comments, and it will be preserved on regeneration
1;
