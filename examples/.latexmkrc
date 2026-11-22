# Keep the examples independently compilable from this directory.
$ENV{'TEXINPUTS'} = '../tex:' . ($ENV{'TEXINPUTS'} // '');
