#!/usr/bin/perl
use strict;



my %polarityRelSys=();
my %polarityRelGold=();
my %entityDocs=();
my %entityDocsSys=();
my $avgACC=0;
my $samplesEntities=0;


open (FICHIN,$ARGV[0]) or die("not found $ARGV[0]");
my $line=<FICHIN>;
while (my $line=<FICHIN>){
  if ($line=~/\n/){
    chop ($line);
  }
  $line=~s/\"//g;
  if ($line=~/\w/){
    	(my $entity,my $id,my $polarity)=split(/\t/,$line);
	 $polarityRelGold{$entity}{$id}=$polarity;
	 $entityDocs{$entity}.="|$id"; 
  }	
}
close (FICHIN);

open (FICHIN,$ARGV[1]) or die("not found $ARGV[1]");
$line=<FICHIN>;
while (my $line=<FICHIN>){
  if ($line=~/\n/){
    chop ($line);
  }
  $line=~s/\"//g;
  if ($line=~/\w/){
    	(my $entity,my $id,my $polarity)=split(/\t/,$line);
	 $polarityRelSys{$entity}{$id}=$polarity;
  }	
}
close (FICHIN);


print "system\tentity\taccuracy\n";
foreach my $entity (keys %entityDocs){
  my $samples=0;
  my $ACC=0;
  foreach my $doc (split(/\|/,$entityDocs{$entity})){
    if ($doc ne ""){
      $samples++;
      if ($polarityRelSys{$entity}{$doc} eq $polarityRelGold{$entity}{$doc}){
	$ACC++;
      }
    }
  }	
  $ACC=$ACC/$samples;
  print "$ARGV[1]\t$entity\t$ACC\n"; 
  $samplesEntities++;
  $avgACC+=$ACC;
}
print "$ARGV[1]\taverage\t".($avgACC/$samplesEntities)."\n";

