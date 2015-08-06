#!/usr/bin/perl
use strict;



my %priorityRelSys=();
my %priorityRelGold=();
my %entityDocs=();
my $avgF=0;
my $samplesEntities=0;

open (FICHIN,$ARGV[0]) or die("not found $ARGV[0]");
my $line=<FICHIN>;
while (my $line=<FICHIN>){
  if ($line=~/\n/){
    chop ($line);
  } 
  $line=~s/\"//g;
  if ($line=~/\w/){
    (my $entity,my $id,my $priority)=split(/\t/,$line);
    if ($priority eq "RELATED"){
      $priorityRelGold{$entity}{$id}=1;
      $entityDocs{$entity}.="|$id"; 
    }
    if ($priority eq "UNRELATED"){
      $priorityRelGold{$entity}{$id}=0;
      $entityDocs{$entity}.="|$id"; 
    }
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
    (my $entity,my $id,my $priority)=split(/\t/,$line);
    if ($priority eq "RELATED"){
      $priorityRelSys{$entity}{$id}=1;
    }
    if ($priority eq "UNRELATED"){
      $priorityRelSys{$entity}{$id}=0;
    }
  }	
}
close (FICHIN);



foreach my $entity (keys %entityDocs){
  my $samplesS=0;
  my $samplesR=0;
  my $R=0;
  my $S=0;
  foreach my $doc1 (split(/\|/,$entityDocs{$entity})){
  if ($doc1 ne ""){
    my $Rd=0;
    my $sampRd=0;
    my $Sd=0;
    my $sampSd=0;
    foreach my $doc2 (split(/\|/,$entityDocs{$entity})){
      if (($doc1 ne $doc2)&&($doc2 ne "")){
	if ($priorityRelGold{$entity}{$doc1}>$priorityRelGold{$entity}{$doc2}){
	  $sampSd++;
	 
	  if ((exists $priorityRelSys{$entity}{$doc1})&&
	      (exists $priorityRelSys{$entity}{$doc2})&&	
	      ($priorityRelSys{$entity}{$doc1}>$priorityRelSys{$entity}{$doc2})){
	    $Sd++;
	  }
	}
	if ($priorityRelGold{$entity}{$doc1}<$priorityRelGold{$entity}{$doc2}){
	  $sampSd++;
	  if ((exists $priorityRelSys{$entity}{$doc1})&&
	      (exists $priorityRelSys{$entity}{$doc2})&&				
	      ($priorityRelSys{$entity}{$doc1}<$priorityRelSys{$entity}{$doc2})){
	    $Sd++;
	  }
	}
	
	if ((exists $priorityRelSys{$entity}{$doc1})&&
	    (exists $priorityRelSys{$entity}{$doc2})&&	
	    ($priorityRelSys{$entity}{$doc1}>$priorityRelSys{$entity}{$doc2})){
	  $sampRd++;
	  if ($priorityRelGold{$entity}{$doc1}>$priorityRelGold{$entity}{$doc2}){
	    $Rd++;
	  }
	}
	if ((exists $priorityRelSys{$entity}{$doc1})&&
	    (exists $priorityRelSys{$entity}{$doc2})&&	
	    ($priorityRelSys{$entity}{$doc1}<$priorityRelSys{$entity}{$doc2})){	
	  $sampRd++;
	  if ($priorityRelGold{$entity}{$doc1}<$priorityRelGold{$entity}{$doc2}){
	    $Rd++;
	  }
	}
      }
    }
    $samplesS++;
    if ($sampSd>0){
      $S+=$Sd/$sampSd;
    }else{
      $S+=1;
    }
    $samplesR++;
    if ($sampRd>0){
      $R+=$Rd/$sampRd;
    }else{
      $R+=1;
    }
  }
}
  $R=$R/$samplesR;
  $S=$S/$samplesS;
  my $F=0;
  if (($R>0)&&($S>0)){
    $F=2/(1/$R+1/$S);
  }
  print "entity\t$entity\tReliability=$R\tSensitivity=$S\tF measure=$F\n"; 
  $samplesEntities++;
  $avgF+=$F;
}

print "Average F measure=".($avgF/$samplesEntities)."\n";
