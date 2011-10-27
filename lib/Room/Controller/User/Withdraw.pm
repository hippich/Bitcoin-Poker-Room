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

    my $currency = $c->model("PokerNetwork::Currencies")->find({ id => $currency_name });
    $c->page_not_found unless $currency;

    $c->stash->{currency} = $currency;
}

sub withdraw :Chained('withdraw_base') :PathPart('') :Args(0) :FormConfig {
    my ($self, $c) = @_;
    my $form = $c->stash->{form};
    my $balance = $c->user->balance( $c->stash->{currency}->serial );
    $c->stash->{page_title} = 'Withdraw '. $c->stash->{currency}->name;

    $c->stash->{balance} = $balance;

    if ($form->submitted_and_valid) {

        if (! $c->user->check_password( $form->params->{password} )) {
          $form->get_field("password")->get_constraint({ type => "Callback" })->force_errors(1);
          $form->process();
          return;
        }

        my $address = $form->params->{bitcoin_address};
        my $amount = $form->params->{amount};
        my $model = $c->model( $c->stash->{currency}->class ); 

        my $adj_amount = $amount * $c->stash->{currency}->rate * 100;

        if ($balance->amount < $amount || $amount < 0.01 || int($amount * 100) / 100 < $amount)  {
          $form->get_field("amount")->get_constraint({ type => "Callback" })->force_errors(1);
          $form->process();
          return;
        }

        my $withdraw_cb = sub {
            my ($withdrawal) = @_;
            my $result = $model->send_to_address($address, $amount);
            my $error = $model->api->error;
            $withdrawal->dest($address);

            if ( $model->api->error ) {
              push @{$c->flash->{errors}}, "We received your withdrawal request and will process it ASAP. If you will not receive bitcoins in 24 hours, please contact us.";
            }
            else {
              push @{$c->flash->{messages}}, "Bitcoins sent.";
            }

            return ($result, $error);
        };

        $c->user->withdraw_bitcoin(
            $c->stash->{currency},
            $amount,
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
