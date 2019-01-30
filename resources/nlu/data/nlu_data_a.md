## intent:find_el_by_attribute
- find [employee](el) [Georgi](word) [has salary](attr) [12345](num) and [birth date](attr) [2 November 2001](date)
- find [employee](el) [Mark](word) [has salary](attr) [>](num_op) [12345](num)
- find [employees](el) that [was born](attr) [after](date_op) [2 November 2001](date)
- find [male](gender) [employee](el) [Georgi](word) with [salary](attr) [12345](num) and [birth date](attr) [2 November 2001](date)


## lookup:num_op
- >
- <

## lookup:date_op
- before
- after
- on

## lookup:gender
- male
- female

## synonym:with salary
- have salary
- has salary

## synonym:was born
- with birth date
- were born

## regex:num
- [1-9][0-9]*

## synonym:>
- greater than
- greater
- bigger
## synonym:<
- lower than
- lower
- smaller
## synonym:=
- equal to
- equal
- exactly