package Room::Model::BitcoinServer;

use JSON::RPC::Client;
use Moose;
use MooseX::Types::Moose qw/ArrayRef Str ClassName Undef/;
extends 'Catalyst::Model';

has jsonrpc_client => (is => 'rw');
has jsonrpc_host => (is => 'rw', isa => Str);
has jsonrpc_uri => (is => 'rw', isa => Str);
has jsonrpc_user => (is => 'rw', isa => Str);
has jsonrpc_password => (is => 'rw', isa => Str);


sub BUILD {
  my $self = shift;

  $self->jsonrpc_client( new JSON::RPC::Client );
  $self->jsonrpc_client->ua->credentials(
    $self->jsonrpc_host,
    'jsonrpc',
    $self->jsonrpc_user => $self->jsonrpc_password,
  );
}


sub get_received_by_address {
  my ($self, $address) = @_;

  my $res = $self->__send_json_request({
      method => 'getreceivedbyaddress',
      params => [$address],
  });

  return $res->{content}->{result};
}


sub send_to_address {
  my ($self, $address, $amount) = @_;

  # This is required to force $amount to be json-coded as real type,
  # not string, in following JSON-RPC request
  $amount += 0;
  
  my $res = $self->__send_json_request({
      method => 'sendtoaddress',
      params => [$address, $amount],
  });
  
  return $res;
}


sub get_new_address {
  my $self = shift;

  my $res = $self->__send_json_request({
      method => 'getnewaddress',
      params => [],
  });

  return $res->{content}->{result};
}


sub __send_json_request {
  my ($self, $obj) = @_;
 
  return $self->jsonrpc_client->call(
    $self->jsonrpc_uri, $obj
  );
}

1;