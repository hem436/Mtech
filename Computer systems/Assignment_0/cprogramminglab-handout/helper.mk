# Set course/lab variables
LAB = cprogramminglab

# Check handin parameters
ifdef HANDIN_TAR
  HANDIN_FILE = $(HANDIN_TAR)
else
  ifneq ($(words $(HANDIN_FILES)),1)
    $(error HANDIN_TAR not set, and HANDIN_FILES has more than one file)
  endif
  HANDIN_FILE = $(HANDIN_FILES)
endif

#####################################################################
# Rules to create and verify handin files
#####################################################################

ifdef HANDIN_TAR

$(HANDIN_TAR): $(HANDIN_FILES)
	tar cvf $@ $^

.PHONY: handin
handin: $(HANDIN_TAR)

else

.PHONY: handin
handin:
	@echo "There is no handin tar. Submit \"$(HANDIN_FILE)' directly."

endif

