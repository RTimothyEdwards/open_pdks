#!/usr/bin/env perl
#
# This is a simple script that generates Makefile "TOOLS" flags. 
# 
# This is not used at all during part of any build or CI. It's a convenience
# tool for open_pdks contributors.
#
open(FH, '<', "./tools.txt") or die $!;
while (<FH>) {
    chomp $_;
    my $capitalized = uc $_;
    my $disable_macro = "$capitalized\_DISABLED";
    print <<"HD"
# $disable_macro = 0 | 1
$disable_macro = \@$disable_macro\@
ifneq (\${$disable_macro}, 1)
	TOOLS += $_
endif

HD
}