OUTPUT=../static-website

all:
	rsync -rt --copy-links --delete-delay --exclude='*.jinja' --exclude=Makefile --exclude='.*' --exclude='_*' . $(OUTPUT)
	# https://github.com/castedo/jinjagen
	jinjagen -m jinjagenadd $(OUTPUT)

clean:
	rm -rf $(OUTPUT)

