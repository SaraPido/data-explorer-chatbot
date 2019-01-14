## intent:find_el_by_word
- find [teacher](el) [Daniel](word)
- find [class](el) [1^B](word)
- find [class](el) [2^A](word)
- find [class](el) [1^C](word)
- find [lesson](el) [Maths](word)
- find [teacher](el) [Nicola](word)
- find [teacher](el) [Nicola](word)
- find [teacher](el) [Nicola](word)
- find [teacher](el) [Nicola](word)

## intent:find_el_by_rel_word
- find [class](el) with [lesson](rel_el) [Maths](word)
- find [lesson](el) with [teacher](rel_el) [Nicola](word)
- find [lesson](el) with [teacher](rel_el) [Nicola](word)
- find [teacher](el) with [lesson](rel_el) [Geography](word)
- find [lesson](el) with [class](rel_el) [1^B](word)
- find [lesson](el) with [class](rel_el) [2^B](word)
- find [lesson](el) with [class](rel_el) [1^B](word)

## intent:view_rel_el
- view [teacher](rel_el)
- view [lesson](rel_el)
- view [class](rel_el)
- view [timetable](rel_el)

## lookup:el
- teacher
- lesson
- class

## lookup:rel_el
- teacher
- lesson
- class
- timetables

## lookup:word
- Nicola
- Maristella
- Vittorio
- Albert
- Florian
- Maths
- Computer Science
- Geography
- History
- 1^A
- 2^B
- 2^C


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