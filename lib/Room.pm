package Room;
use Moose;
use namespace::autoclean;

use Catalyst::Runtime 5.80;
use CatalystX::RoleApplicator;

# Set flags and add plugins for the application
#
#         -Debug: activates the debug mode for very useful log messages
#   ConfigLoader: will load the configuration from a Config::General file in the
#                 application's home directory
# Static::Simple: will serve static files from the application's root
#                 directory

use Catalyst qw/
    StackTrace
    ConfigLoader
    Static::Simple
    Session
    Session::Store::File
    Session::State::Cookie
    Authentication
    RequireSSL
    Email
    Log::Handler
    LogWarnings
/;

extends 'Catalyst';

our $VERSION = '0.01';
$VERSION = eval $VERSION;

# Configure the application.
#
# Note that settings in room.conf (or other external
# configuration file that you set up manually) take precedence
# over this when using ConfigLoader. Thus configuration
# details given here can function as a default configuration,
# with an external configuration file acting as an override for
# local deployment.

__PACKAGE__->apply_request_class_roles(qw/
          Catalyst::TraitFor::Request::BrowserDetect
/);

__PACKAGE__->config(
    name => 'Room',
    
    # Disable deprecated behavior needed by old applications
    disable_component_resolution_regex_fallback => 1,
    
    static => {
        ignore_extensions => [ qw/asp php/ ],
    },

    'Controller::HTML::FormFu' => {
      constructor => {
          tt_args => {
              ENCODING => 'UTF-8',
              INCLUDE_PATH => [
                __PACKAGE__->path_to( 'root', 'formfu' ),
              ],
          },
          render_method => "tt",
      },

      model_stash => {
          schema => 'PokerNetwork',
      },
    },

    'View::TT' => {
        ENCODING => 'UTF-8',
    },

    'Plugin::Authentication' => {
        default => {
            credential => {
                user_model => 'PokerNetwork::Users',
                class => 'Password',
                password_type => 'self_check',
            },
            store => {
                class => 'DBIx::Class',
                user_model => 'PokerNetwork::Users',
            },
       },
    },
);

__PACKAGE__->config->{email} = [qw/Sendmail/];

# Hide config variables from debug screen
sub dump_these {
    my $c = shift;
    my @variables = $c->next::method(@_);
    return grep { $_->[0] ne 'Config' } @variables;
}

# Start the application
__PACKAGE__->setup();


=head1 NAME

Room - Catalyst based application

=head1 SYNOPSIS

    script/room_server.pl

=head1 DESCRIPTION

[enter your description here]

=head1 SEE ALSO

L<Room::Controller::Root>, L<Catalyst>

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


1;
