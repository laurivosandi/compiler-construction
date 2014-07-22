-- Sum numbers 1 .. n
DEF MAIN:nat == sum(10, 0)
DEF sum(x:nat, y:nat):nat == IF eq(x, 0) THEN y ELSE sum(sub(x,1), add(y,x)) FI
