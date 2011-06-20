package Room::Schema::PokerNetwork::ResultSet::Users;

use strict;
use warnings;
use base 'DBIx::Class::ResultSet';

=head2 affiliate_username

A predefined search for an affiliate's username.

=cut

sub affiliate_username {
  my ($self, $affiliate_serial, $username) = @_;

  return $self->search({
    affiliate => { '=' => $affiliate_serial },
    name => { '=' => $username }
  });
}

1;
