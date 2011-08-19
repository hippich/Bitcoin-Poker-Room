package Room::Controller::Tourneys;
use Moose;
use namespace::autoclean;

BEGIN {extends 'Catalyst::Controller'; }

=head1 NAME

Room::Controller::Tourneys - Catalyst Controller

=head1 DESCRIPTION

Catalyst Controller.

=head1 METHODS

=cut


=head2 base 

Chain start.

=cut 
sub base :Chained :PathPart('tourneys') :CaptureArgs(0) {}

=head2 index

Show list of all tourneys

=cut
sub index :Chained('base') :PathPart('') :Args(0) {
    my ( $self, $c ) = @_;

    $c->stash->{tourneys} = $c->model('PokerNetwork::Tourneys')->search({
        state => { '<>' => 'canceled' },
    }, {
        page => $c->req->params->{page} || 1,
        rows => 20,
        order_by => {
            -desc => 'serial',
        },
    });
}


=head2 details_base 


=cut
sub tourney_base :Chained('base') :PathPart('') :CaptureArgs(1) {
    my ($self, $c, $serial) = @_;
    $c->stash->{tourney} = $c->model('PokerNetwork::Tourneys')->find($serial);
    $c->res->redirect('/404-not-found') unless $c->stash->{tourney};

    $c->stash->{url} = $c->config->{rest_url} || '/POKER_REST';
    $c->stash->{uid} = ($c->user) ? $c->user->serial : 0;
    $c->stash->{auth} = $c->session->{pokernetwork_auth} || 'N';
}

=head2 details 

Tourney details page. Here player can check tourney stats and register for tourney.

=cut
sub details :Chained('tourney_base') :PathPart('') :Args(0) {}


=head2 table 

For currently logged in user opens his table.

=cut 
sub table :Chained('tourney_base') :Args(0) {
    my ($self, $c, $serial) = @_;

    my $table_serial = $c->stash->{tourney}->get_table_serial($c->user->serial);
    $c->stash->{table} = $c->model("PokerNetwork::Pokertables")->find($table_serial);

    $c->stash->{template} = 'tables/view';
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

1;
