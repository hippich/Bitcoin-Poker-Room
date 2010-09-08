package Room::Controller::User;
use Moose;
use namespace::autoclean;
use DateTime;
use Data::Dumper;

BEGIN {extends 'Catalyst::Controller::HTML::FormFu'; }

=head1 NAME

Room::Controller::User - Catalyst Controller

=head1 DESCRIPTION

Catalyst Controller.

=head1 METHODS

=cut

sub auto :Private {
  my ($self, $c) = @_;

  if (!$c->user && $c->action->private_path !~ /user\/(login|register)/) {
    $c->res->redirect(
      $c->uri_for('/user/login', '', {'destination' => $c->action,})
    );

    return;
  }

  if ($c->user) {
    $c->forward('deposit_bitcoin_refresh');
  }

  1;
}


=head2 index

=cut

sub index :Path :Args(0) {
    my ( $self, $c ) = @_;

}

sub login :Local :Args(0) :FormConfig {
    my ( $self, $c ) = @_;

    if ($c->user) {
      $c->response->redirect(
        $c->uri_for('/user')
      );
    }
    
    my $form = $c->stash->{form};

    if ($form->submitted_and_valid) {
    
      my $user = $c->authenticate({
                    name => $form->params->{name},
                    password => $form->params->{password},
                 });

      if ($user) {
        if ($c->req->param('destination')) {
          $c->res->redirect(
            $c->req->param('destination')
          );
        }
        
        $c->res->redirect(
          $c->uri_for('/user')
        );
      }
      else {
        push @{$c->stash->{errors}}, "Invalid Username or Password.";
      }
    }
}


sub logout :Local :Args(0) {
  my ( $self, $c ) = @_;

  $c->logout;
  
  $c->model("PokerNetwork")->logout(
    $c->session->{pokernetwork_auth}
  );
  $c->session->{pokernetwork_auth} = undef;
  
  push @{$c->flash->{messages}}, "Logged out. Good bye.";

  $c->res->redirect(
    $c->uri_for('/')
  );
}


sub register :Local :Args(0) :FormConfig {
  my ( $self, $c ) = @_;

  if ($c->user) {
    $c->response->redirect(
      $c->uri_for('/user')
    );
  }

  my $form = $c->stash->{form};

  if ($form->submitted_and_valid) {

    if (
          $c->model("PokerNetwork::Users")->search({ name => $form->params->{name} })->count > 0
       ) {
      $form->get_field("name")->get_constraint({ type => "Callback" })->force_errors(1);
      $form->process();
      return;
    }

    if (
          $form->params->{email} ne '' &&
          $c->model("PokerNetwork::Users")->search({ email => $form->params->{email} })->count > 0
    ) {
      $form->get_field("email")->get_constraint({ type => "Callback" })->force_errors(1);
      $form->process();
      return;
    }

    my $user = $c->model("PokerNetwork::Users")->new({
      name => $form->params->{name},
      password => $form->params->{password},
      created => DateTime->now,
    });

    if ( $form->params->{email} ) {
      $user->email( $form->params->{email} );
    }
    
    $user->insert();

    push @{$c->flash->{messages}}, "Account successfully created. Please, login with your details.";

    $c->res->redirect(
      $c->uri_for('/user/login')
    );
  }
}



sub deposit_bitcoin :Path('deposit/bitcoin') {
  my ( $self, $c ) = @_;

  if (! $c->user->bitcoin_address) {
    $c->user->bitcoin_address(
      $c->model("BitcoinServer")->get_new_address()
    );
    
    $c->user->update();
  }

  $c->stash->{bitcoin_address} = $c->user->bitcoin_address;
  $c->stash->{bitcoins_sent} = $c->user->bitcoins_received || 0;
}



sub deposit_bitcoin_refresh :Private {
  my ( $self, $c ) = @_;

  my $bitcoins_new_balance = $c->model("BitcoinServer")->get_received_by_address( $c->user->bitcoin_address );

  if ($bitcoins_new_balance > $c->user->bitcoins_received) {
    my $diff = $bitcoins_new_balance - $c->user->bitcoins_received;
    
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

    $c->user->bitcoins_received(
      $bitcoins_new_balance
    );

    $c->user->update;
  }
}



sub withdraw_bitcoin :Path('withdraw/bitcoin') :FormConfig {
  my ($self, $c) = @_;
  my $form = $c->stash->{form};

  if ($form->submitted_and_valid) {
    my $balance = $c->user->balances->search({currency_serial => 1})->first;
    my $address = $form->params->{bitcoin_address};
    my $amount = $form->params->{amount};

    if ($balance->amount < $amount) {
      $form->get_field("amount")->get_constraint({ type => "Callback" })->force_errors(1);
      $form->process();
      return;
    }

    my $result = $c->model("BitcoinServer")->send_to_address($address, $amount);

    # Create withdrawal record for tracking purposes.
    my $withdrawal = $c->user->withdrawals->create({
      currency_serial => 1,
      amount => $amount,
      info => $address . "\n" . Dumper($result),
      created_at => DateTime->now,
    });

    $balance->amount(
      $balance->amount() - $amount
    );
    $balance->update();

    if ($result->{content}->{result} eq 'sent') {
      # Mark as processed if successful
      $withdrawal->processed_at( DateTime->now() );
      $withdrawal->processed(1);
      $withdrawal->update();

      push @{$c->flash->{messages}}, "Bitcoins sent.";

      $c->res->redirect(
        $c->uri_for('/user')
      );
    }
    else {
      push @{$c->stash->{errors}}, "We received your withdrawal request and will process it ASAP. If you will not receive bitcoins in 24 hours, please contact us.";
    }
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

