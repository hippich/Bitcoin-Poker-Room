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
    my $page = $c->req->params->{page} || 1;

    @{$c->stash->{servers}} = $c->model('PokerNetwork::Resthost')->all;
    @{$c->stash->{currencies}} = $c->model('PokerNetwork::Currencies')->all;

    $c->stash->{small_blinds} = $c->model("PokerNetwork::Pokertables")->search(
        { small_blind => { '>', 0 } }, { columns => [ qw/ small_blind / ], distinct => 1 }
    );
    
    $c->stash->{big_blinds} = $c->model("PokerNetwork::Pokertables")->search(
        { big_blind => { '>', 0 } }, { columns => [ qw/ big_blind / ], distinct => 1, order_by => { -desc => 'big_blind' } }
    );
    
    my $params = $c->req->params;
    my $params_count = scalar( keys %{$params} );
    my $filter = {};

    if ($params_count > 0) {
        # Show filtered tables

        # Add server filter 
        $filter->{resthost_serial} = $params->{resthost_serial} unless !$params->{resthost_serial};

        # Add currency filter 
        $filter->{currency_serial} = $params->{currency_serial} unless !$params->{currency_serial};

        # Add variant filter 
        $filter->{variant} = $params->{variant} unless !$params->{variant};

        # Add limit type filter 
        $filter->{limit_type} = $params->{limit_type} unless !$params->{limit_type};

        # Add blinds range filter 
        my $min_blinds = $params->{blinds_range_min} || 0;
        my $max_blinds = $params->{blinds_range_max} || 0;
        $filter->{small_blind} = { '>=' => $min_blinds } unless $min_blinds == 0; 
        $filter->{big_blind} = { '<=' => $max_blinds } unless $max_blinds == 0; 

        # Add min/max seats filter 
        my $seats_min = $params->{seats_range_input_min} || 2;
        my $seats_max = $params->{seats_range_input_max} || 10;

        $filter->{seats} = {
            '>=' => $seats_min,
            '<=' => $seats_max,
        };

        # Add min/max players filter 
        my $players_min = $params->{players_range_input_min} || 0;
        my $players_max = $params->{players_range_input_max} || 10;

        $filter->{players} = {
            '>=' => $players_min,
            '<=' => $players_max,
        };
    }

    $filter->{tourney_serial} = 0;

    $c->stash->{ajax} = $c->req->params->{ajax};
    $c->stash->{page} = $page;

    $c->stash->{tables} = $c->model("PokerNetwork::Pokertables")->advanced_search(
        $filter,
        {
            rows => 15,
            page => $page,
            order_by => {
                -desc => 'players',
            }
        }
    );
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

    $c->stash->{url} = $c->get_rest_url('table-' . $game_id, $c->stash->{table}->host);
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

