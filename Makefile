PDF2HTML=/usr/local/bin/pdftohtml -noframes
HTML2TXT=lynx -dump

SILENT=> /dev/null

%.html: %.pdf
	$(PDF2HTML) $< $(SILENT)

%.txt: %.html
	$(HTML2TXT) $< > $@
