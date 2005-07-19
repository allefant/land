EXAMPLES = image draw font isometric imperium widget

EXAMPLES-CLEAN = $(patsubst %,%-clean, $(EXAMPLES))
EXAMPLES-SHINY = $(patsubst %,%-shiny, $(EXAMPLES))

NO_TARGETS = 1

include ../../makefile.template

examples: $(EXAMPLES)
examples-clean: $(EXAMPLES-CLEAN)
examples-shiny: $(EXAMPLES-SHINY)

$(EXAMPLES): %:
	$(MAK) -C $*

$(EXAMPLES-CLEAN): %-clean:
	$(MAK) -C $* clean

$(EXAMPLES-SHINY): %-shiny:
	$(MAK) -C $* shiny

.PHONY: $(EXAMPLES) $(EXAMPLES-CLEAN) $(EXAMPLES-SHNIY)

