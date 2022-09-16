function executionTime () {
  (test -f $1 && echo "processing ${1}") || (echo "file ${1} does not exist")
  cat $1 | 
  grep -E "^ExecutionTime" | 
  awk 'NR>1{print $3-old; old=$3}'
}
