package Room::Schema::PokerNetwork::ResultSet::Pokertables;

use strict;
use warnings;

use base 'DBIx::Class::ResultSet';

=head2 cash_games

A predefined search for all BTC ring games.

=cut

sub cash_games {
    my ($self) = @_;

    return $self->search({ -and => [
        currency_serial => 1,
        tourney_serial => 0
        ]},
        { order_by => 'players DESC'},
    );
}

1;
