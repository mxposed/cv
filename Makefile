current_dir := $(shell pwd)

default:
	./node_modules/.bin/electron-pdf -m 0 $(current_dir)/cv.html $(current_dir)/cv.pdf
	./node_modules/.bin/electron-pdf -m 0 $(current_dir)/resume.html $(current_dir)/resume.pdf

export: default
	cp -f cv.pdf MarkovCV.pdf
