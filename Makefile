current_dir := $(shell pwd)
timestamp := $(shell date +%Y_%b)

default: cv resume resume_ml

cv:
	./node_modules/.bin/electron-pdf -m 0 $(current_dir)/cv.html $(current_dir)/cv.pdf

resume:
	./node_modules/.bin/electron-pdf -m 0 $(current_dir)/resume.html $(current_dir)/resume.pdf

resume_ml:
	./node_modules/.bin/electron-pdf -m 0 $(current_dir)/resume_ml.html $(current_dir)/resume_ml.pdf

export: default
	cp -f cv.pdf Markov_CV_$(timestamp).pdf
	cp -f resume.pdf Markov_resume_$(timestamp).pdf
	cp -f resume_ml.pdf Markov_resume_ml_$(timestamp).pdf
