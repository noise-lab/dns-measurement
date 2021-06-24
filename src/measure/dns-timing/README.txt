The modified code in the branch "resolver-research" is used to parse through a list of resolvers and upload the data collected from them to a csv file.

The file "resolver_timings.py" requires four arguments that can be found and altered in the .py file.
	- "./dns-timing" is the dns-timing function. This has not been altered. 
	- "doh" 
	- The recursors file. Two currently exist. "recursors" consists of the entire list of resolvers, while "recursors-few" consists of a shortened list. This second file is only used for testing if the tool is working. 
	- "domains" is a list of domains that the resolvers will be tested with. 

The command to run the "resolver_timings.py" tool is "python3 resolver_timings.py". The results will be exported to a csv. It is currently titled "test3.csv".

The amount of times that the measurements for the resolvers run can be changed by altering the number inside the "in range" section of the for loop in "resolver_timings.py". 
