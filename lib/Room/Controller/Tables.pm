package Room::Controller::Tables;
use Moose;
use namespace::autoclean;

use Net::Twitter::Lite;

BEGIN {extends 'Catalyst::Controller'; }

=head1 NAME

Room::Controller::Tables - Catalyst Controller

=head1 DESCRIPTION

Catalyst Controller.

=head1 METHODS

=cut

=head2 index

Show list of all existing tables.

=cut
sub index :Path :Args(0) {
    my ( $self, $c ) = @_;

    @{$c->stash->{servers}} = $c->model('PokerNetwork::Resthost')->all;
    @{$c->stash->{currencies}} = $c->model('PokerNetwork::Currencies')->all;
    
    my $params = $c->req->params;
    my $params_count = scalar( keys %{$params} );

    if ($params_count > 0) {
        # Show filtered tables
    }
    else {
        # Show popular tables 
    }

}


=head2 my 

Return all tables curreny user is sit at.

=cut
sub my :Local :Args(0) {
    my ($self, $c) = @_;

    $c->page_not_found unless $c->user;

    $c->stash->{tables} = $c->user->tables;
}

=head2 table 

Begin of table actions chain. 

=cut
sub table :Chained :CaptureArgs(1) {
    my ($self, $c, $game_id) = @_;

    $c->stash->{table} = $c->model('PokerNetwork::Pokertables')->find($game_id);

    $c->page_not_found unless $c->stash->{table};

    if (my $tourney = $c->stash->{table}->tourney) {
        if ($c->user && $tourney->is_user_registered($c->user->serial)) {
            $c->res->redirect(
                $c->uri_for(
                    '/tourneys/'. $tourney->serial .'/table'
                )
            );
            return;
        }
    }

    $c->stash->{url} = $c->get_rest_url('table-' . $game_id);
    $c->stash->{uid} = ($c->user) ? $c->user->serial : 0;
    $c->stash->{auth} = $c->session->{pokernetwork_auth} || 'N';
}


=head2 view 

View table 

=cut 
sub view :Chained('table') :Args(0) {
    my ($self, $c) = @_;
}

=head1 AUTHOR

Pavel Karoukin

=head1 LICENSE

Copyright (C) 2010 Pavel A. Karoukin <pavel@yepcorp.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

=cut

__PACKAGE__->meta->make_immutable;

