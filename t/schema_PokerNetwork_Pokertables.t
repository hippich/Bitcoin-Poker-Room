use strict;
use warnings;
use Test::More;
use Test::DBIx::Class;

fixtures_ok "basic", "Fixtures loaded.";

ok my $tables = Pokertables, 'Pokertables ResultSet loaded.';

my $t = $tables->next;
$t = $tables->next;

my $search_result = $tables->search({ small_blind => 10000 });
ok $search_result->count >= 1, 'One table found via advanced_search';
my $table = $search_result->next;
ok $table->big_blind == 20000, 'Big blind should be equal 200';

$search_result = $tables->search({ small_blind => { '>' => 100 } });
ok $search_result->count >= 1, 'One table found via advanced_search with small_blind > 100';

$search_result = $tables->search({ seats => { '>=' => 2, '<=' => 10 } });
ok $search_result->count >= 1, 'One table found via advanced_search with 2 <= seats <= 10';

$search_result = $tables->search({ seats => { '>=' => 2, '<=' => 3 } });
ok $search_result->count == 0, 'Zero tables should be found via advanced_search with 2 <= seats <= 3';

done_testing();


