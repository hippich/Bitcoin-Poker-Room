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


sub auto :Private {
  my ($self, $c) = @_;

  if (! $c->user) {
    $c->response->redirect(
      $c->uri_for(
        '/user/login',
        '',
        {
          'destination' => $c->uri_for( $c->action )
        }
      )
    );
  }

  1;
}


=head2 index

=cut

sub index :Path :Args(0) {
    my ( $self, $c ) = @_;

    $c->stash->{tables} = $c->model("PokerNetwork::Pokertables")->search({
                                currency_serial => 1,
                                tourney_serial => 0,
                          },
                          {
                                order_by => {
                                  -desc => 'players',
                                },
                          });

}

sub notify :Local :Args(0) {
  my ( $self, $c ) = @_;

  my $players = $c->model("PokerNetwork::Pokertables")->get_column('players');
  my $total = $players->sum;

  if ($total > 0) {
    my $nt = Net::Twitter::Lite->new(
      consumer_key => $c->config->{twitter_consumer_key},
      consumer_secret => $c->config->{twitter_consumer_secret},
      access_token => $c->config->{twitter_access_token},
      access_token_secret => $c->config->{twitter_access_token_secret}
    );

    my $result = eval { $nt->update($total . ' player(s) sits right now at poker tables at #bitcoin #poker room http://bit.ly/dF1K8h.') }; 
  }

  $c->response->body('Done');
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

