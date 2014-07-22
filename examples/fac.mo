-- syntax correct, result 3628800
DEF fac(x:nat):nat == IF eq(x,0) THEN 1 ELSE mul(x, fac(sub(x,1))) FI
DEF MAIN:nat == fac(10)
