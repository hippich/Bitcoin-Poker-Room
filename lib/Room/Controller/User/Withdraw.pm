package Room::Controller::User::Withdraw;
use Moose;
use namespace::autoclean;

BEGIN {extends 'Catalyst::Controller::HTML::FormFu'; }

=head1 NAME

Room::Controller::User::Withdraw - Catalyst Controller

=head1 DESCRIPTION

Catalyst Controller.

=head1 METHODS

=cut


=head2 index

=cut

sub base :Chained :PathPart('user/withdraw') :CaptureArgs(0) {
    my ( $self, $c ) = @_;
}

sub index :Chained :PathPart('') :Args(0) {
}

sub withdraw_base :Chained('base') :PathPart('') :CaptureArgs(1) {
    my ($self, $c, $currency_name) = @_;
    my $currency_serial = $c->config->{payments}->{$currency_name}->{currency_serial};
    $c->page_not_found unless $currency_serial;

    $c->stash->{payment_model} = $c->model( $c->config->{payments}->{$currency_name}->{model} );
    $c->stash->{payment} = $c->config->{payments}->{$currency_name};

    $c->stash->{currency} = $c->model('PokerNetwork::Currencies')->find({
        serial => $currency_serial
    });
    $c->page_not_found unless $c->stash->{currency};
}

sub withdraw :Chained('withdraw_base') :PathPart('') :Args(0) :FormConfig {
    my ($self, $c) = @_;
    my $form = $c->stash->{form};

    if ($form->submitted_and_valid) {

        if (! $c->user->check_password( $form->params->{password} )) {
          $form->get_field("password")->get_constraint({ type => "Callback" })->force_errors(1);
          $form->process();
          return;
        }

        my $address = $form->params->{bitcoin_address};
        my $amount = $form->params->{amount};
        my $adj_amount = $amount * 100 * $c->stash->{payment}->{rate};

        my $withdraw_cb = sub {
            my ($withdrawal) = @_;
            my $result = $c->stash->{payment_model}->send_to_address($address, $amount);
            my $error = $c->stash->{payment_model}->api->error;
            $withdrawal->dest($address);

            if (! $c->stash->{payment_model}->api->error) {
              push @{$c->flash->{messages}}, "Bitcoins sent.";
            }
            else {
              push @{$c->flash->{errors}}, "We received your withdrawal request and will process it ASAP. If you will not receive bitcoins in 24 hours, please contact us.";
            }

            return ($result, $error);
        };

        $c->user->withdraw_bitcoin(
            $c->stash->{currency}->serial,
            $adj_amount,
            $withdraw_cb
        );

        $c->res->redirect(
          $c->uri_for('/user')
        );
    }
}


=head1 AUTHOR

pavel,,,

=head1 LICENSE

This library is free software. You can redistribute it and/or modify
it under the same terms as Perl itself.

=cut

__PACKAGE__->meta->make_immutable;

1;
