#!/bin/bash

_wc() { wc -l $1 > $2 ; }
_cp() { cp $1 $2 ; }
_split() {
    cp $1 $2
    echo "111" >> $2
    cp $1 $3
    echo "222" >> $3
}
_join() {
    cat $1 > $3
    cat $2 >> $3
}

export -f _wc
export -f _cp
export -f _split
export -f _join
