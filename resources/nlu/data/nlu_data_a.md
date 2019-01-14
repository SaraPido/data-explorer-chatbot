## intent:find_el_by_word
- find [employee](el) [Georgi](word)
- find [department](el) [Sales](word)
- find [department](el) [Finance](word)
- find [employee](el) [Nicola](word)

## intent:find_el_by_num
- find [employee](el) [greater than](op) [23](num)
- find [employee](el) [540](num)
- find [department](el) [lower than](op) [2340](num)
- find [department](el) [equal to](op) [927](num)
- find [employee](el) [6784](num)

## intent:find_el_by_rel_word
- find [employee](el) with [title](rel_el) [Staff](word)
- find [employee](el) with [title](rel_el) [Engineer](word)
- find [employee](el) with [title](rel_el) [Senior Staff](word)
- find [employee](el) with [title](rel_el) [Assistant Engineer](word)

## intent:find_el_by_rel_num
- find [employee](el) with [salary](rel_el) [greater than](op) [23](num)
- find [employee](el) with [salary](rel_el) [11](num)
- find [employee](el) with [salary](rel_el) [equal to](op) [746](num)
- find [employee](el) with [salary](rel_el) [lower than](op) [23421](num)

## intent:view_rel_el
- view [employee](rel_el)
- view [title](rel_el)
- view [department](rel_el)
- view [employee](rel_el)

## lookup:el
- employee
- department

## lookup:rel_el
- employee
- title
- department
- salary

## lookup:word
- Georgi
- Bezalel
- Simmel
- Senior Engineer
- Staff
- Assistant Engineer
- Development
- Finance
- Research

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