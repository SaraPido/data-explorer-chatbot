## intent:find_el_by_attr
- find [customer](el) [Mark](word)
- find [customer](el) [with contact](attr) [Peter Parker](word)
- find [customer](el) [with contact](attr) [Mark](word)
- find [customer](el) that [paid](attr) [<](num_op) [1223](num)€
- find [customer](el) that [reported to](attr) [James Brown](word)
- find [customer](el) that [ordered](attr) [Motorcycle](word)
- find [customer](el) that [ordered](attr) [Something Cool](word)
- find [customer](el) [located in](attr) [London](word)
- find [employee](el) that [work in](attr) [Italy](word) 
- find [employee](el) [John](word)
- find [employee](el) that [work in](attr) [Milan](word)
- find [employee](el) [Philip](word)
- find [employee](el) that [work in](attr) [Paris](word)

## intent:filter_el_by_attr
- filter [customer](el) [Mark](word)
- filter [with contact](attr) [Peter Parker](word)
- filter [customer](el) [with contact](attr) [Mark](word)
- filter the ones that [paid](attr) [<](num_op) [1223](num)€
- filter [customer](el) that [reported to](attr) [James Brown](word)
- filter the ones [ordered](attr) [Motorcycle](word)
- filter [customer](el) that [ordered](attr) [Something Cool](word)
- filter [located in](attr) [London](word)
- filter [employee](el) that [work in](attr) [Italy](word) 
- filter [John](word)
- filter [employee](el) that [work in](attr) [Milan](word)
- filter [employee](el) [Philip](word)
- filter [employee](el) that [work in](attr) [Paris](word)

## intent:cross_rel
- [works in office](rel)
- [related sales representative](rel)
- [orders made](rel)

## lookup:el
- customer
- employee
- office
- product
- product line
- payment
- order

## lookup:rel
- something

## lookup:word
- Nicola
- Giorgio
- Vittorio
- Albert
- 1923 Moto Guzzi
- Car Models
- Florian
- Car
- Ferrari
- Moto Guzzi
- Mario

## intent:show_rel
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