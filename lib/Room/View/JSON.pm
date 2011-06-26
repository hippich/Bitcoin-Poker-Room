package Room::View::JSON;
use base qw( Catalyst::View::JSON );

use JSON ();

sub encode_json {
    my ($self, $c, $data) = @_;
    my $encoder = JSON->new->ascii->pretty->allow_blessed->convert_blessed;
    $encoder->encode($data);
}

1;
