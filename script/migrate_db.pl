#!/usr/bin/perl 
#===============================================================================
#
#         FILE:  migrate_db.pl
#
#        USAGE:  ./migrate_db.pl  
#
#  DESCRIPTION:  Migrates DB 
#
#      OPTIONS:  --from, --to 
#              
# REQUIREMENTS:  ---
#         BUGS:  ---
#        NOTES:  ---
#       AUTHOR:  Pavel A. Karoukin
#      COMPANY:  Yep Corp Limited
#      VERSION:  1.0
#      CREATED:  10/25/2011 06:58:21 PM
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
use Getopt::Long;

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
    }
);

my $version = Room::Schema::PokerNetwork->VERSION;
my $current_version = $dh->database_version;

if ($version > $current_version) {
    $dh->upgrade;
}
else {
    $dh->downgrade;
}
 
say "done";