# First run all the experiments
# then plot the data using R

##### Generate data for all experiments on datasets #####
	python3 econf.py
	python3 gsci.py
	python3 ibmhr.py
	python3 wh.py


##### Generate data for all experiments on partially synthetic data  #####
	python3 synthetic_study.py

##### Make all plots #####
	Rscript plotting.R