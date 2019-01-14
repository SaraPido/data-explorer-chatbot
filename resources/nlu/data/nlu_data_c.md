## intent:find_el_by_word
- find [customer](el) [Nicola](word)
- find [employee](el) [Mark](word)
- find [employee](el) [Luigi](word)
- find [product](el) [Ferrari](word)
- find [employee](el) [George](word)

## intent:find_el_by_num
- find [customer](el) [greater than](op) [23](num)
- find [employee](el) [540](num)
- find [office](el) [lower than](op) [2340](num)
- find [product](el) [equal to](op) [927](num)
- find [employee](el) [6784](num)

## intent:find_el_by_rel_word
- find [customer](el) with [product](rel_el) [Ferrari](word)
- find [office](el) with [office](rel_el) [Motorola](word)
- find [employee](el) with [product line](rel_el) [Example](word)
- find [employee](el) with [office](rel_el) [Mario](word)

## intent:find_el_by_rel_num
- find [office](el) with [product](rel_el) [greater than](op) [23](num)
- find [employee](el) with [title](rel_el) [11](num)
- find [customer](el) with [salary](rel_el) [equal to](op) [746](num)
- find [employee](el) with [product](rel_el) [lower than](op) [23421](num)

## intent:view_rel_el
- view [payment](rel_el)
- view [product](rel_el)
- view [employee](rel_el)
- view [product line](rel_el)

## lookup:el
- customer
- employee
- office
- product

## lookup:rel_el
- customer
- employee
- office
- product
- product line
- payment
- order

## lookup:word
- Nicola
- Giorgio
- Vittorio
- Albert
- Florian
- Car
- Ferrari
- Mario

## intent:view_all_rel
- show me the relations
- its relations
- view relations
- relations
## intent:select_el_by_pos
- select [first](pos) row
- [second](pos) row
- select [third](pos)
- select [fourth](pos)
- select the [2nd](pos) row
- select the [fifth](pos)
## intent:show_context
- show the context
- the context
- context
- view context
## intent:go_back_to_context_pos
- go back to [first](pos)
- go back to [second](pos)
- go back
## synonym:1st
- first
- 1
## synonym:2nd
- second
- 2
## synonym:3rd
- third
- 3
## synonym:4th
- fourth
- 4
## synonym:5th
- fifth
- 5
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