default:
	electroshot file:///Users/markov/Documents/CV/cv.html 2048x --format pdf --filename "cv.pdf" --pdf-page-size A4

export: default
	cp -f cv.pdf MarkovCV.pdf
