#!/usr/bin/perl 
#===============================================================================
#
#         FILE:  dhinit.pl
#
#        USAGE:  ./script/dhinit.pl  
#
#  DESCRIPTION: Initialize DeployHandler module. Required to run only once.
#
#      OPTIONS:  ---
# REQUIREMENTS:  ---
#         BUGS:  ---
#        NOTES:  ---
#       AUTHOR:  Pavel A. Karoukin, pavel@yepcorp.com
#      COMPANY:  Yep Corp Limited
#      VERSION:  1.0
#      CREATED:  10/24/2011 07:53:39 AM
#     REVISION:  ---
#===============================================================================

use strict;
use warnings;
use v5.10;

BEGIN {
    use FindBin qw($Bin);
    use lib $Bin . "/../lib";
}

use aliased 'DBIx::Class::DeploymentHandler' => 'DH';
use Room::Schema::PokerNetwork;

my $s = Room::Schema::PokerNetwork->connect({
        dsn => 'dbi:mysql:pythonpokernetwork',
        user => 'root',
        password => '',
        AutoCommit => 1,
});

my $dh = DH->new(
    {
        schema              => $s,
        script_directory    => "$FindBin::Bin/../sql",
        databases           => 'MySQL',
        sql_translator_args => { add_drop_table => 0 },
        force_overwrite     => 1,
    }
);

say "Adding version table to DB.";

$dh->prepare_version_storage_install;
$dh->install_version_storage; 
$dh->add_database_version({ version => $s->VERSION });

say "Generating v1 schema.";

$dh->prepare_install;

say "Done.";
