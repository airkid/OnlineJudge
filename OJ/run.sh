ulimit -c 0 -l 0 -t $1 -v $2
shift 2
$*
