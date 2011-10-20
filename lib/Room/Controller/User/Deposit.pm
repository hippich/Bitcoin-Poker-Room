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

    my $payments = $c->config->{payments};

    for my $name (keys %{$payments}) {
        my $serial = $payments->{$name}->{currency_serial};

        push @{$c->stash->{payments}}, {
            deposit => $c->user->bitcoin_balance($serial),
            balance => $c->user->balance($serial),
            currency => $c->model('PokerNetwork::Currencies')->find({ serial => $serial}),
            rate => $payments->{$name}->{rate},
        };
    }
}



sub deposit_bitcoin_refresh :Private {
    my ( $self, $c ) = @_;

    if ($c->user->bitcoin_checked + 1 > time()) {
        $c->log->debug('Last time balance checked - '. $c->user->bitcoin_checked .'. Waiting '. ($c->user->bitcoin_checked + 300 - time()) .' seconds.' );
        return 1;
    }

    $c->log->debug('Time to check balance.' );

    $c->user->bitcoin_checked(time());
    $c->user->update();

    my $payments = $c->config->{payments};

    for my $name (keys %{$payments}) {
        my $payment = $payments->{$name};
        
        my $new_balance_cb = sub {
            my $address = shift->address;
            my $model = $payment->{model};
            my $minconf = $payment->{minconf};

            # To force int value type for JSON-RPC
            $minconf += 0;

            my $received = $c->model($model)->get_received_by_address( $address, $minconf );
            $received ||= 0;

            return $received * $payment->{rate};
        };

        my $new_address_cb = sub {
            return $c->model($payment->{model})->get_new_address;
        };

        $c->user->deposit_bitcoin($payment->{currency_serial}, $new_balance_cb, $new_address_cb);
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
