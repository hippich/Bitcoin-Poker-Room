package Room::Controller::User::Deposit;
use Moose;
use namespace::autoclean;

BEGIN {extends 'Catalyst::Controller'; }

=head1 NAME

Room::Controller::User::Deposit - Catalyst Controller

=head1 DESCRIPTION

Catalyst Controller.

=head1 METHODS

=cut


=head2 index

=cut

sub index :Path :Args(0) {
    my ( $self, $c ) = @_;

    $c->response->body('Matched Room::Controller::User::Deposit in User::Deposit.');
}

sub bitcoin :Local {
  my ( $self, $c ) = @_;
  $c->forward('deposit_bitcoin_refresh');
  $c->stash->{bitcoin_address} = $c->user->bitcoin_address;
  $c->stash->{bitcoins_sent} = $c->user->bitcoins_received || 0;
}



sub deposit_bitcoin_refresh :Private {
  my ( $self, $c ) = @_;

  if ($c->user->bitcoin_checked + 300 > time()) {
      $c->log->debug('Last time balance checked - '. $c->user->bitcoin_checked .'. Waiting '. ($c->user->bitcoin_checked + 300 - time()) .' seconds.' );
      return 1;
  }

  $c->log->debug('Time to check balance.' );

  $c->user->bitcoin_checked(time());
  $c->user->update();

  if (! $c->user->bitcoin_address) {
    $c->user->bitcoin_address(
      $c->model("BitcoinServer")->get_new_address()
    );
    
    $c->user->update();
  }

  my $bitcoins_new_balance = $c->model("BitcoinServer")->get_received_by_address( $c->user->bitcoin_address );

  if ($bitcoins_new_balance && $bitcoins_new_balance > $c->user->bitcoins_received) {
    my $diff = $bitcoins_new_balance - $c->user->bitcoins_received;
    $c->user->bitcoins_received(
      $c->user->bitcoins_received + $diff
    );

    $c->user->update;

    $c->user->deposits->create({
      currency_serial => 1,
      amount => $diff,
      processed => 1,
      info => $c->user->bitcoin_address,
      created_at => DateTime->now,
      processed_at => DateTime->now,
    });

    my $balance = $c->user->balances->find_or_create({ currency_serial => 1 });
    $balance->amount( $balance->amount + $diff );
    $balance->update();
  }
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
