use strict;
use warnings;
use Data::Dumper qw(Dumper);

my $tmax = 3;	#max number of frames before considering a new pulse
my $dmax = 5;	#max distance in pixels before considering a new pulse

my $maxc = 500; #max contours/frame to cycle back through. Usually not used, but could be an issue when many pulses are on a frame at once.


#*********** subroutine to calculate Euclidean distance between pulses
sub distance($$$$) {
	my($x1, $y1, $x2, $y2) = @_;
	return sqrt(($x2 - $x1) ** 2 + ($y2 - $y1) ** 2);
}

my $filename = $ARGV[0];
open(my $fh, '<:encoding(UTF-8)', $filename)
  or die "Could not open file '$filename' $!";
 
my $counter = 0;
my $curdist;
my $cdist;
my @contour;
my @pulse;
my $pulseno = 1;
my $pulseofn = 0;
my $closestcon = 10000; #Starting with absurdly high value so first d is always lower


print "frame,x,y,pulse\n";
#Full data matrix into 2d array
while (my $row = <$fh>) {
  chomp $row;
  my @datapts = split /\,/, $row;
  if($counter == 0){
	#skipping header;
  }else{
	my (@row) = split /\,/, $row;
	push (@{contour}, \@row);

  }
  $counter++;
}

for(my $i=0; $i < $counter-1 ; $i++) {
        #Loop back 2 time points
	for(my $tp=1; $tp < $maxc; $tp++) {
		#Check if reached all the way back to Contour 0
		if ($tp >= $i){
			if($closestcon > 999){	#First contour which gets placed into a pulse 0 automatically
				$contour[$i][3] = $pulseno;
				for(my $d=0; $d < 3; $d++){
					print "$contour[$i][$d],";
				}
			}else{
				#hit 0 but not first time through
				$cdist = distance($contour[$i][1],$contour[$i][2], $contour[$i-$tp][1],$contour[$i-$tp][2]);
				if ($cdist < $dmax){	#its the same pulse
					$contour[$i][3] = $contour[$i-$tp][3];
					for(my $d=0; $d < 3; $d++){
						print "$contour[$i][$d],";
					}
					$closestcon = 600;
					print "$contour[$i][3]\n";
					last;
				}else{	#it's a new pulse
					$pulseno++;
					$contour[$i][3] = $pulseno;
					for(my $d=0; $d < 3; $d++){
						print "$contour[$i][$d],";
					}
				$closestcon = 600;
				print "$contour[$i][3]\n";
				last;
				}
			}
			print "$contour[$i][3]\n";
			$closestcon = $dmax;
			last;
		}
		#Now check distance of current contour to $tp previous contour 
		$cdist = distance($contour[$i][1],$contour[$i][2], $contour[$i-$tp][1],$contour[$i-$tp][2]);
		if ($cdist < $dmax){ #it's within the distance to be the same pulse
			$pulseofn = $contour[$i-$tp][3];
			$contour[$i][3] = $pulseofn;
			for(my $d=0; $d < 3; $d++){
				print "$contour[$i][$d],";
			}
			print "$contour[$i][3]\n";
			$closestcon = $dmax;
			last;
		}
		if ($cdist < $closestcon){
			$closestcon = $cdist;
			$pulseofn = $contour[$i-$tp][3];
		}
#Uncomment to Debug
#		print "i".$i.")  $tp Contours ago: ".$contour[$i-$tp][0].",".$contour[$i-$tp][1]." Current frame: $contour[$i][0],$contour[$i][1]\t";
#		print "Contour distance: ".$cdist."\n";
		if ($contour[$i][0] - $contour[$i-$tp][0] > $tmax){
#			print "More than $tmax frames ago. Closest dist is $closestcon\n\n";
			if ($cdist < $dmax){	#its the same pulse
				$contour[$i][3] = $pulseofn;
				for(my $d=0; $d < 3; $d++){
					print "$contour[$i][$d],";
				}
				$closestcon = 600;
				print "$contour[$i][3]\n";
				last;
			}else{	#it's a new pulse
				$pulseno++;
				$contour[$i][3] = $pulseno;
				for(my $d=0; $d < 3; $d++){
					print "$contour[$i][$d],";
				}
				$closestcon = 600;
				print "$contour[$i][3]\n";
				last;
			}
		}
	} 
} 

#print Dumper \@contour;
#print $contour[100][0]."\n";
#print @contour;
