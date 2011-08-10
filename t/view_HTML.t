use strict;
use warnings;
use Test::More;

BEGIN { 
  use_ok 'Room' or die;
  use_ok 'Room::View::HTML' or die;
}

ok my $view = Room->view('HTML'), 'Get HTML view object.';

ok $view->template_exists('pages', 'about_us'), 'template_exists() should return true for "about_us" template.';
ok ! $view->template_exists('pages', 'indexNOTEXISTS'), 'template_exists() should return false for "indexNOTEXISTS" template.';
ok ! $view->template_exists('pages', '../../../room_sample.conf'), 'template_exists() should return false for "../../../room_sample.conf" file.';
ok ! $view->template_exists('pages', '../index'), 'template_exists() should return false for "../index" file.';

done_testing();
