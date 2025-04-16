current_dir := $(shell pwd)
timestamp := $(shell date +%Y_%b)

default: cv resume

cv:
	./node_modules/.bin/electron-pdf -m 0 $(current_dir)/cv.html $(current_dir)/cv.pdf

resume:
	./node_modules/.bin/electron-pdf -m 0 $(current_dir)/resume.html $(current_dir)/resume.pdf

export: default
	cp -f cv.pdf Markov_CV_$(timestamp).pdf
	cp -f resume.pdf Markov_resume_$(timestamp).pdf
